"""HT-GNN smoke train + score CLI backends."""

from __future__ import annotations

from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT
from catalog.graph.schema_v1 import OUTPUTS
from catalog.htgnn.encoder import load_edge_subsample, train_smoke_embeddings
from catalog.signals._common import export_parquet
from catalog.signals._common import CommandTimer, write_receipt

RECEIPT_PATH = BUILD_REPORTS / "htgnn_train_receipt_v1.json"
VERSION = "htgnn_train_v1"


def run_htgnn_train(*, epochs: int = 20, snapshot_month: str | None = None, limit: int = 50_000) -> dict[str, Any]:
    timer = CommandTimer()
    edges, month = load_edge_subsample(snapshot_month=snapshot_month, limit=limit)
    emb = train_smoke_embeddings(edges, epochs=epochs)

    out_path = OUTPUTS["node_embeddings"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "node_type": nt,
            "node_id": nid,
            "snapshot_month": month,
            "embedding": vec,
            "embedding_dim": len(vec),
        }
        for (nt, nid), vec in emb.items()
    ]

    export_parquet(rows, out_path)

    receipt = write_receipt(
        RECEIPT_PATH,
        command="htgnn-train",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(OUTPUTS["events"].relative_to(ROOT))],
        input_fingerprints={},
        output_files=[str(out_path.relative_to(ROOT))],
        row_counts={"nodes": len(rows), "edges_subsample": len(edges)},
        warnings=[],
        missing_data_flags=[],
        success=True,
        extra={
            "scan_type": VERSION,
            "snapshot_month": month,
            "epochs": epochs,
            "elapsed_sec": timer.elapsed_sec,
        },
    )
    return receipt


def run_htgnn_score() -> dict[str, Any]:
    """Inference-only: verify embeddings parquet exists."""
    out_path = OUTPUTS["node_embeddings"]
    if not out_path.exists():
        return run_htgnn_train(epochs=5)

    con = duckdb.connect()
    n = con.execute("SELECT COUNT(*)::BIGINT FROM read_parquet(?)", [str(out_path)]).fetchone()[0]
    return {
        "command": "htgnn-score",
        "nodes": int(n),
        "path": str(out_path.relative_to(ROOT)),
    }
