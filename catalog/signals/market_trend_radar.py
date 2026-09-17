"""
Market trend radar — commodity movement changes that may imply market trend.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, WAREHOUSE
from catalog.freight_movement import SCTG2_LABELS, get_faf_csv
from catalog.graph.schema_v1 import OUTPUTS as THG_OUTPUTS
from catalog.graph.month_picker import pick_snapshot_month
from catalog.moving_commodity import get_cfs_csv
from catalog.signals._common import (
    CSV_OPTS,
    CommandTimer,
    EXPORTS_DIR,
    export_parquet,
    fingerprint_paths,
    stable_id,
    write_receipt,
)
from catalog.graph.schema_v1 import OUTPUTS as THG_OUTPUTS
from catalog.signals.commodity_truck_signal import CSV_PATH as TRUCK_CSV
from catalog.source_truth import require_path

RECEIPT_PATH = BUILD_REPORTS / "market_trend_radar_v1.json"
CHANGE_SCORES_PATH = THG_OUTPUTS["change_scores"]
CSV_PATH = EXPORTS_DIR / "market_trend_radar_v1.csv"
PARQUET_PATH = WAREHOUSE / "market_trend_radar_v1.parquet"
VERSION = "market_trend_radar_v1"


def _faf5_pct(con: duckdb.DuckDBPyConnection) -> dict[str, float]:
    faf = get_faf_csv()
    rows = con.execute(
        f"""
        WITH t AS (
          SELECT sctg2, SUM(TRY_CAST(tons_2024 AS DOUBLE)) kt
          FROM read_csv_auto(?, {CSV_OPTS}) GROUP BY 1
        ), tot AS (SELECT SUM(kt) t FROM t)
        SELECT sctg2, ROUND(100.0*kt/t, 3) FROM t, tot
        """,
        [str(faf)],
    ).fetchall()
    return {str(r[0]).zfill(2)[:2]: float(r[1]) for r in rows}


def _cfs_pct(con: duckdb.DuckDBPyConnection) -> dict[str, float]:
    cfs = get_cfs_csv()
    rows = con.execute(
        f"""
        WITH t AS (
          SELECT SUBSTR(REGEXP_REPLACE(SCTG,'[^0-9]',''),1,2) sctg2,
            SUM(TRY_CAST(SHIPMT_WGHT AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE)) w
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE SCTG IS NOT NULL GROUP BY 1
        ), tot AS (SELECT SUM(w) t FROM t)
        SELECT sctg2, ROUND(100.0*w/t, 3) FROM t, tot WHERE sctg2 IS NOT NULL AND sctg2 != ''
        """,
        [str(cfs)],
    ).fetchall()
    return {str(r[0]).zfill(2)[:2]: float(r[1]) for r in rows if r[0]}


def _corridor_trends(con: duckdb.DuckDBPyConnection, snapshot_month: str) -> list[dict]:
    corridor_path = THG_OUTPUTS["change_scores_corridor"]
    if not corridor_path.exists():
        return []
    rows = con.execute(
        f"""
        SELECT sctg2, state, change_score, truck_observation_delta_pct,
          faf5_pct_of_national, truck_vs_faf_residual
        FROM read_parquet('{corridor_path}')
        WHERE snapshot_month = ? AND change_score > 0
        ORDER BY change_score DESC
        LIMIT 20
        """,
        [snapshot_month],
    ).fetchall()
    out = []
    for r in rows:
        sctg = str(r[0]).zfill(2)[:2]
        state = str(r[1] or "")
        out.append(
            {
                "sctg2": sctg,
                "sctg2_name": SCTG2_LABELS.get(sctg, sctg),
                "commodity_family": f"{_sctg_family(sctg)}_{state}",
                "change_score": float(r[2] or 0),
                "truck_observation_delta_pct": float(r[3] or 0),
                "faf5_pct_of_national": float(r[4] or 0),
                "truck_vs_faf_residual": float(r[5] or 0),
                "shipper_count": 0,
                "carrier_count": 0,
                "state_count": 1,
                "inspection_sum": 0,
                "truck_signal_count": 0,
                "avg_market_signal": float(r[2] or 0),
                "max_recency": min(100.0, abs(float(r[3] or 0))),
            }
        )
    return out


def _graph_trends(con: duckdb.DuckDBPyConnection) -> list[dict] | None:
    scores_path = THG_OUTPUTS["change_scores"]
    events_path = THG_OUTPUTS["events"]
    if not scores_path.exists() or not events_path.exists():
        return None
    snapshot_month = pick_snapshot_month(events_path, con=con)
    rows = con.execute(
        f"""
        WITH top AS (
          SELECT c.sctg2, c.change_score, c.truck_observation_delta_pct,
            c.faf5_pct_of_national, c.truck_vs_faf_residual, c.snapshot_month
          FROM read_parquet('{scores_path}') c
          WHERE c.snapshot_month = ?
          ORDER BY c.change_score DESC
          LIMIT 50
        ),
        hauls AS (
          SELECT json_extract_string(attrs_json, '$.sctg2') AS sctg2,
            COUNT(DISTINCT src_id) AS shippers,
            COUNT(DISTINCT dst_id) AS carriers,
            COUNT(DISTINCT json_extract_string(attrs_json, '$.state')) AS states,
            SUM(weight) AS insp
          FROM read_parquet('{events_path}')
          WHERE edge_type = 'observed_haul' AND event_time = ?
          GROUP BY 1
        )
        SELECT t.sctg2, t.change_score, t.truck_observation_delta_pct,
          t.faf5_pct_of_national, t.truck_vs_faf_residual,
          COALESCE(h.shippers, 0), COALESCE(h.carriers, 0), COALESCE(h.states, 0), COALESCE(h.insp, 0)
        FROM top t
        LEFT JOIN hauls h ON t.sctg2 = h.sctg2
        ORDER BY t.change_score DESC
        """,
        [snapshot_month, snapshot_month],
    ).fetchall()
    if not rows:
        return None
    national = [
        {
            "sctg2": str(r[0]).zfill(2)[:2],
            "sctg2_name": SCTG2_LABELS.get(str(r[0]).zfill(2)[:2], str(r[0])),
            "commodity_family": _sctg_family(str(r[0]).zfill(2)[:2]),
            "change_score": float(r[1] or 0),
            "truck_observation_delta_pct": float(r[2] or 0),
            "faf5_pct_of_national": float(r[3] or 0),
            "truck_vs_faf_residual": float(r[4] or 0),
            "shipper_count": int(r[5]),
            "carrier_count": int(r[6]),
            "state_count": int(r[7]),
            "inspection_sum": int(r[8] or 0),
            "truck_signal_count": int(r[8] or 0),
            "avg_market_signal": float(r[1] or 0),
            "max_recency": min(100.0, abs(float(r[2] or 0))),
        }
        for r in rows
    ]
    if len(national) >= 10:
        return national
    for ct in _corridor_trends(con, snapshot_month):
        national.append(ct)
        if len(national) >= 10:
            break
    return national


def _sctg_family(sctg: str) -> str:
    return {
        "02": "grain_feed",
        "11": "metal_sheet",
        "17": "petroleum_chem",
        "18": "hazmat",
        "19": "coal_coke",
        "31": "general_freight",
        "41": "waste_scrap",
    }.get(sctg, "general_freight")


def _truck_agg(con: duckdb.DuckDBPyConnection) -> list[dict]:
    if not TRUCK_CSV.exists():
        return []
    rows = con.execute(
        f"""
        SELECT sctg2, sctg2_name, commodity_inferred,
          COUNT(*) signals, COUNT(DISTINCT dot_number) carriers,
          COUNT(DISTINCT shipper_name_norm) shippers, COUNT(DISTINCT state) states,
          SUM(inspection_count) insp, AVG(market_signal_score) avg_market,
          MAX(recency_score) max_recency
        FROM read_csv_auto(?, {CSV_OPTS})
        WHERE sctg2 IS NOT NULL AND sctg2 != ''
        GROUP BY 1,2,3 ORDER BY insp DESC
        """,
        [str(TRUCK_CSV)],
    ).fetchall()
    return [
        {
            "sctg2": r[0],
            "sctg2_name": r[1],
            "commodity_family": r[2],
            "truck_signal_count": int(r[3]),
            "carrier_count": int(r[4]),
            "shipper_count": int(r[5]),
            "state_count": int(r[6]),
            "inspection_sum": int(r[7]),
            "avg_market_signal": float(r[8] or 0),
            "max_recency": float(r[9] or 0),
        }
        for r in rows
    ]


def run_market_trend_radar() -> dict[str, Any]:
    timer = CommandTimer()
    warnings: list[str] = []
    missing: list[str] = []
    input_source = "thg_change_scores"

    con = duckdb.connect()
    faf_pct = _faf5_pct(con)
    cfs_pct = _cfs_pct(con)
    truck = _graph_trends(con)
    if truck is None:
        input_source = "commodity_truck_signal_csv"
        if not TRUCK_CSV.exists():
            from catalog.signals.commodity_truck_signal import run_commodity_truck_signal

            run_commodity_truck_signal()
            warnings.append("generated_commodity_truck_signal_first")
        truck = _truck_agg(con)

    # EIA / STB optional scores
    eia_score = 0.0
    stb_score = 0.0
    try:
        pet = require_path("pet_imports")
        eia_score = 50.0 if pet.stat().st_size > 1_000_000 else 0.0
    except FileNotFoundError:
        missing.append("eia_pet_imports")
    try:
        stb = require_path("stb_ep724_public")
        stb_score = 60.0
    except FileNotFoundError:
        missing.append("stb_ep724")

    trends: list[dict[str, Any]] = []
    for row in truck:
        sctg = str(row["sctg2"]).zfill(2)[:2]
        base = 0.6 * faf_pct.get(sctg, 0) + 0.4 * cfs_pct.get(sctg, 0)
        graph_score = row.get("change_score", 0)
        truck_bonus = min(25.0, row["truck_signal_count"] / 50.0)
        recency_bonus = min(15.0, row["max_recency"] / 10.0)
        delta_bonus = min(20.0, abs(row.get("truck_observation_delta_pct", 0)) / 5.0)
        choke_bonus = 5.0 if sctg in ("17", "18", "19") else 0.0
        eia_bonus = eia_score * 0.1 if sctg in ("17", "12") else 0.0
        stb_bonus = stb_score * 0.08 if sctg in ("19", "02") else 0.0
        if input_source == "thg_change_scores":
            movement = round(graph_score + choke_bonus + eia_bonus + stb_bonus, 2)
        else:
            movement = round(base + truck_bonus + recency_bonus + choke_bonus + eia_bonus + stb_bonus, 2)

        direction = (
            "acceleration" if row.get("truck_observation_delta_pct", 0) > 10
            else "deceleration" if row.get("truck_observation_delta_pct", 0) < -10
            else "chokepoint" if sctg in ("17", "18") and eia_score > 0
            else "accumulation" if movement > 15 else "unknown"
        )
        if direction == "unknown" and movement > 30 and row["max_recency"] > 70:
            direction = "acceleration"
        if sctg in ("17", "18") and eia_score > 0:
            direction = "chokepoint"
        conf = "strong" if row["truck_signal_count"] > 100 and base > 5 else "medium" if row["truck_signal_count"] > 20 else "weak"

        trends.append(
            {
                "trend_id": stable_id("trend", sctg, row["commodity_family"]),
                "commodity_family": row["commodity_family"],
                "sctg2": sctg,
                "sctg2_name": row["sctg2_name"] or SCTG2_LABELS.get(sctg, sctg),
                "trend_name": f"{row['sctg2_name']} truck observation cluster",
                "trend_direction": direction,
                "trend_confidence": conf,
                "physical_signal_summary": (
                    f"{row['inspection_sum']:,} inspection-weighted stops across "
                    f"{row['carrier_count']} carriers and {row['shipper_count']} shippers in {row['state_count']} states"
                ),
                "truck_signal_count": row["truck_signal_count"],
                "carrier_count": row["carrier_count"],
                "shipper_count": row["shipper_count"],
                "state_count": row["state_count"],
                "corridor_count": row["state_count"],
                "faf5_pct_of_national": faf_pct.get(sctg, 0),
                "cfs_pct_of_shipments": cfs_pct.get(sctg, 0),
                "eia_signal_score": round(eia_bonus, 2),
                "stb_rail_signal_score": round(stb_bonus, 2),
                "pipeline_signal_score": 0.0,
                "ag_signal_score": 5.0 if sctg == "02" else 0.0,
                "movement_score": movement,
                "recency_score": row["max_recency"],
                "chokepoint_score": choke_bonus,
                "mode_shift_score": 0.0,
                "truck_observation_bonus": truck_bonus,
                "base_movement_score": round(base, 2),
                "commodity_market_signal_score": round(movement * (1.2 if conf == "strong" else 1.0), 2),
                "why_it_matters": (
                    f"Physical truck sensor density for {row['sctg2_name']} may precede financial repricing "
                    f"in energy, logistics, or commodity-exposed equities."
                ),
                "graph_change_score": graph_score,
                "truck_observation_delta_pct": row.get("truck_observation_delta_pct", 0),
                "truck_vs_faf_residual": row.get("truck_vs_faf_residual", 0),
                "evidence_files": [
                    str(THG_OUTPUTS["change_scores"].relative_to(ROOT))
                    if THG_OUTPUTS["change_scores"].exists()
                    else str(TRUCK_CSV.relative_to(ROOT)),
                    str(get_faf_csv().relative_to(ROOT)),
                ],
                "missing_data_flags": ",".join(missing) if missing else "",
            }
        )

    trends.sort(key=lambda x: x["commodity_market_signal_score"], reverse=True)

    fields = list(trends[0].keys()) if trends else []
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        if fields:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(trends)

    export_parquet(trends, PARQUET_PATH)

    fps = fingerprint_paths([TRUCK_CSV, get_faf_csv(), get_cfs_csv()])
    receipt = write_receipt(
        RECEIPT_PATH,
        command="market-trend-radar",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(TRUCK_CSV.relative_to(ROOT))],
        input_fingerprints=fps,
        output_files=[str(CSV_PATH.relative_to(ROOT)), str(PARQUET_PATH.relative_to(ROOT))],
        row_counts={"trends": len(trends)},
        warnings=warnings,
        missing_data_flags=missing,
        success=True,
        extra={
            "scan_type": VERSION,
            "input_source": input_source,
            "top_10": trends[:10],
            "elapsed_sec": timer.elapsed_sec,
        },
    )
    receipt["input_source"] = input_source
    return receipt
