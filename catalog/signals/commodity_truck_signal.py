"""
Commodity-on-truck signal extraction.

Truck inspections are physical sensors. Aggregate to carrier×shipper×commodity signals.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, WAREHOUSE
from catalog.path_resolver import resolve_family_file
from catalog.signals._common import (
    CSV_OPTS,
    CommandTimer,
    EXPORTS_DIR,
    export_parquet,
    fingerprint_paths,
    stable_id,
    write_receipt,
)

RECEIPT_PATH = BUILD_REPORTS / "commodity_truck_signal_v1.json"
CSV_PATH = EXPORTS_DIR / "commodity_truck_signal_v1.csv"
PARQUET_PATH = WAREHOUSE / "commodity_truck_signal_v1.parquet"
VERSION = "commodity_truck_signal_v1"

SCTG_MAP = {
    "grain_feed": ("02", "Cereal grains"),
    "petroleum_chem": ("17", "Petroleum products"),
    "tanker": ("17", "Petroleum products"),
    "hazmat": ("18", "Chemical products"),
    "coal_coke": ("19", "Coal"),
    "metal_sheet": ("11", "Nonmetal minerals"),
    "waste_scrap": ("41", "Waste/scrap"),
    "general_freight": ("31", "Mixed freight"),
}


def run_commodity_truck_signal(*, min_inspections: int = 3, limit: int = 25000) -> dict[str, Any]:
    timer = CommandTimer()
    warnings: list[str] = []
    missing: list[str] = []

    insp = resolve_family_file(
        "fmcsa_carriers", "mcmis/vehicle_inspection_file.csv", root_level=True, min_bytes=500_000_000
    )
    census = resolve_family_file("fmcsa_carriers", "company_census.csv", root_level=True, min_bytes=500_000_000)
    if not insp or not census:
        raise FileNotFoundError("FMCSA inspection or census not resolved")

    con = duckdb.connect()
    total_rows = con.execute(
        f"SELECT COUNT(*)::BIGINT FROM read_csv_auto(?, {CSV_OPTS})", [str(insp)]
    ).fetchone()[0]

    sql = f"""
    WITH insp AS (
      SELECT
        TRY_CAST(DOT_NUMBER AS BIGINT) AS dot_number,
        TRIM(SHIPPER_NAME) AS shipper_name,
        UPPER(REGEXP_REPLACE(REGEXP_REPLACE(TRIM(SHIPPER_NAME), '[^A-Z0-9 ]', ' '), '\\s+', ' ')) AS shipper_name_norm,
        INSPECTION_ID,
        INSP_DATE AS signal_date,
        COUNTY_CODE_STATE AS state,
        LOCATION_DESC AS county_or_geo,
        CARGO_TANK AS commodity_raw,
        HAZMAT_PLACARD_REQ AS hazmat_flag,
        INSP_CARRIER_NAME AS carrier_name_raw,
        TRY_CAST(OOS_TOTAL AS INTEGER) AS oos_total,
        TRY_CAST(VIOL_TOTAL AS INTEGER) AS viol_total
      FROM read_csv_auto(?, {CSV_OPTS})
      WHERE DOT_NUMBER IS NOT NULL
        AND SHIPPER_NAME IS NOT NULL
        AND TRIM(SHIPPER_NAME) NOT IN ('NONE','NA','SELF','LINE RUN','')
        AND INSP_DATE IS NOT NULL
        AND TRY_CAST(INSP_DATE AS BIGINT) >= 20240101
    ),
    census AS (
      SELECT TRY_CAST(DOT_NUMBER AS BIGINT) AS dot_number, LEGAL_NAME
      FROM read_csv_auto(?, {CSV_OPTS})
    ),
    tagged AS (
      SELECT
        i.*,
        COALESCE(c.LEGAL_NAME, i.carrier_name_raw) AS carrier_name,
        CASE
          WHEN UPPER(COALESCE(i.hazmat_flag,'')) = 'Y' AND i.commodity_raw IN ('406','407','331') THEN 'petroleum_chem'
          WHEN UPPER(COALESCE(i.hazmat_flag,'')) = 'Y' THEN 'hazmat'
          WHEN i.commodity_raw IN ('406','407','331') THEN 'tanker'
          WHEN i.shipper_name_norm LIKE '%GRAIN%' OR i.shipper_name_norm LIKE '%FEED%' OR i.shipper_name_norm LIKE '%MILL%' THEN 'grain_feed'
          WHEN i.shipper_name_norm LIKE '%PETROLEUM%' OR i.shipper_name_norm LIKE '%OIL %' OR i.shipper_name_norm LIKE '%REFIN%' THEN 'petroleum_chem'
          WHEN i.shipper_name_norm LIKE '%COAL%' THEN 'coal_coke'
          WHEN i.shipper_name_norm LIKE '%CHEM%' OR i.shipper_name_norm LIKE '%PLAST%' THEN 'hazmat'
          WHEN i.shipper_name_norm LIKE '%STEEL%' OR i.shipper_name_norm LIKE '%METAL%' OR i.shipper_name_norm LIKE '%SCRAP%' THEN 'metal_sheet'
          ELSE 'general_freight'
        END AS commodity_inferred
      FROM insp i
      LEFT JOIN census c ON i.dot_number = c.dot_number
    )
    SELECT
      dot_number,
      carrier_name,
      shipper_name,
      shipper_name_norm,
      commodity_raw,
      commodity_inferred,
      CASE
        WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' AND commodity_raw IN ('406','407','331') THEN 'strong'
        WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' THEN 'medium'
        WHEN shipper_name_norm LIKE '%PETROLEUM%' OR shipper_name_norm LIKE '%GRAIN%' OR shipper_name_norm LIKE '%COAL%' THEN 'medium'
        ELSE 'weak'
      END AS commodity_confidence,
      CASE
        WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' THEN 'hazmat_placard_plus_context'
        WHEN commodity_raw IS NOT NULL AND TRIM(commodity_raw) != '' THEN 'cargo_tank_or_inspection_field'
        ELSE 'shipper_name_pattern'
      END AS inference_method,
      state,
      ANY_VALUE(county_or_geo) AS county_or_geo,
      COUNT(*)::BIGINT AS inspection_count,
      MIN(signal_date) AS first_signal_date,
      MAX(signal_date) AS last_signal_date,
      SUM(CASE WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' THEN 1 ELSE 0 END)::BIGINT AS hazmat_stops,
      SUM(COALESCE(oos_total,0))::BIGINT AS oos_count,
      SUM(COALESCE(viol_total,0))::BIGINT AS violation_count
    FROM tagged
    GROUP BY dot_number, carrier_name, shipper_name, shipper_name_norm, commodity_raw,
      commodity_inferred, commodity_confidence, inference_method, state
    HAVING COUNT(*) >= ?
    ORDER BY inspection_count DESC
    LIMIT ?
    """

    rows = con.execute(sql, [str(insp), str(census), min_inspections, limit]).fetchall()

    signals: list[dict[str, Any]] = []
    max_insp = max((int(r[10]) for r in rows), default=1)
    for r in rows:
        commodity_inferred = r[5]
        sctg2, sctg2_name = SCTG_MAP.get(commodity_inferred, ("", "Unknown"))
        insp_ct = int(r[10])
        last_date = str(r[12])
        recency = 1.0 if last_date >= "20260101" else 0.7 if last_date >= "20250101" else 0.4
        movement = round(100.0 * insp_ct / max_insp, 2)
        hazmat_boost = 1.15 if int(r[13]) > 0 else 1.0
        conf = r[6]
        market_signal = round(
            min(100.0, movement * recency * hazmat_boost * {"strong": 1.2, "medium": 1.0, "weak": 0.8}.get(conf, 0.5)),
            2,
        )
        sig_id = stable_id(str(r[0]), r[3], commodity_inferred, r[8] or "")

        signals.append(
            {
                "signal_id": sig_id,
                "signal_date": last_date,
                "source_family": "fmcsa_carriers",
                "source_file": str(insp.relative_to(ROOT)),
                "source_mtime": int(insp.stat().st_mtime),
                "source_row_count_sampled_or_total": int(total_rows),
                "dot_number": str(r[0]),
                "carrier_name": r[1],
                "shipper_name": r[2],
                "shipper_name_norm": r[3],
                "commodity_raw": r[4],
                "commodity_inferred": commodity_inferred,
                "sctg2": sctg2,
                "sctg2_name": sctg2_name,
                "commodity_confidence": conf,
                "inference_method": r[7],
                "inspection_count": insp_ct,
                "distinct_vehicle_count": None,
                "distinct_driver_count": None,
                "state": r[8],
                "county_or_geo": r[9],
                "origin_hint": None,
                "destination_hint": None,
                "corridor_hint": r[8],
                "mode": "truck",
                "hazmat_flag": "Y" if int(r[13]) > 0 else "N",
                "violation_count": int(r[15]),
                "oos_count": int(r[14]),
                "safety_risk_score": round(min(100.0, int(r[14]) * 2 + int(r[15]) * 0.5), 2),
                "recency_score": round(recency * 100, 2),
                "movement_intensity_score": movement,
                "market_signal_score": market_signal,
                "evidence_strength": conf,
                "notes": "Aggregated FMCSA inspection sensor; not bill-of-lading commodity proof",
            }
        )

    fields = list(signals[0].keys()) if signals else []
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        if fields:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(signals)

    export_parquet(signals, PARQUET_PATH)

    fps = fingerprint_paths([insp, census])
    receipt = write_receipt(
        RECEIPT_PATH,
        command="commodity-truck-signal",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(p.relative_to(ROOT)) for p in [insp, census]],
        input_fingerprints=fps,
        output_files=[str(CSV_PATH.relative_to(ROOT)), str(PARQUET_PATH.relative_to(ROOT))],
        row_counts={"signals": len(signals), "source_inspection_rows": int(total_rows)},
        warnings=warnings,
        missing_data_flags=missing,
        success=True,
        extra={
            "scan_type": VERSION,
            "thesis": "commodity on truck = market signal",
            "elapsed_sec": timer.elapsed_sec,
            "top_10": signals[:10],
        },
    )
    return receipt
