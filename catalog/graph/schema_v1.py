"""THG schema v1 — node types, edge types, event record shape.

Contract lives here. Events live in warehouse/th_graph_v1/.
"""

from __future__ import annotations

from catalog.config import ROOT

THG_ROOT = ROOT / "warehouse" / "th_graph_v1"

NODE_TYPES = (
    "carrier",
    "shipper",
    "commodity",
    "corridor",
    "rail_operator",
    "national",
    "state",
    "country",
    "maritime_org",
    "lei",
    "ticker",
)

EDGE_TYPES = (
    "observed_haul",
    "hauls_commodity",
    "operates_in",
    "modeled_flow",
    "shipment_share",
    "rail_metric",
    "commodity_pressure",
    "origin_pressure",
    "trade_import",
    "carrier_risk",
    "pipeline_signal",
    "identity_match",
    "maritime_license",
)

EVENT_COLUMNS = (
    "event_id",
    "edge_type",
    "src_type",
    "src_id",
    "dst_type",
    "dst_id",
    "event_time",
    "event_grain",
    "weight",
    "confidence",
    "inference_method",
    "source_family",
    "source_path",
    "source_mtime",
    "attrs_json",
)

OUTPUTS = {
    "events": THG_ROOT / "temporal_edge_events_v1.parquet",
    "nodes": THG_ROOT / "nodes_v1.parquet",
    "edge_catalog": THG_ROOT / "edges_v1.parquet",
    "change_scores": THG_ROOT / "temporal_change_scores_v1.parquet",
    "change_scores_corridor": THG_ROOT / "temporal_change_scores_corridor_v1.parquet",
    "node_embeddings": THG_ROOT / "node_embeddings_v1.parquet",
}
