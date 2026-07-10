"""Minimal heterogeneous graph encoder (smoke train)."""

from __future__ import annotations

import hashlib
import math
from typing import Any

import duckdb

from catalog.graph.schema_v1 import OUTPUTS

EMBED_DIM = 32


def _hash_embed(node_id: str, dim: int = EMBED_DIM) -> list[float]:
    h = hashlib.sha256(node_id.encode()).digest()
    out = []
    for i in range(dim):
        b = h[i % len(h)]
        out.append(math.sin((b + 1) * (i + 1) * 0.13))
    return out


def load_edge_subsample(
    *,
    snapshot_month: str | None = None,
    limit: int = 50_000,
) -> tuple[list[dict[str, Any]], str]:
    events_path = OUTPUTS["events"]
    if not events_path.exists():
        raise FileNotFoundError(f"Run thg-build first: {events_path}")

    con = duckdb.connect()
    if not snapshot_month:
        from catalog.graph.month_picker import pick_snapshot_month

        snapshot_month = pick_snapshot_month(events_path, con=con, min_sctg2_count=1)

    rows = con.execute(
        """
        SELECT edge_type, src_type, src_id, dst_type, dst_id, event_time,
          weight, confidence, event_grain
        FROM read_parquet(?)
        WHERE event_grain = 'month' AND event_time = ?
        ORDER BY weight DESC
        LIMIT ?
        """,
        [str(events_path), snapshot_month, limit],
    ).fetchall()

    edges = [
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
    return edges, snapshot_month


def train_smoke_embeddings(
    edges: list[dict[str, Any]],
    *,
    epochs: int = 20,
    embed_dim: int = EMBED_DIM,
) -> dict[tuple[str, str], list[float]]:
    """Message-passing-lite: aggregate neighbor means then blend with hash prior."""
    nodes: set[tuple[str, str]] = set()
    for e in edges:
        nodes.add((e["src_type"], e["src_id"]))
        nodes.add((e["dst_type"], e["dst_id"]))

    emb = {(nt, nid): _hash_embed(f"{nt}:{nid}", embed_dim) for nt, nid in nodes}

    try:
        import torch
        import torch.nn.functional as F

        idx = {k: i for i, k in enumerate(nodes)}
        n = len(nodes)
        adj = torch.zeros(n, n)
        for e in edges:
            si = idx[(e["src_type"], e["src_id"])]
            di = idx[(e["dst_type"], e["dst_id"])]
            w = min(1.0, e["weight"] / 1000.0)
            adj[si, di] += w
            adj[di, si] += w
        adj = adj + torch.eye(n)
        deg = adj.sum(dim=1, keepdim=True).clamp(min=1.0)
        norm_adj = adj / deg

        x = torch.tensor([emb[k] for k in idx], dtype=torch.float32)
        for _ in range(epochs):
            x = F.relu(norm_adj @ x)
            x = F.normalize(x, dim=1)
        for i, k in enumerate(idx):
            emb[k] = x[i].tolist()
    except ImportError:
        pass

    return emb
