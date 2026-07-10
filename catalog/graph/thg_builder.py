"""Materialize temporal_edge_events from on-disk transport evidence."""

from __future__ import annotations

from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT
from catalog.freight_movement import get_faf_csv
from catalog.graph.iran_oil import append_iran_oil_events
from catalog.graph.schema_v1 import OUTPUTS, THG_ROOT
from catalog.graph.thg_entity import append_identity_events
from catalog.graph.thg_sources import (
    append_carrier_risk_events,
    append_eia_events,
    append_fmc_maritime_events,
    append_pipeline_events,
    append_stb_r1_events,
    append_trade_events,
)
from catalog.moving_commodity import get_cfs_csv
from catalog.path_resolver import resolve_family_file
from catalog.signals._common import CommandTimer, CSV_OPTS, fingerprint_paths, write_receipt
from catalog.source_truth import require_path

RECEIPT_PATH = BUILD_REPORTS / "thg_build_receipt_v1.json"
VERSION = "thg_build_v1"


def _build_fmcsa(con: duckdb.DuckDBPyConnection, insp: str, insp_rel: str, insp_mtime: float, from_month: str, min_stops: int) -> None:
    con.execute(
        f"""
        CREATE OR REPLACE TABLE fmcsa_events AS
        WITH insp AS (
          SELECT
            TRY_CAST(DOT_NUMBER AS BIGINT) AS dot_number,
            UPPER(REGEXP_REPLACE(REGEXP_REPLACE(TRIM(SHIPPER_NAME), '[^A-Z0-9 ]', ' '), '\\s+', ' ')) AS shipper_norm,
            SUBSTR(CAST(INSP_DATE AS VARCHAR), 1, 6) AS event_month,
            COUNTY_CODE_STATE AS state,
            CARGO_TANK AS cargo_tank,
            HAZMAT_PLACARD_REQ AS hazmat_flag
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE DOT_NUMBER IS NOT NULL
            AND SHIPPER_NAME IS NOT NULL
            AND TRIM(SHIPPER_NAME) NOT IN ('NONE','NA','SELF','LINE RUN','')
            AND INSP_DATE IS NOT NULL
            AND TRY_CAST(INSP_DATE AS BIGINT) >= {from_month}01
        ),
        tagged AS (
          SELECT *,
            CASE
              WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' AND cargo_tank IN ('406','407','331') THEN '17'
              WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' THEN '18'
              WHEN cargo_tank IN ('406','407','331') THEN '17'
              WHEN shipper_norm LIKE '%GRAIN%' OR shipper_norm LIKE '%FEED%' OR shipper_norm LIKE '%MILL%' THEN '02'
              WHEN shipper_norm LIKE '%PETROLEUM%' OR shipper_norm LIKE '%OIL %' OR shipper_norm LIKE '%REFIN%' THEN '17'
              WHEN shipper_norm LIKE '%COAL%' THEN '19'
              WHEN shipper_norm LIKE '%CHEM%' OR shipper_norm LIKE '%PLAST%' THEN '18'
              WHEN shipper_norm LIKE '%STEEL%' OR shipper_norm LIKE '%METAL%' OR shipper_norm LIKE '%SCRAP%' THEN '11'
              ELSE '31'
            END AS sctg2,
            CASE
              WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' AND cargo_tank IN ('406','407','331') THEN 'strong'
              WHEN UPPER(COALESCE(hazmat_flag,'')) = 'Y' THEN 'medium'
              WHEN shipper_norm LIKE '%GRAIN%' OR shipper_norm LIKE '%PETROLEUM%' OR shipper_norm LIKE '%COAL%' THEN 'medium'
              ELSE 'weak'
            END AS confidence
          FROM insp
          WHERE event_month >= '{from_month}'
        ),
        monthly AS (
          SELECT event_month, shipper_norm, dot_number,
            COALESCE(state, 'UNK') AS state, sctg2,
            MAX(confidence) AS confidence, COUNT(*)::DOUBLE AS weight
          FROM tagged
          GROUP BY 1, 2, 3, 4, 5
          HAVING COUNT(*) >= {min_stops}
        )
        SELECT
          md5('observed_haul|' || shipper_norm || '|' || CAST(dot_number AS VARCHAR) || '|' || state || '|' || event_month) AS event_id,
          'observed_haul' AS edge_type, 'shipper' AS src_type, shipper_norm AS src_id,
          'carrier' AS dst_type, CAST(dot_number AS VARCHAR) AS dst_id,
          event_month AS event_time, 'month' AS event_grain, weight, confidence,
          'fmcsa_inspection_aggregate' AS inference_method, 'fmcsa_carriers' AS source_family,
          ? AS source_path, ?::BIGINT AS source_mtime,
          json_object('sctg2', sctg2, 'state', state) AS attrs_json
        FROM monthly
        UNION ALL
        SELECT
          md5('hauls_commodity|' || CAST(dot_number AS VARCHAR) || '|' || sctg2 || '|' || event_month) AS event_id,
          'hauls_commodity' AS edge_type, 'carrier' AS src_type, CAST(dot_number AS VARCHAR) AS src_id,
          'commodity' AS dst_type, sctg2 AS dst_id,
          event_month AS event_time, 'month' AS event_grain,
          SUM(weight) AS weight, MAX(confidence) AS confidence,
          'fmcsa_inspection_aggregate' AS inference_method, 'fmcsa_carriers' AS source_family,
          ? AS source_path, ?::BIGINT AS source_mtime,
          json_object('aggregated_states', COUNT(DISTINCT state)) AS attrs_json
        FROM monthly
        GROUP BY event_month, dot_number, sctg2
        UNION ALL
        SELECT
          md5('operates_in|' || CAST(dot_number AS VARCHAR) || '|' || state || '|' || event_month) AS event_id,
          'operates_in' AS edge_type, 'carrier' AS src_type, CAST(dot_number AS VARCHAR) AS src_id,
          'state' AS dst_type, state AS dst_id,
          event_month AS event_time, 'month' AS event_grain,
          SUM(weight) AS weight, MAX(confidence) AS confidence,
          'fmcsa_inspection_aggregate' AS inference_method, 'fmcsa_carriers' AS source_family,
          ? AS source_path, ?::BIGINT AS source_mtime,
          json_object('state', state) AS attrs_json
        FROM monthly
        GROUP BY event_month, dot_number, state
        """,
        [insp, insp_rel, insp_mtime, insp_rel, insp_mtime, insp_rel, insp_mtime],
    )


def _build_macro(con: duckdb.DuckDBPyConnection, faf: str, faf_rel: str, faf_mtime: float, cfs: str, cfs_rel: str, cfs_mtime: float) -> None:
    con.execute(
        f"""
        CREATE OR REPLACE TABLE macro_events AS
        WITH faf AS (
          SELECT sctg2, dms_orig AS corridor, SUM(TRY_CAST(tons_2024 AS DOUBLE)) AS ktons
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE sctg2 IS NOT NULL
          GROUP BY 1, 2
        ),
        cfs AS (
          SELECT SUBSTR(REGEXP_REPLACE(SCTG,'[^0-9]',''),1,2) AS sctg2,
            SUM(TRY_CAST(SHIPMT_WGHT AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE)) AS wgt
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE SCTG IS NOT NULL
          GROUP BY 1
        )
        SELECT
          md5('modeled_flow|' || corridor || '|' || sctg2) AS event_id,
          'modeled_flow' AS edge_type, 'corridor' AS src_type, corridor AS src_id,
          'commodity' AS dst_type, sctg2 AS dst_id,
          '2024' AS event_time, 'year' AS event_grain, ktons AS weight,
          'strong' AS confidence, 'faf5_tons_2024' AS inference_method,
          'faf5_freight' AS source_family, ? AS source_path, ?::BIGINT AS source_mtime,
          '{{}}' AS attrs_json
        FROM faf
        UNION ALL
        SELECT
          md5('shipment_share|' || sctg2) AS event_id,
          'shipment_share' AS edge_type, 'commodity' AS src_type, sctg2 AS src_id,
          'national' AS dst_type, 'US' AS dst_id,
          '2022' AS event_time, 'year' AS event_grain, wgt AS weight,
          'strong' AS confidence, 'cfs_2022_pums' AS inference_method,
          'trade' AS source_family, ? AS source_path, ?::BIGINT AS source_mtime,
          '{{}}' AS attrs_json
        FROM cfs WHERE sctg2 IS NOT NULL AND sctg2 != ''
        """,
        [faf, cfs, faf_rel, faf_mtime, cfs_rel, cfs_mtime],
    )


def run_thg_build(*, from_month: str = "202401", min_stops: int = 2) -> dict[str, Any]:
    timer = CommandTimer()
    THG_ROOT.mkdir(parents=True, exist_ok=True)

    insp = resolve_family_file(
        "fmcsa_carriers", "mcmis/vehicle_inspection_file.csv", root_level=True, min_bytes=500_000_000
    )
    if not insp:
        raise FileNotFoundError("FMCSA inspections not resolved")

    faf = get_faf_csv()
    cfs = get_cfs_csv()
    insp_rel = str(insp.relative_to(ROOT))
    insp_mtime = insp.stat().st_mtime
    faf_rel = str(faf.relative_to(ROOT))
    faf_mtime = faf.stat().st_mtime
    cfs_rel = str(cfs.relative_to(ROOT))
    cfs_mtime = cfs.stat().st_mtime
    events_path = OUTPUTS["events"]

    con = duckdb.connect()
    _build_fmcsa(con, str(insp), insp_rel, insp_mtime, from_month, min_stops)
    _build_macro(con, str(faf), faf_rel, faf_mtime, str(cfs), cfs_rel, cfs_mtime)

    con.execute(
        """
        CREATE OR REPLACE TABLE all_events AS
        SELECT * FROM fmcsa_events
        UNION ALL
        SELECT * FROM macro_events
        """
    )

    build_warnings: list[str] = []
    extra_input_files: list[str] = []
    append_eia_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_iran_oil_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_trade_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_fmc_maritime_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_stb_r1_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_carrier_risk_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_pipeline_events(con, input_files=extra_input_files, warnings=build_warnings)
    append_identity_events(con, input_files=extra_input_files, warnings=build_warnings)

    try:
        dwell = require_path("stb_ep724_dwell")
        dwell_rel = str(dwell.relative_to(ROOT))
        con.execute(
            f"""
            INSERT INTO all_events
            SELECT
              md5('rail_metric|' || railroad_mark || '|' || measure_name_analytics || '|' || CAST(report_period_end_date AS VARCHAR)) AS event_id,
              'rail_metric' AS edge_type, 'rail_operator' AS src_type, railroad_mark AS src_id,
              'national' AS dst_type, measure_name_analytics AS dst_id,
              SUBSTR(CAST(report_period_end_date AS VARCHAR), 1, 7) AS event_time,
              'month' AS event_grain, TRY_CAST(fact_value AS DOUBLE) AS weight,
              'medium' AS confidence, 'stb_ep724_dwell' AS inference_method,
              'stb_rail' AS source_family, ? AS source_path, ?::BIGINT AS source_mtime,
              json_object('railroad_name', railroad_name) AS attrs_json
            FROM read_csv_auto(?, {CSV_OPTS})
            WHERE railroad_mark IS NOT NULL AND measure_name_analytics ILIKE '%dwell%'
            """,
            [dwell_rel, dwell.stat().st_mtime, str(dwell)],
        )
    except FileNotFoundError:
        pass

    con.execute("COPY all_events TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(events_path)])

    event_count = con.execute("SELECT COUNT(*)::BIGINT FROM all_events").fetchone()[0]
    by_type = con.execute(
        "SELECT edge_type, COUNT(*)::BIGINT n FROM all_events GROUP BY 1 ORDER BY n DESC"
    ).fetchall()

    con.execute(
        """
        COPY (
          SELECT DISTINCT src_type AS node_type, src_id AS node_id FROM all_events
          UNION SELECT DISTINCT dst_type, dst_id FROM all_events
        ) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)
        """,
        [str(OUTPUTS["nodes"])],
    )
    node_count = con.execute("SELECT COUNT(*)::BIGINT FROM read_parquet(?)", [str(OUTPUTS["nodes"])]).fetchone()[0]

    con.execute(
        """
        COPY (SELECT DISTINCT edge_type, src_type, dst_type FROM all_events)
        TO ? (FORMAT PARQUET, COMPRESSION ZSTD)
        """,
        [str(OUTPUTS["edge_catalog"])],
    )

    receipt = write_receipt(
        RECEIPT_PATH,
        command="thg-build",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[insp_rel, faf_rel, cfs_rel, *extra_input_files],
        input_fingerprints=fingerprint_paths([insp, faf, cfs]),
        output_files=[
            str(OUTPUTS["events"].relative_to(ROOT)),
            str(OUTPUTS["nodes"].relative_to(ROOT)),
            str(OUTPUTS["edge_catalog"].relative_to(ROOT)),
        ],
        row_counts={"events": int(event_count), "nodes": int(node_count), "edge_types": len(by_type)},
        warnings=build_warnings,
        missing_data_flags=[],
        success=True,
        extra={
            "scan_type": VERSION,
            "from_month": from_month,
            "events_by_type": {r[0]: int(r[1]) for r in by_type},
            "elapsed_sec": timer.elapsed_sec,
        },
    )
    return receipt
