"""
Inspection-level cargo → entity ties from FMCSA MCMIS.

Documented on disk:
  _unwrapped/fmcsa_carriers/mcmis/vehicle_inspection_file.csv  (~8.3M rows)
  _unwrapped/fmcsa_carriers/company_census.csv                   (carrier CRGO_* certs)

Each inspection row can include:
  DOT_NUMBER, INSP_CARRIER_NAME, SHIPPER_NAME, CARGO_TANK, HAZMAT_PLACARD_REQ,
  GROSS_COMB_VEH_WT, INSP_LEVEL_ID, LOCATION, COUNTY_CODE_STATE

Commodity is NOT a direct SCTG field on inspections. Tie path:
  inspection.shipper + inspection.cargo_tank/hazmat
    → carrier entity (DOT + legal name)
    → commodity capability (company_census CRGO_* flags)
    → inferred_lane (metal, grain, petroleum, hazmat, general)

This is documented enforcement stops — not live load postings.
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.source_truth import require_path, resolved_sources_dict
from catalog.util import append_log, write_json

EXPORTS_DIR = ROOT / "exports"
RECEIPT_PATH = BUILD_REPORTS / "cargo_inspection_v1.json"
CSV_OPTS = "header=true, ignore_errors=true"


def get_inspection_file() -> Path:
    return require_path("fmcsa_inspections")


def get_census() -> Path:
    return require_path("fmcsa_census")

CRGO_LANE_SQL = """
  CASE
    WHEN c.crgo_metal = 'X' THEN 'metal_sheet'
    WHEN c.crgo_grain = 'X' THEN 'grain_feed'
    WHEN c.crgo_liqgas = 'X' OR c.crgo_chem = 'X' THEN 'petroleum_chem'
    WHEN c.crgo_coal = 'X' THEN 'coal_coke'
    WHEN c.crgo_waste = 'X' THEN 'waste_scrap'
    WHEN c.crgo_gen = 'X' THEN 'general_freight'
    ELSE 'unknown'
  END
"""

TANK_LANE_SQL = """
  CASE
    WHEN i.cargo_tank IN ('406','407','331') THEN 'tanker'
    WHEN UPPER(COALESCE(i.hazmat,'')) = 'Y' THEN 'hazmat'
    ELSE NULL
  END
"""


def run_cargo_inspection(
    *,
    min_inspections: int = 5,
    limit: int = 500,
    state: str | None = None,
    lane: str | None = None,
    export_name: str | None = None,
) -> dict[str, Any]:
    inspection_file = get_inspection_file()
    census = get_census()
    if not inspection_file.exists() or not census.exists():
        raise FileNotFoundError("FMCSA inspection or census files missing")

    t0 = time.monotonic()
    con = duckdb.connect()
    insp = str(inspection_file)
    census_path = str(census)

    state_filter = ""
    params: list[Any] = [insp, census_path]
    if state:
        state_filter = "AND i.COUNTY_CODE_STATE = ?"
        params.append(state.upper())

    coverage = con.execute(
        f"""
        SELECT
          COUNT(*)::BIGINT AS total_inspections,
          SUM(CASE WHEN SHIPPER_NAME IS NOT NULL AND TRIM(SHIPPER_NAME) NOT IN ('','NONE','NA','SELF') THEN 1 ELSE 0 END)::BIGINT AS documented_shipper,
          SUM(CASE WHEN CARGO_TANK IS NOT NULL AND TRIM(CARGO_TANK) != '' THEN 1 ELSE 0 END)::BIGINT AS documented_cargo_tank,
          SUM(CASE WHEN UPPER(COALESCE(HAZMAT_PLACARD_REQ,'')) = 'Y' THEN 1 ELSE 0 END)::BIGINT AS hazmat_placard
        FROM read_csv_auto(?, {CSV_OPTS})
        """,
        [insp],
    ).fetchone()

    rows = con.execute(
        f"""
        WITH grouped AS (
        WITH insp AS (
          SELECT
            TRY_CAST(DOT_NUMBER AS BIGINT) AS dot,
            INSPECTION_ID,
            INSP_DATE,
            INSP_LEVEL_ID AS insp_level,
            TRIM(SHIPPER_NAME) AS shipper,
            CARGO_TANK AS cargo_tank,
            HAZMAT_PLACARD_REQ AS hazmat,
            TRY_CAST(GROSS_COMB_VEH_WT AS INTEGER) AS gcw,
            INSP_CARRIER_NAME AS carrier_name,
            COUNTY_CODE_STATE AS state,
            LOCATION_DESC AS location
          FROM read_csv_auto(?, {CSV_OPTS}) i
          WHERE DOT_NUMBER IS NOT NULL
            AND SHIPPER_NAME IS NOT NULL
            AND TRIM(SHIPPER_NAME) NOT IN ('NONE', 'NA', 'SELF', 'LINE RUN', '')
            {state_filter}
        ),
        census AS (
          SELECT
            TRY_CAST(DOT_NUMBER AS BIGINT) AS dot,
            LEGAL_NAME,
            PHY_STATE,
            PHY_CITY,
            PHONE,
            TRY_CAST(POWER_UNITS AS INTEGER) AS power_units,
            UPPER(TRIM(COALESCE(CRGO_METALSHEET,''))) AS crgo_metal,
            UPPER(TRIM(COALESCE(CRGO_GRAINFEED,''))) AS crgo_grain,
            UPPER(TRIM(COALESCE(CRGO_LIQGAS,''))) AS crgo_liqgas,
            UPPER(TRIM(COALESCE(CRGO_CHEM,''))) AS crgo_chem,
            UPPER(TRIM(COALESCE(CRGO_COALCOKE,''))) AS crgo_coal,
            UPPER(TRIM(COALESCE(CRGO_GARBAGE,''))) AS crgo_waste,
            UPPER(TRIM(COALESCE(CRGO_GENFREIGHT,''))) AS crgo_gen
          FROM read_csv_auto(?, {CSV_OPTS})
        )
        SELECT
          i.shipper,
          i.dot,
          COALESCE(c.LEGAL_NAME, i.carrier_name) AS carrier_entity,
          c.PHY_CITY,
          c.PHY_STATE,
          c.PHONE,
          c.power_units,
          {CRGO_LANE_SQL} AS commodity_lane_cert,
          {TANK_LANE_SQL} AS inspection_lane_hint,
          i.cargo_tank,
          i.hazmat,
          ROUND(AVG(i.gcw)) AS avg_gcw,
          COUNT(*)::BIGINT AS inspection_count,
          MAX(i.INSP_DATE) AS latest_insp_date
        FROM insp i
        LEFT JOIN census c ON i.dot = c.dot
        GROUP BY 1,2,3,4,5,6,7,8,9,10,11
        HAVING COUNT(*) >= ?
        )
        SELECT * FROM grouped
        {"WHERE commodity_lane_cert = ?" if lane else ""}
        ORDER BY inspection_count DESC
        LIMIT ?
        """,
        (
            [*params, min_inspections]
            + ([lane] if lane else [])
            + [limit]
        ),
    ).fetchall()

    ties = []
    for row in rows:
        ties.append(
            {
                "shipper": row[0],
                "dot_number": str(row[1]),
                "carrier_entity": row[2],
                "city": row[3],
                "state": row[4],
                "phone": row[5],
                "power_units": row[6],
                "commodity_lane_cert": row[7],
                "inspection_lane_hint": row[8],
                "cargo_tank": row[9],
                "hazmat": row[10],
                "avg_gcw": row[11],
                "inspection_count": int(row[12]),
                "latest_insp_date": row[13],
            }
        )

    by_lane: dict[str, int] = {}
    for t in ties:
        lane = t["commodity_lane_cert"]
        by_lane[lane] = by_lane.get(lane, 0) + t["inspection_count"]

    csv_path = EXPORTS_DIR / (export_name or "cargo_inspection_ties_v1.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(ties[0].keys()) if ties else []
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        if fields:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(ties)

    receipt = {
        "scan_type": "cargo_inspection_v1",
        "as_of": utc_now()[:10],
        "what_this_is": (
            "FMCSA roadside inspection records joined to carrier census on DOT_NUMBER. "
            "Shipper name at inspection ties a shipper entity to a carrier entity; "
            "CRGO_* census flags tie carrier to certified commodity lanes."
        ),
        "what_this_is_not": [
            "Bill of lading commodity codes (SCTG) per inspection — not in this file",
            "Live available loads",
            "Proof of specific cargo on that truck — shipper field is inspection documentation",
        ],
        "sources": {
            "inspections": str(inspection_file.relative_to(ROOT)),
            "census": str(census.relative_to(ROOT)),
            "source_truth": resolved_sources_dict(),
        },
        "join_key": "TRY_CAST(DOT_NUMBER AS BIGINT)",
        "coverage": {
            "total_inspections": int(coverage[0]),
            "documented_shipper": int(coverage[1]),
            "documented_cargo_tank": int(coverage[2]),
            "hazmat_placard": int(coverage[3]),
            "shipper_rate_pct": round(100.0 * coverage[1] / coverage[0], 1) if coverage[0] else 0,
        },
        "commodity_tie_method": {
            "primary": "company_census CRGO_* certification flags",
            "secondary": "inspection CARGO_TANK code (406/407/331=tanker) + HAZMAT_PLACARD_REQ",
            "entity_shipper": "inspection SHIPPER_NAME",
            "entity_carrier": "DOT_NUMBER + LEGAL_NAME / INSP_CARRIER_NAME",
        },
        "insp_level_ids": {
            "1": "Full inspection (driver + vehicle)",
            "2": "Walk-around driver/vehicle",
            "3": "Driver-only",
            "4": "Special study",
            "5": "Vehicle-only (Terminal)",
            "6": "Radioactive materials",
        },
        "by_commodity_lane": by_lane,
        "top_ties": ties[:25],
        "tie_count": len(ties),
        "export_csv": str(csv_path.relative_to(ROOT)),
        "filters": {
            "min_inspections": min_inspections,
            "state": state,
            "lane": lane,
            "limit": limit,
        },
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} cargo_inspection_v1.json ties={len(ties)}",
    )
    return receipt
