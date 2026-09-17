"""Emit identity_match edges from LEI + SEC onto THG events."""

from __future__ import annotations

import json
import re
from pathlib import Path

import duckdb

from catalog.config import ROOT, UNWRAPPED
from catalog.path_resolver import resolve_family_file
from catalog.signals._common import CSV_OPTS


def _norm_name(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", name.upper())).strip()


def append_identity_events(
    con: duckdb.DuckDBPyConnection,
    *,
    input_files: list[str],
    warnings: list[str],
    shipper_limit: int = 5000,
) -> int:
    lei_dir = UNWRAPPED / "lei_entities" / "lei2_latest"
    lei_files = sorted(lei_dir.glob("*.csv")) if lei_dir.is_dir() else []
    sec_path = UNWRAPPED / "sec_filings" / "company_tickers.json"
    insp = resolve_family_file(
        "fmcsa_carriers", "mcmis/vehicle_inspection_file.csv", root_level=True, min_bytes=500_000_000
    )
    if not insp:
        warnings.append("identity_fmcsa_missing")
        return 0

    insp_rel = str(insp.relative_to(ROOT))
    input_files.append(insp_rel)

    con.execute(
        f"""
        CREATE OR REPLACE TABLE top_shippers AS
        SELECT shipper_norm, COUNT(*)::BIGINT n
        FROM (
          SELECT UPPER(REGEXP_REPLACE(REGEXP_REPLACE(TRIM(SHIPPER_NAME), '[^A-Z0-9 ]', ' '), '\\s+', ' ')) AS shipper_norm
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE SHIPPER_NAME IS NOT NULL
            AND TRIM(SHIPPER_NAME) NOT IN ('NONE','NA','SELF','LINE RUN','')
        ) s
        WHERE shipper_norm != ''
        GROUP BY 1
        ORDER BY n DESC
        LIMIT ?
        """,
        [str(insp), shipper_limit],
    )

    inserted = 0

    if lei_files:
        lei = lei_files[-1]
        lei_rel = str(lei.relative_to(ROOT))
        input_files.append(lei_rel)
        con.execute(
            f"""
            CREATE OR REPLACE TABLE lei_names AS
            SELECT
              "LEI" AS lei,
              UPPER(REGEXP_REPLACE(REGEXP_REPLACE(TRIM("Entity.LegalName"), '[^A-Z0-9 ]', ' '), '\\s+', ' ')) AS name_norm
            FROM read_csv_auto(?, {CSV_OPTS}, header=true)
            WHERE "Entity.LegalName" IS NOT NULL AND TRIM("Entity.LegalName") != ''
            """,
            [str(lei)],
        )
        con.execute(
            f"""
            INSERT INTO all_events
            SELECT
              md5('identity_match|shipper|' || s.shipper_norm || '|lei|' || l.lei) AS event_id,
              'identity_match' AS edge_type,
              'shipper' AS src_type, s.shipper_norm AS src_id,
              'lei' AS dst_type, l.lei AS dst_id,
              'snapshot' AS event_time, 'snapshot' AS event_grain,
              LEAST(100.0, 50.0 + s.n / 20.0) AS weight,
              'exact' AS confidence,
              'lei_legal_name_exact' AS inference_method,
              'lei_entities' AS source_family,
              ? AS source_path, ?::BIGINT AS source_mtime,
              json_object('match_tier', 'exact', 'inspection_stops', s.n) AS attrs_json
            FROM top_shippers s
            INNER JOIN lei_names l ON s.shipper_norm = l.name_norm
            """,
            [lei_rel, lei.stat().st_mtime],
        )
        inserted += con.execute(
            "SELECT COUNT(*)::BIGINT FROM all_events WHERE edge_type = 'identity_match' AND dst_type = 'lei'"
        ).fetchone()[0]

    if sec_path.is_file():
        sec_rel = str(sec_path.relative_to(ROOT))
        input_files.append(sec_rel)
        tickers: list[tuple[str, str, str]] = []
        data = json.loads(sec_path.read_text(encoding="utf-8"))
        for _k, row in data.items():
            title = _norm_name(str(row.get("title", "")))
            ticker = str(row.get("ticker", "")).upper()
            cik = str(row.get("cik_str", row.get("cik", "")))
            if title and ticker:
                tickers.append((title, ticker, cik))

        if tickers:
            values = ",".join(
                f"('{t.replace(chr(39), chr(39)+chr(39))}','{tk}','{c}')"
                for t, tk, c in tickers[:8000]
            )
            con.execute(
                f"""
                CREATE OR REPLACE TABLE sec_tickers AS
                SELECT * FROM (VALUES {values}) AS t(title_norm, ticker, cik)
                """
            )
            con.execute(
                f"""
                INSERT INTO all_events
                SELECT
                  md5('identity_match|shipper|' || s.shipper_norm || '|ticker|' || t.ticker) AS event_id,
                  'identity_match' AS edge_type,
                  'shipper' AS src_type, s.shipper_norm AS src_id,
                  'ticker' AS dst_type, t.ticker AS dst_id,
                  'snapshot' AS event_time, 'snapshot' AS event_grain,
                  40.0 AS weight,
                  'blocked_fuzzy' AS confidence,
                  'sec_title_substring' AS inference_method,
                  'sec_filings' AS source_family,
                  ? AS source_path, ?::BIGINT AS source_mtime,
                  json_object('match_tier', 'blocked_fuzzy', 'accepted', false, 'cik', t.cik) AS attrs_json
                FROM top_shippers s
                INNER JOIN sec_tickers t ON s.shipper_norm LIKE '%' || t.title_norm || '%'
                WHERE LENGTH(t.title_norm) >= 8
                LIMIT 2000
                """,
                [sec_rel, sec_path.stat().st_mtime],
            )
            inserted += con.execute(
                "SELECT COUNT(*)::BIGINT FROM all_events WHERE edge_type = 'identity_match' AND dst_type = 'ticker'"
            ).fetchone()[0]
    else:
        warnings.append("sec_tickers_missing")

    return inserted
