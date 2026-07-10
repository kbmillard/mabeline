"""Iran oil origin-pressure tests."""

from __future__ import annotations

from catalog.graph.iran_oil import classify_join, parse_eia_iran, parse_imdb_iran
from catalog.graph.schema_v1 import EDGE_TYPES, NODE_TYPES


def test_schema_has_origin_pressure():
    assert "origin_pressure" in EDGE_TYPES
    assert "country" in NODE_TYPES


def test_classify_join_diverge_for_202606():
    assert classify_join({"202310", "202309"}, "202606") == "no_iran_eia_in_window"
    assert classify_join({"202606"}, "202606") == "aligned"
    assert classify_join({"202601"}, "202606") == "diverge"


def test_parse_eia_iran_has_2023_months():
    eia = parse_eia_iran()
    months = {r["period"] for r in eia["monthly"]}
    assert "202310" in months
    assert eia["monthly"][-1]["period"] == "202310"


def test_parse_imdb_iran_may_2026():
    imdb = parse_imdb_iran()
    assert imdb["country"] is not None
    assert imdb["country"]["cty_code"] == "5070"
    assert imdb["country"]["month"] == "202605"
    assert imdb["country"]["con_val_mo"] == 3873
