"""HT-GNN smoke tests."""

from __future__ import annotations

from catalog.graph.schema_v1 import OUTPUTS
from catalog.htgnn.encoder import load_edge_subsample, train_smoke_embeddings
from catalog.htgnn.train import run_htgnn_train


def test_htgnn_train_produces_embeddings():
    if not OUTPUTS["events"].exists():
        return
    receipt = run_htgnn_train(epochs=1, limit=1000)
    assert receipt["row_counts"]["nodes"] > 0
    assert OUTPUTS["node_embeddings"].exists()


def test_encoder_smoke():
    if not OUTPUTS["events"].exists():
        return
    edges, _ = load_edge_subsample(limit=500)
    emb = train_smoke_embeddings(edges, epochs=1)
    assert len(emb) > 0
    assert len(next(iter(emb.values()))) > 0
