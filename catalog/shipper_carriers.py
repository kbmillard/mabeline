"""
Shipper→carrier roll-up exports from FMCSA inspection evidence.

Uses inspection SHIPPER_NAME ties joined to census on DOT_NUMBER.
Does not rank on CRGO_* flags alone.
"""

from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from typing import Any

import duckdb

from catalog.cargo_inspection import get_census, get_inspection_file
from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.source_truth import resolved_sources_dict
from catalog.util import append_log, write_json

EXPORTS_DIR = ROOT / "exports"
CSV_OPTS = "header=true, ignore_errors=true"

SHIPPER_FILTER_SQL = """
  UPPER(TRIM(SHIPPER_NAME)) LIKE '%' || UPPER(?) || '%'
  AND TRIM(SHIPPER_NAME) NOT IN ('NONE', 'NA', 'SELF', 'LINE RUN', '')
"""


def run_shipper_carriers(
    *,
    shipper: str,
    min_stops: int = 1,
    export_name: str | None = None,
    receipt_name: str | None = None,
) -> dict[str, Any]:
    """Roll up distinct carriers serving a shipper filter pattern."""
    t0 = time.monotonic()
    inspection_file = get_inspection_file()
    census = get_census()
    if not inspection_file.exists() or not census.exists():
        raise FileNotFoundError("FMCSA inspection or census missing")

    slug = re.sub(r"[^a-z0-9]+", "_", shipper.lower()).strip("_")[:48] or "shipper"
    csv_name = export_name or f"{slug}_carriers_v1.csv"
    receipt_file = receipt_name or f"{slug}_carriers_receipt_v1.json"
    csv_path = EXPORTS_DIR / csv_name
    receipt_path = BUILD_REPORTS / receipt_file

    con = duckdb.connect()
    insp = str(inspection_file)
    census_path = str(census)

    rows = con.execute(
        f"""
        WITH filtered AS (
          SELECT
            TRY_CAST(i.DOT_NUMBER AS BIGINT) AS dot_number,
            TRIM(i.SHIPPER_NAME) AS shipper_name_variant,
            TRIM(i.INSP_CARRIER_NAME) AS insp_carrier_name,
            i.INSPECTION_ID,
            i.INSP_DATE
          FROM read_csv_auto(?, {CSV_OPTS}) i
          WHERE i.DOT_NUMBER IS NOT NULL
            AND i.SHIPPER_NAME IS NOT NULL
            AND {SHIPPER_FILTER_SQL}
        ),
        census AS (
          SELECT
            TRY_CAST(DOT_NUMBER AS BIGINT) AS dot_number,
            LEGAL_NAME,
            PHY_CITY,
            PHY_STATE,
            PHONE,
            TRY_CAST(POWER_UNITS AS INTEGER) AS power_units
          FROM read_csv_auto(?, {CSV_OPTS})
        )
        SELECT
          f.dot_number,
          COALESCE(c.LEGAL_NAME, f.insp_carrier_name) AS carrier_name,
          c.PHY_CITY AS city,
          c.PHY_STATE AS state,
          c.PHONE AS phone,
          c.power_units,
          COUNT(DISTINCT f.INSPECTION_ID)::BIGINT AS inspection_count,
          COUNT(*)::BIGINT AS stop_count,
          MIN(f.INSP_DATE) AS first_inspection_date,
          MAX(f.INSP_DATE) AS last_inspection_date,
          STRING_AGG(DISTINCT f.shipper_name_variant, ' | ') AS shipper_name_variant
        FROM filtered f
        LEFT JOIN census c ON f.dot_number = c.dot_number
        GROUP BY 1,2,3,4,5,6
        HAVING COUNT(*) >= ?
        ORDER BY stop_count DESC
        """,
        [insp, shipper, census_path, min_stops],
    ).fetchall()

    carriers: list[dict[str, Any]] = []
    for row in rows:
        variants = row[10]
        variant_str = str(variants) if variants else ""
        carriers.append(
            {
                "dot_number": str(row[0]),
                "carrier_name": row[1],
                "city": row[2],
                "state": row[3],
                "phone": row[4],
                "power_units": row[5],
                "inspection_count": int(row[6]),
                "stop_count": int(row[7]),
                "first_inspection_date": row[8],
                "last_inspection_date": row[9],
                "shipper_name_variant": variant_str,
                "evidence_source": str(inspection_file.relative_to(ROOT)),
                "confidence": (
                    "high — documented shipper on FMCSA inspection stop; "
                    "carrier identity from census LEGAL_NAME or inspection carrier name"
                ),
                "confidence_notes": (
                    "Not bill-of-lading proof of cargo; inspection-documented shipper field. "
                    "Do not infer SCTG commodity from this join alone."
                ),
            }
        )

    fields = [
        "dot_number",
        "carrier_name",
        "city",
        "state",
        "phone",
        "power_units",
        "stop_count",
        "inspection_count",
        "first_inspection_date",
        "last_inspection_date",
        "shipper_name_variant",
        "evidence_source",
        "confidence",
        "confidence_notes",
    ]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for c in carriers:
            w.writerow(c)

    receipt = {
        "scan_type": "shipper_carriers_receipt_v1",
        "shipper_filter": shipper,
        "distinct_carriers": len(carriers),
        "min_stops": min_stops,
        "export_csv": str(csv_path.relative_to(ROOT)),
        "sources": {
            "inspections": str(inspection_file.relative_to(ROOT)),
            "census": str(census.relative_to(ROOT)),
            "source_truth": resolved_sources_dict(),
        },
        "join_key": "DOT_NUMBER",
        "method": "SHIPPER_NAME LIKE filter → group by DOT_NUMBER",
        "top_10": carriers[:10],
        "confidence_policy": "inspection shipper field; not CRGO_* flags",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }
    write_json(receipt_path, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} {receipt_file} carriers={len(carriers)} shipper={shipper!r}",
    )
    receipt["receipt_path"] = str(receipt_path.relative_to(ROOT))
    return receipt


def run_dollar_general_carriers() -> dict[str, Any]:
    return run_shipper_carriers(
        shipper="DOLLAR GENERAL",
        min_stops=1,
        export_name="dollar_general_carriers_v1.csv",
        receipt_name="dollar_general_carriers_receipt_v1.json",
    )
