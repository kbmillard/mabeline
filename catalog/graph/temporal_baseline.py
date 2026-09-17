"""SQL month-over-month change scores on temporal_edge_events."""

from __future__ import annotations

from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT
from catalog.freight_movement import SCTG2_LABELS, get_faf_csv
from catalog.graph.month_picker import pick_snapshot_month
from catalog.graph.schema_v1 import OUTPUTS
from catalog.signals._common import CSV_OPTS, CommandTimer, fingerprint_paths, write_receipt

RECEIPT_PATH = BUILD_REPORTS / "thg_baseline_receipt_v1.json"
VERSION = "thg_baseline_v1"


def _score_sql(*, partition_cols: str, id_suffix: str, include_state: bool) -> str:
    state_select = "o.state," if include_state else ""
    state_id = " || COALESCE(o.state, '')" if include_state else ""
    state_filter = " AND state IS NOT NULL AND state != '' AND state != 'UNK'" if include_state else ""
    monthly_group = "1, 2, 3" if include_state else "1, 2"
    monthly_select = "event_month, sctg2, state" if include_state else "event_month, sctg2"
    null_state = "" if include_state else ", NULL AS state"
    return f"""
          WITH hauls AS (
            SELECT
              event_time AS event_month,
              json_extract_string(attrs_json, '$.sctg2') AS sctg2,
              json_extract_string(attrs_json, '$.state') AS state,
              SUM(weight) AS w
            FROM read_parquet('{{events_s}}')
            WHERE edge_type = 'observed_haul' AND event_grain = 'month'
            GROUP BY 1, 2, 3
          ),
          monthly AS (
            SELECT {monthly_select}, SUM(w) AS truck_weight
            FROM hauls
            WHERE sctg2 IS NOT NULL AND sctg2 != ''{state_filter}
            GROUP BY {monthly_group}
          ),
          ordered AS (
            SELECT *, LAG(truck_weight) OVER (PARTITION BY {partition_cols} ORDER BY event_month) AS prior_weight
            FROM monthly
          ),
          faf AS (
            SELECT sctg2, SUM(TRY_CAST(tons_2024 AS DOUBLE)) kt
            FROM read_csv_auto('{{faf_s}}', {CSV_OPTS})
            WHERE sctg2 IS NOT NULL
            GROUP BY 1
          ),
          faf_tot AS (SELECT SUM(kt) t FROM faf),
          faf_pct AS (
            SELECT sctg2, ROUND(100.0 * kt / t, 4) AS faf5_pct_of_national
            FROM faf, faf_tot
          )
          SELECT
            md5(o.sctg2 || '|' || o.event_month || '{id_suffix}'{state_id}) AS change_id,
            o.sctg2,
            o.event_month AS snapshot_month,
            {state_select if include_state else 'NULL AS state,'}
            o.truck_weight,
            o.prior_weight,
            ROUND(CASE WHEN o.prior_weight IS NULL OR o.prior_weight = 0 THEN 0
              ELSE 100.0 * (o.truck_weight - o.prior_weight) / o.prior_weight END, 3) AS truck_observation_delta_pct,
            ROUND(o.truck_weight - COALESCE(o.prior_weight, 0), 2) AS truck_observation_delta_abs,
            COALESCE(f.faf5_pct_of_national, 0) AS faf5_pct_of_national,
            ROUND(CASE WHEN f.faf5_pct_of_national IS NULL OR f.faf5_pct_of_national = 0 THEN 0
              ELSE o.truck_weight / f.faf5_pct_of_national END, 4) AS truck_vs_faf_residual,
            ROUND(LEAST(100, GREATEST(0,
              0.5 * COALESCE(CASE WHEN o.prior_weight > 0 THEN 100.0 * (o.truck_weight - o.prior_weight) / o.prior_weight ELSE 0 END, 0)
              + 0.3 * COALESCE(f.faf5_pct_of_national, 0)
              + 0.2 * LEAST(50, o.truck_weight / 1000.0)
            )), 3) AS change_score,
            'sql_baseline_v1' AS method
          FROM ordered o
          LEFT JOIN faf_pct f ON o.sctg2 = f.sctg2
          WHERE o.event_month IS NOT NULL
    """


def run_temporal_baseline() -> dict[str, Any]:
    timer = CommandTimer()
    events_path = OUTPUTS["events"]
    if not events_path.exists():
        raise FileNotFoundError(f"Run thg-build first: {events_path}")

    snapshot_month = pick_snapshot_month(events_path)
    out_path = OUTPUTS["change_scores"]
    corridor_path = OUTPUTS["change_scores_corridor"]
    faf = get_faf_csv()
    con = duckdb.connect()

    events_s = str(events_path)
    faf_s = str(faf)
    out_s = str(out_path)
    corridor_s = str(corridor_path)

    national_sql = _score_sql(partition_cols="sctg2", id_suffix="|nat|", include_state=False)
    corridor_sql = _score_sql(partition_cols="sctg2, state", id_suffix="|cor|", include_state=True)

    con.execute(
        f"""
        COPY (
          {national_sql.format(events_s=events_s, faf_s=faf_s)}
        ) TO '{out_s}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    con.execute(
        f"""
        COPY (
          {corridor_sql.format(events_s=events_s, faf_s=faf_s)}
        ) TO '{corridor_s}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    row_count = con.execute("SELECT COUNT(*)::BIGINT FROM read_parquet(?)", [str(out_path)]).fetchone()[0]
    corridor_count = con.execute(
        "SELECT COUNT(*)::BIGINT FROM read_parquet(?)", [str(corridor_path)]
    ).fetchone()[0]
    latest = con.execute(
        """
        SELECT sctg2, snapshot_month, change_score, truck_observation_delta_pct
        FROM read_parquet(?)
        WHERE snapshot_month = ?
        ORDER BY change_score DESC
        LIMIT 10
        """,
        [str(out_path), snapshot_month],
    ).fetchall()
    top = [
        {
            "sctg2": r[0],
            "sctg2_name": SCTG2_LABELS.get(str(r[0]).zfill(2)[:2], r[0]),
            "snapshot_month": r[1],
            "change_score": float(r[2]),
            "truck_observation_delta_pct": float(r[3] or 0),
        }
        for r in latest
    ]

    receipt = write_receipt(
        RECEIPT_PATH,
        command="thg-baseline",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(events_path.relative_to(ROOT)), str(faf.relative_to(ROOT))],
        input_fingerprints=fingerprint_paths([events_path, faf]),
        output_files=[
            str(out_path.relative_to(ROOT)),
            str(corridor_path.relative_to(ROOT)),
        ],
        row_counts={"change_scores": int(row_count), "corridor_change_scores": int(corridor_count)},
        warnings=[],
        missing_data_flags=[],
        success=True,
        extra={
            "scan_type": VERSION,
            "snapshot_month": snapshot_month,
            "top_change_scores": top,
            "elapsed_sec": timer.elapsed_sec,
        },
    )
    return receipt
