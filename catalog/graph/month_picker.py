"""Pick last complete snapshot month from temporal_edge_events."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

import duckdb


def pick_snapshot_month(
    events_parquet: Path | str,
    *,
    min_haul_weight: float = 5000.0,
    min_sctg2_count: int = 8,
    con: duckdb.DuckDBPyConnection | None = None,
) -> str:
    """
    Return the latest month where national observed_haul weight and commodity
    coverage exceed thresholds. Falls back if the max month is thin.
    """
    path = str(events_parquet)
    own = con is None
    if own:
        con = duckdb.connect()

    rows = con.execute(
        """
        SELECT
          event_time AS event_month,
          SUM(weight) AS w,
          COUNT(DISTINCT json_extract_string(attrs_json, '$.sctg2')) AS n_sctg
        FROM read_parquet(?)
        WHERE edge_type = 'observed_haul' AND event_grain = 'month'
        GROUP BY 1
        ORDER BY event_month DESC
        """,
        [path],
    ).fetchall()

    if own:
        con.close()

    if not rows:
        raise ValueError(f"No observed_haul months in {events_parquet}")

    now = datetime.now()
    current_ym = f"{now.year}{now.month:02d}"

    for month, weight, n_sctg in rows:
        month_s = str(month)
        if month_s >= current_ym:
            continue
        if float(weight or 0) >= min_haul_weight and int(n_sctg or 0) >= min_sctg2_count:
            return month_s

    for month, weight, n_sctg in rows:
        month_s = str(month)
        if month_s >= current_ym:
            continue
        if float(weight or 0) >= min_haul_weight:
            return month_s

    return str(rows[0][0])
