"""FMC maritime + STB R1 THG source smoke tests."""

from __future__ import annotations

from pathlib import Path

import duckdb

from catalog.graph.schema_v1 import EDGE_TYPES, NODE_TYPES
from catalog.graph.thg_sources import (
    _parse_r1_metrics,
    append_fmc_maritime_events,
    append_stb_r1_events,
)

ROOT = Path(__file__).resolve().parents[1]


def _empty_events(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE all_events (
          event_id VARCHAR, edge_type VARCHAR, src_type VARCHAR, src_id VARCHAR,
          dst_type VARCHAR, dst_id VARCHAR, event_time VARCHAR, event_grain VARCHAR,
          weight DOUBLE, confidence VARCHAR, inference_method VARCHAR, source_family VARCHAR,
          source_path VARCHAR, source_mtime BIGINT, attrs_json VARCHAR
        )
        """
    )


def test_schema_includes_maritime():
    assert "maritime_license" in EDGE_TYPES
    assert "maritime_org" in NODE_TYPES


def test_fmc_maritime_append_when_files_present():
    oti = ROOT / "_unwrapped" / "fmc_maritime" / "oti_licensed_active.csv"
    if not oti.exists():
        return
    con = duckdb.connect()
    _empty_events(con)
    files: list[str] = []
    warns: list[str] = []
    n = append_fmc_maritime_events(con, input_files=files, warnings=warns)
    assert n > 0
    assert con.execute(
        "SELECT COUNT(*) FROM all_events WHERE edge_type='maritime_license'"
    ).fetchone()[0] == n
    assert any("fmc_maritime" in f for f in files)


def test_r1_bnsf_miles_not_line_number():
    path = ROOT / "_unwrapped" / "stb_rail" / "R1-BNSF-2025.xlsx"
    if not path.exists():
        return
    m = _parse_r1_metrics(path)
    assert m.get("miles_of_road", 0) > 1000
    assert m.get("train_miles", 0) > 1_000_000


def test_stb_r1_append_when_files_present():
    path = ROOT / "_unwrapped" / "stb_rail" / "R1-BNSF-2025.xlsx"
    if not path.exists():
        return
    con = duckdb.connect()
    _empty_events(con)
    files: list[str] = []
    warns: list[str] = []
    n = append_stb_r1_events(con, input_files=files, warnings=warns)
    assert n > 0
    rows = con.execute(
        """
        SELECT src_id, dst_id, weight FROM all_events
        WHERE inference_method='stb_r1_2025' AND src_id='BNSF' AND dst_id='miles_of_road'
        """
    ).fetchall()
    assert rows and rows[0][2] > 1000
    assert any("2025" in f or "R1" in f for f in files)
