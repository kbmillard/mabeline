"""Heterogeneous graph encoder (scaled subsample train)."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from typing import Any

import duckdb

from catalog.graph.schema_v1 import OUTPUTS

EMBED_DIM = 32

# Keep transport signal types represented even when carrier_risk dominates.
_STRATIFY_TYPES = (
    "observed_haul",
    "hauls_commodity",
    "operates_in",
    "origin_pressure",
    "maritime_license",
    "rail_metric",
    "commodity_pressure",
    "trade_import",
    "modeled_flow",
)


def _hash_embed(node_id: str, dim: int = EMBED_DIM) -> list[float]:
    h = hashlib.sha256(node_id.encode()).digest()
    out = []
    for i in range(dim):
        b = h[i % len(h)]
        out.append(math.sin((b + 1) * (i + 1) * 0.13))
    return out


def _rows_to_edges(rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [
        {
            "edge_type": r[0],
            "src_type": r[1],
            "src_id": r[2],
            "dst_type": r[3],
            "dst_id": r[4],
            "event_time": r[5],
            "weight": float(r[6] or 0),
            "confidence": r[7],
            "event_grain": r[8],
        }
        for r in rows
    ]


def load_edge_subsample(
    *,
    snapshot_month: str | None = None,
    limit: int = 250_000,
) -> tuple[list[dict[str, Any]], str]:
    events_path = OUTPUTS["events"]
    if not events_path.exists():
        raise FileNotFoundError(f"Run thg-build first: {events_path}")

    con = duckdb.connect()
    if not snapshot_month:
        from catalog.graph.month_picker import pick_snapshot_month

        snapshot_month = pick_snapshot_month(events_path, con=con, min_sctg2_count=1)

    path = str(events_path)
    seen: set[tuple[Any, ...]] = set()
    collected: list[tuple[Any, ...]] = []

    def _add(rows: list[tuple[Any, ...]]) -> None:
        for r in rows:
            key = (r[0], r[1], r[2], r[3], r[4], r[5])
            if key in seen:
                continue
            seen.add(key)
            collected.append(r)
            if len(collected) >= limit:
                return

    # 1) Snapshot month (YYYYMM haul / operates_in spine)
    _add(
        con.execute(
            """
            SELECT edge_type, src_type, src_id, dst_type, dst_id, event_time,
              weight, confidence, event_grain
            FROM read_parquet(?)
            WHERE event_grain = 'month' AND event_time = ?
            ORDER BY weight DESC
            LIMIT ?
            """,
            [path, snapshot_month, limit],
        ).fetchall()
    )

    # 2) Stratified fill: priority edge types (year + other months)
    if len(collected) < limit:
        per_type = max(500, (limit - len(collected)) // max(1, len(_STRATIFY_TYPES)))
        for et in _STRATIFY_TYPES:
            if len(collected) >= limit:
                break
            _add(
                con.execute(
                    """
                    SELECT edge_type, src_type, src_id, dst_type, dst_id, event_time,
                      weight, confidence, event_grain
                    FROM read_parquet(?)
                    WHERE edge_type = ?
                      AND NOT (event_grain = 'month' AND event_time = ?)
                    ORDER BY weight DESC
                    LIMIT ?
                    """,
                    [path, et, snapshot_month, per_type],
                ).fetchall()
            )

    # 3) Remaining quota: heaviest remaining month-grain edges (any YYYYMM)
    if len(collected) < limit:
        need = limit - len(collected)
        _add(
            con.execute(
                """
                SELECT edge_type, src_type, src_id, dst_type, dst_id, event_time,
                  weight, confidence, event_grain
                FROM read_parquet(?)
                WHERE event_grain = 'month'
                  AND length(event_time) = 6
                  AND event_time != ?
                ORDER BY weight DESC
                LIMIT ?
                """,
                [path, snapshot_month, need],
            ).fetchall()
        )

    # 4) Last resort: carrier_risk / other (hash-stable sample via weight order)
    if len(collected) < limit:
        need = limit - len(collected)
        _add(
            con.execute(
                """
                SELECT edge_type, src_type, src_id, dst_type, dst_id, event_time,
                  weight, confidence, event_grain
                FROM read_parquet(?)
                WHERE edge_type = 'carrier_risk'
                ORDER BY weight DESC
                LIMIT ?
                """,
                [path, need],
            ).fetchall()
        )

    return _rows_to_edges(collected[:limit]), snapshot_month


def train_smoke_embeddings(
    edges: list[dict[str, Any]],
    *,
    epochs: int = 20,
    embed_dim: int = EMBED_DIM,
) -> dict[tuple[str, str], list[float]]:
    """Sparse message-passing: neighbor mean blend with hash prior (scales past dense adj)."""
    nodes: set[tuple[str, str]] = set()
    neigh: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for e in edges:
        s = (e["src_type"], e["src_id"])
        d = (e["dst_type"], e["dst_id"])
        nodes.add(s)
        nodes.add(d)
        neigh[s].append(d)
        neigh[d].append(s)

    emb = {(nt, nid): _hash_embed(f"{nt}:{nid}", embed_dim) for nt, nid in nodes}

    try:
        import torch

        idx = {k: i for i, k in enumerate(nodes)}
        n = len(nodes)
        x = torch.tensor([emb[k] for k in idx], dtype=torch.float32)

        # Build sparse adjacency once (COO → sparse mm each epoch).
        src_i: list[int] = []
        dst_i: list[int] = []
        for e in edges:
            si = idx[(e["src_type"], e["src_id"])]
            di = idx[(e["dst_type"], e["dst_id"])]
            src_i.extend([si, di])
            dst_i.extend([di, si])
        # Self-loops
        src_i.extend(range(n))
        dst_i.extend(range(n))

        indices = torch.tensor([src_i, dst_i], dtype=torch.long)
        values = torch.ones(len(src_i), dtype=torch.float32)
        adj = torch.sparse_coo_tensor(indices, values, (n, n)).coalesce()
        deg = torch.sparse.sum(adj, dim=1).to_dense().clamp(min=1.0).unsqueeze(1)

        for _ in range(epochs):
            x = torch.sparse.mm(adj, x) / deg
            x = torch.relu(x)
            x = torch.nn.functional.normalize(x, dim=1)
        for i, k in enumerate(idx):
            emb[k] = x[i].tolist()
    except ImportError:
        for _ in range(epochs):
            nxt: dict[tuple[str, str], list[float]] = {}
            for node in nodes:
                vecs = [emb[node]] + [emb[nb] for nb in neigh[node][:64]]
                dim = len(vecs[0])
                mean = [sum(v[i] for v in vecs) / len(vecs) for i in range(dim)]
                norm = math.sqrt(sum(v * v for v in mean)) or 1.0
                nxt[node] = [v / norm for v in mean]
            emb = nxt

    return emb
