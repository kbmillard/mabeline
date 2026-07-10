"""
STB EP724 rail performance staging and transport_economy add-on.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.source_truth import require_path, resolved_sources_dict
from catalog.util import append_log, write_json

RECEIPT_PATH = BUILD_REPORTS / "stb_ep724_staging_receipt_v1.json"
CSV_OPTS = "header=true, ignore_errors=true, sample_size=-1"


def _ep724_paths() -> dict[str, Path]:
    return {
        "public_data": require_path("stb_ep724_public"),
        "terminal_dwell": require_path("stb_ep724_dwell"),
        "element_10": require_path("stb_ep724_element10"),
    }


def inspect_ep724() -> dict[str, Any]:
    paths = _ep724_paths()
    con = duckdb.connect()
    tables: dict[str, Any] = {}

    for key, path in paths.items():
        row_count = con.execute(
            "SELECT COUNT(*)::BIGINT FROM read_csv_auto(?, header=true, ignore_errors=true)",
            [str(path)],
        ).fetchone()[0]
        cols = con.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true, ignore_errors=true) LIMIT 0",
            [str(path)],
        ).fetchall()
        raw_sample = con.execute(
            "SELECT * FROM read_csv_auto(?, header=true, ignore_errors=true) LIMIT 3",
            [str(path)],
        ).fetchdf()
        sample = json.loads(raw_sample.to_json(orient="records", date_format="iso"))

        tables[key] = {
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "row_count": int(row_count),
            "columns": [c[0] for c in cols],
            "sample_rows": sample,
        }

    public = tables["public_data"]
    join_keys = {
        "railroad_mark": "Class I / railroad identifier",
        "railroad_name": "Human-readable railroad",
        "report_period_start_date": "Period start",
        "report_period_end_date": "Period end",
        "measure_name_analytics": "Performance measure code",
        "fact_value": "Reported metric value",
    }
    recommended_joins = [
        "railroad_mark → FAF5 rail mode context (no direct DOT join)",
        "measure_name_analytics + report_period → time-series rail performance",
        "terminal dwell file → yard/terminal congestion signals",
    ]

    return {
        "scan_type": "stb_ep724_staging_receipt_v1",
        "status": "staged",
        "integration": "addon_not_full_sctg_wire",
        "tables": tables,
        "total_rows": sum(t["row_count"] for t in tables.values()),
        "join_keys": join_keys,
        "recommended_joins": recommended_joins,
        "sctg_note": "EP724 is railroad performance metrics, not commodity-coded tonnage — stage only",
        "source_truth": resolved_sources_dict(),
        "created_at": utc_now(),
    }


def ep724_rail_addon(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    """Low-risk summary for transport_economy receipt."""
    path = str(require_path("stb_ep724_public"))
    by_rr = con.execute(
        f"""
        SELECT
          railroad_mark,
          railroad_name,
          COUNT(*)::BIGINT AS measure_rows,
          COUNT(DISTINCT measure_name_analytics)::BIGINT AS distinct_measures,
          MAX(report_year) AS latest_report_year
        FROM read_csv_auto(?, {CSV_OPTS})
        WHERE railroad_mark IS NOT NULL
        GROUP BY 1, 2
        ORDER BY measure_rows DESC
        LIMIT 15
        """,
        [path],
    ).fetchall()

    dwell_path = str(require_path("stb_ep724_dwell"))
    dwell_top = con.execute(
        f"""
        SELECT railroad_mark, railroad_name,
          ROUND(AVG(TRY_CAST(fact_value AS DOUBLE)), 3) AS avg_dwell
        FROM read_csv_auto(?, {CSV_OPTS})
        WHERE measure_name_analytics ILIKE '%dwell%'
        GROUP BY 1, 2
        ORDER BY avg_dwell DESC NULLS LAST
        LIMIT 10
        """,
        [dwell_path],
    ).fetchall()

    return {
        "layer": "stb_ep724_rail_performance",
        "status": "addon",
        "class_i_summary": [
            {
                "railroad_mark": r[0],
                "railroad_name": r[1],
                "measure_rows": int(r[2]),
                "distinct_measures": int(r[3]),
                "latest_report_year": r[4],
            }
            for r in by_rr
        ],
        "terminal_dwell_top": [
            {"railroad_mark": r[0], "railroad_name": r[1], "avg_dwell": r[2]}
            for r in dwell_top
        ],
        "note": "Rail performance overlay — not SCTG commodity proof",
    }


def run_stb_ep724_staging() -> dict[str, Any]:
    t0 = time.monotonic()
    receipt = inspect_ep724()
    receipt["elapsed_sec"] = round(time.monotonic() - t0, 2)
    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} stb_ep724_staging_receipt_v1.json rows={receipt['total_rows']}",
    )
    return receipt
