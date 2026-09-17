"""
Physical entity matcher — candidate edges with confidence tiers.
"""

from __future__ import annotations

import csv
from typing import Any

import re

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, UNWRAPPED, WAREHOUSE
from catalog.path_resolver import resolve_family_file
from catalog.signals._common import CommandTimer, CSV_OPTS, EXPORTS_DIR, export_parquet, stable_id, write_receipt

RECEIPT_PATH = BUILD_REPORTS / "entity_resolution_edges_v1.json"
CSV_PATH = EXPORTS_DIR / "entity_resolution_edges_v1.csv"
PARQUET_PATH = WAREHOUSE / "entity_resolution_edges_v1.parquet"
VERSION = "entity_resolution_edges_v1"


def run_physical_entity_matcher(*, limit: int = 50000) -> dict[str, Any]:
    timer = CommandTimer()
    insp = resolve_family_file(
        "fmcsa_carriers", "mcmis/vehicle_inspection_file.csv", root_level=True, min_bytes=500_000_000
    )
    census = resolve_family_file("fmcsa_carriers", "company_census.csv", root_level=True, min_bytes=500_000_000)
    if not insp or not census:
        raise FileNotFoundError("FMCSA files not resolved")

    con = duckdb.connect()
    rows = con.execute(
        f"""
        WITH insp AS (
          SELECT TRY_CAST(DOT_NUMBER AS BIGINT) dot, TRIM(SHIPPER_NAME) shipper,
            UPPER(REGEXP_REPLACE(TRIM(SHIPPER_NAME), '[^A-Z0-9 ]', ' ')) shipper_norm,
            COUNT(*)::BIGINT n
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE SHIPPER_NAME IS NOT NULL AND TRIM(SHIPPER_NAME) NOT IN ('NONE','NA','SELF','')
          GROUP BY 1,2,3
        ),
        census AS (
          SELECT TRY_CAST(DOT_NUMBER AS BIGINT) dot, LEGAL_NAME
          FROM read_csv_auto(?, {CSV_OPTS})
        )
        SELECT i.dot, c.LEGAL_NAME, i.shipper, i.shipper_norm, i.n
        FROM insp i
        LEFT JOIN census c ON i.dot = c.dot
        ORDER BY i.n DESC
        LIMIT ?
        """,
        [str(insp), str(census), limit],
    ).fetchall()

    edges: list[dict[str, Any]] = []
    lei_path = UNWRAPPED / "lei_entities" / "lei2_latest"
    lei_files = sorted(lei_path.glob("*.csv")) if lei_path.is_dir() else []
    sec_path = UNWRAPPED / "sec_filings" / "company_tickers.json"

    lei_names: dict[str, str] = {}
    if lei_files:
        lei_rows = con.execute(
            f"""
            SELECT "LEI" AS lei,
              UPPER(REGEXP_REPLACE(REGEXP_REPLACE(TRIM("Entity.LegalName"), '[^A-Z0-9 ]', ' '), '\\s+', ' ')) AS name_norm
            FROM read_csv_auto(?, {CSV_OPTS}, header=true)
            WHERE "Entity.LegalName" IS NOT NULL
            """,
            [str(lei_files[-1])],
        ).fetchall()
        lei_names = {r[1]: r[0] for r in lei_rows if r[1]}

    sec_titles: dict[str, str] = {}
    if sec_path.is_file():
        import json

        data = json.loads(sec_path.read_text(encoding="utf-8"))
        for row in data.values():
            title = re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", str(row.get("title", "")).upper())).strip()
            ticker = str(row.get("ticker", "")).upper()
            if title and ticker:
                sec_titles[title] = ticker

    for r in rows:
        dot, legal, shipper, shipper_norm, n = r
        # Carrier edge (exact DOT)
        edges.append(
            {
                "edge_id": stable_id("dot", str(dot)),
                "left_family": "fmcsa_carrier",
                "left_id": str(dot),
                "left_name": legal or "",
                "right_family": "dot_number",
                "right_id": str(dot),
                "right_name": legal or "",
                "match_tier": "exact",
                "match_score": 100.0,
                "blocking_key": f"DOT_{dot}",
                "evidence": f"FMCSA census/legal name for DOT {dot}",
                "source_files": str(census.relative_to(ROOT)),
                "risk_flags": "",
                "accepted": True,
            }
        )
        # Shipper-carrier service edge (inferred from inspections)
        edges.append(
            {
                "edge_id": stable_id("svc", str(dot), shipper_norm),
                "left_family": "fmcsa_shipper",
                "left_id": shipper_norm,
                "left_name": shipper,
                "right_family": "fmcsa_carrier",
                "right_id": str(dot),
                "right_name": legal or "",
                "match_tier": "inferred",
                "match_score": min(95.0, 50.0 + n / 10.0),
                "blocking_key": f"SHIPPER_NORM_{shipper_norm[:32]}",
                "evidence": f"{n} documented inspection stops shipper→carrier",
                "source_files": str(insp.relative_to(ROOT)),
                "risk_flags": "not_bill_of_lading_proof",
                "accepted": n >= 5,
            }
        )
        if shipper_norm in lei_names:
            edges.append(
                {
                    "edge_id": stable_id("lei", shipper_norm, lei_names[shipper_norm]),
                    "left_family": "fmcsa_shipper",
                    "left_id": shipper_norm,
                    "left_name": shipper,
                    "right_family": "lei",
                    "right_id": lei_names[shipper_norm],
                    "right_name": legal or shipper,
                    "match_tier": "exact",
                    "match_score": 100.0,
                    "blocking_key": f"LEI_NAME_{shipper_norm[:32]}",
                    "evidence": "LEI legal name exact match",
                    "source_files": str(lei_files[-1].relative_to(ROOT)) if lei_files else "",
                    "risk_flags": "",
                    "accepted": True,
                }
            )
        for title, ticker in sec_titles.items():
            if len(title) >= 8 and title in shipper_norm:
                edges.append(
                    {
                        "edge_id": stable_id("sec", shipper_norm, ticker),
                        "left_family": "fmcsa_shipper",
                        "left_id": shipper_norm,
                        "left_name": shipper,
                        "right_family": "sec_ticker",
                        "right_id": ticker,
                        "right_name": title,
                        "match_tier": "blocked_fuzzy",
                        "match_score": 40.0,
                        "blocking_key": f"SEC_TITLE_{ticker}",
                        "evidence": "SEC title substring in shipper_norm",
                        "source_files": str(sec_path.relative_to(ROOT)),
                        "risk_flags": "blocked_fuzzy_not_accepted",
                        "accepted": False,
                    }
                )
                break

    fields = list(edges[0].keys()) if edges else []
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        if fields:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(edges)

    export_parquet(edges, PARQUET_PATH)

    receipt = write_receipt(
        RECEIPT_PATH,
        command="entity-resolution",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(insp.relative_to(ROOT)), str(census.relative_to(ROOT))],
        input_fingerprints={},
        output_files=[str(CSV_PATH.relative_to(ROOT)), str(PARQUET_PATH.relative_to(ROOT))],
        row_counts={"edges": len(edges)},
        warnings=[] if lei_files and sec_path.is_file() else ["lei_or_sec_partial"],
        missing_data_flags=["sam_open_bulk_deferred"] if not lei_files else [],
        success=True,
        extra={"elapsed_sec": timer.elapsed_sec},
    )
    return receipt
