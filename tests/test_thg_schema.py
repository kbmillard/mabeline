"""THG schema tests."""

from __future__ import annotations

from catalog.graph.month_picker import pick_snapshot_month
from catalog.graph.schema_v1 import EDGE_TYPES, EVENT_COLUMNS, OUTPUTS


def test_schema_edge_types_include_wired_sources():
    assert "operates_in" in EDGE_TYPES
    assert "identity_match" in EDGE_TYPES
    assert "commodity_pressure" in EDGE_TYPES
    assert "event_id" in EVENT_COLUMNS
    assert "events" in OUTPUTS


def test_month_picker_skips_current_partial_month():
    if not OUTPUTS["events"].exists():
        return
    month = pick_snapshot_month(OUTPUTS["events"])
    assert month < "202607"
