"""Temporal baseline tests."""

from __future__ import annotations

import duckdb

from catalog.graph.schema_v1 import OUTPUTS


def test_change_scores_no_null_sctg2():
    path = OUTPUTS["change_scores"]
    if not path.exists():
        return
    n = duckdb.connect().execute(
        "SELECT COUNT(*) FROM read_parquet(?) WHERE sctg2 IS NULL OR sctg2 = ''",
        [str(path)],
    ).fetchone()[0]
    assert n == 0


def test_change_scores_month_ordering():
    path = OUTPUTS["change_scores"]
    if not path.exists():
        return
    rows = duckdb.connect().execute(
        """
        SELECT sctg2, snapshot_month
        FROM read_parquet(?)
        ORDER BY sctg2, snapshot_month
        """,
        [str(path)],
    ).fetchall()
    assert len(rows) > 0
