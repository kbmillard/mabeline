"""
Transport Economy v1 — wire physical economy through transportation data.

Spine: SCTG commodity code
  ├─ FAF5 modeled tonnage + mode share (2024)
  ├─ Census CFS shipment weight + value (2022)
  ├─ FMCSA carrier count by cargo certification
  └─ MCMIS inspection shipper→carrier ties (documented stops)

Run: bin/mabel-catalog transport-economy
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.freight_movement import MODE_LABELS, SCTG2_LABELS, get_faf_csv
from catalog.source_truth import require_path, resolved_sources_dict
from catalog.util import append_log, write_json

EXPORTS_DIR = ROOT / "exports"
RECEIPT_PATH = BUILD_REPORTS / "transport_economy_v1.json"
CSV_OPTS = "header=true, ignore_errors=true"


def get_cfs_csv() -> Path:
    return require_path("cfs_2022_pums")


def get_fmcsa_census() -> Path:
    return require_path("fmcsa_census")


def get_inspection_file() -> Path:
    return require_path("fmcsa_inspections")

# SCTG → FMCSA cargo flags + inspection lane keys
SCTG_WIRE: dict[str, dict[str, Any]] = {
    "01": {"crgo": ("CRGO_FARMSUPP",), "lanes": ("grain_feed",)},
    "02": {"crgo": ("CRGO_GRAINFEED", "CRGO_FARMSUPP", "CRGO_PRODUCE"), "lanes": ("grain_feed",)},
    "03": {"crgo": ("CRGO_PRODUCE", "CRGO_FARMSUPP"), "lanes": ("grain_feed",)},
    "07": {"crgo": ("CRGO_MEAT", "CRGO_COLDFOOD"), "lanes": ("general_freight",)},
    "11": {"crgo": ("CRGO_DRYBULK",), "lanes": ("waste_scrap",)},
    "12": {"crgo": ("CRGO_LIQGAS",), "lanes": ("petroleum_chem",)},
    "15": {"crgo": ("CRGO_DRYBULK", "CRGO_BLDGMAT"), "lanes": ("general_freight",)},
    "16": {"crgo": ("CRGO_LIQGAS",), "lanes": ("petroleum_chem",)},
    "17": {"crgo": ("CRGO_LIQGAS", "CRGO_CHEM", "CRGO_OILFIELD"), "lanes": ("petroleum_chem",)},
    "18": {"crgo": ("CRGO_CHEM",), "lanes": ("petroleum_chem",)},
    "19": {"crgo": ("CRGO_COALCOKE",), "lanes": ("coal_coke",)},
    "31": {"crgo": ("CRGO_GENFREIGHT", "CRGO_INTERMODAL"), "lanes": ("general_freight",)},
    "41": {"crgo": ("CRGO_GARBAGE", "CRGO_DRYBULK"), "lanes": ("waste_scrap",)},
}

LANE_TO_SCTG: dict[str, str] = {}
for sctg, spec in SCTG_WIRE.items():
    for lane in spec["lanes"]:
        if lane not in LANE_TO_SCTG:
            LANE_TO_SCTG[lane] = sctg

INSPECTION_LANE_SQL = """
  CASE
    WHEN c.crgo_grain = 'X' THEN 'grain_feed'
    WHEN c.crgo_liqgas = 'X' OR c.crgo_chem = 'X' THEN 'petroleum_chem'
    WHEN c.crgo_coal = 'X' THEN 'coal_coke'
    WHEN c.crgo_waste = 'X' THEN 'waste_scrap'
    WHEN c.crgo_gen = 'X' THEN 'general_freight'
    ELSE 'unknown'
  END
"""


def _faf5_by_sctg(con: duckdb.DuckDBPyConnection, year: str = "2024") -> dict[str, dict]:
    faf = get_faf_csv()
    if not faf.exists():
        return {}
    tons_col = f"tons_{year}"
    tm_col = f"tmiles_{year}"
    path = str(faf)

    totals = con.execute(
        f"""
        SELECT sctg2,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons,
          ROUND(SUM(TRY_CAST({tm_col} AS DOUBLE)), 2) AS mtmiles
        FROM read_csv_auto(?, {CSV_OPTS})
        WHERE sctg2 IS NOT NULL
        GROUP BY 1
        """,
        [path],
    ).fetchall()

    total_kt = sum(float(t) for _, t, _ in totals if t)
    out: dict[str, dict] = {}
    for sctg, kt, tm in totals:
        s = str(sctg).zfill(2)[:2]
        out[s] = {
            "thousand_tons": float(kt),
            "million_ton_miles": float(tm),
            "pct_of_national_tons": round(100.0 * float(kt) / total_kt, 2) if total_kt else 0,
        }

    # top mode per sctg (top 8 commodities by tonnage)
    top_sctgs = sorted(out.keys(), key=lambda k: out[k]["thousand_tons"], reverse=True)[:12]
    if top_sctgs:
        placeholders = ",".join(f"'{s}'" for s in top_sctgs)
        modes = con.execute(
            f"""
            SELECT sctg2, dms_mode,
              ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons
            FROM read_csv_auto(?, {CSV_OPTS})
            WHERE sctg2 IN ({placeholders})
            GROUP BY 1, 2 ORDER BY 1, 3 DESC
            """,
            [path],
        ).fetchall()
        mode_by_sctg: dict[str, list] = {}
        for sctg, mode, kt in modes:
            s = str(sctg).zfill(2)[:2]
            mode_by_sctg.setdefault(s, []).append(
                {
                    "mode": MODE_LABELS.get(str(mode), str(mode)),
                    "thousand_tons": float(kt),
                }
            )
        for s in top_sctgs:
            if s in out and s in mode_by_sctg:
                out[s]["top_modes"] = mode_by_sctg[s][:3]
    return out


def _cfs_by_sctg(con: duckdb.DuckDBPyConnection) -> dict[str, dict]:
    cfs = get_cfs_csv()
    if not cfs.exists():
        return {}
    path = str(cfs)
    rows = con.execute(
        f"""
        SELECT SCTG,
          ROUND(SUM(TRY_CAST(SHIPMT_WGHT AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e6, 2) AS mt,
          ROUND(SUM(TRY_CAST(SHIPMT_VALUE AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e9, 2) AS busd
        FROM read_csv_auto(?, {CSV_OPTS})
        WHERE SCTG IS NOT NULL
        GROUP BY 1
        """,
        [path],
    ).fetchall()
    total_mt = sum(float(mt) for _, mt, _ in rows if mt)
    out = {}
    for sctg, mt, busd in rows:
        s = str(sctg).zfill(2)[:2]
        out[s] = {
            "million_tons": float(mt),
            "billion_usd": float(busd),
            "pct_of_shipment_tons": round(100.0 * float(mt) / total_mt, 2) if total_mt else 0,
        }
    return out


def _fmcsa_carriers_by_sctg(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    census = get_fmcsa_census()
    if not census.exists():
        return {}
    path = str(census)
    out: dict[str, int] = {}
    for sctg, spec in SCTG_WIRE.items():
        flags = spec["crgo"]
        flag_sql = " OR ".join(f"UPPER(TRIM(COALESCE({f}, ''))) = 'X'" for f in flags)
        n = con.execute(
            f"""
            SELECT COUNT(*)::BIGINT FROM read_csv_auto(?, {CSV_OPTS})
            WHERE ({flag_sql}) AND LEGAL_NAME IS NOT NULL
            """,
            [path],
        ).fetchone()[0]
        out[sctg] = int(n)
    return out


def _inspection_ties_by_lane(con: duckdb.DuckDBPyConnection, *, min_count: int = 25, limit_per_lane: int = 5) -> dict[str, list]:
    insp_path = get_inspection_file()
    census_path = get_fmcsa_census()
    if not insp_path.exists() or not census_path.exists():
        return {}
    insp, census = str(insp_path), str(census_path)

    rows = con.execute(
        f"""
        WITH insp AS (
          SELECT
            TRY_CAST(DOT_NUMBER AS BIGINT) AS dot,
            TRIM(SHIPPER_NAME) AS shipper,
            INSP_CARRIER_NAME AS carrier_name
          FROM read_csv_auto(?, {CSV_OPTS})
          WHERE DOT_NUMBER IS NOT NULL
            AND SHIPPER_NAME IS NOT NULL
            AND TRIM(SHIPPER_NAME) NOT IN ('NONE','NA','SELF','LINE RUN','')
        ),
        census AS (
          SELECT TRY_CAST(DOT_NUMBER AS BIGINT) AS dot, LEGAL_NAME,
            UPPER(TRIM(COALESCE(CRGO_GRAINFEED,''))) AS crgo_grain,
            UPPER(TRIM(COALESCE(CRGO_LIQGAS,''))) AS crgo_liqgas,
            UPPER(TRIM(COALESCE(CRGO_CHEM,''))) AS crgo_chem,
            UPPER(TRIM(COALESCE(CRGO_COALCOKE,''))) AS crgo_coal,
            UPPER(TRIM(COALESCE(CRGO_GARBAGE,''))) AS crgo_waste,
            UPPER(TRIM(COALESCE(CRGO_GENFREIGHT,''))) AS crgo_gen
          FROM read_csv_auto(?, {CSV_OPTS})
        ),
        grouped AS (
          SELECT
            {INSPECTION_LANE_SQL} AS lane,
            i.shipper,
            COALESCE(c.LEGAL_NAME, i.carrier_name) AS carrier,
            COUNT(*)::BIGINT AS n
          FROM insp i
          LEFT JOIN census c ON i.dot = c.dot
          GROUP BY 1, 2, 3
          HAVING COUNT(*) >= ?
        )
        SELECT lane, shipper, carrier, n
        FROM grouped
        WHERE lane != 'unknown'
        ORDER BY lane, n DESC
        """,
        [insp, census, min_count],
    ).fetchall()

    by_lane: dict[str, list] = {}
    for lane, shipper, carrier, n in rows:
        by_lane.setdefault(lane, [])
        if len(by_lane[lane]) < limit_per_lane:
            by_lane[lane].append({"shipper": shipper, "carrier": carrier, "inspection_count": int(n)})
    return by_lane


def _transport_score(faf_pct: float, cfs_pct: float, carriers: int, insp_count: int) -> float:
    return round(
        faf_pct * 0.35 + cfs_pct * 0.30 + min(20, carriers / 5000) + min(15, insp_count / 500),
        2,
    )


def run_transport_economy(*, faf_year: str = "2024") -> dict[str, Any]:
    t0 = time.monotonic()
    con = duckdb.connect()

    faf = _faf5_by_sctg(con, faf_year)
    cfs = _cfs_by_sctg(con)
    carriers = _fmcsa_carriers_by_sctg(con)
    insp_by_lane = _inspection_ties_by_lane(con)

    stb_addon: dict[str, Any] | None = None
    try:
        from catalog.stb_ep724 import ep724_rail_addon

        stb_addon = ep724_rail_addon(con)
    except Exception:
        stb_addon = {"layer": "stb_ep724_rail_performance", "status": "skipped"}

    all_sctg = set(faf) | set(cfs) | set(SCTG_WIRE)
    nodes: list[dict[str, Any]] = []

    for sctg in all_sctg:
        label = SCTG2_LABELS.get(sctg, f"SCTG {sctg}")
        f = faf.get(sctg, {})
        c = cfs.get(sctg, {})
        carrier_n = carriers.get(sctg, 0)

        ties: list[dict] = []
        spec = SCTG_WIRE.get(sctg, {})
        for lane in spec.get("lanes", ()):
            ties.extend(insp_by_lane.get(lane, []))
        ties.sort(key=lambda x: x["inspection_count"], reverse=True)
        insp_total = sum(t["inspection_count"] for t in ties)

        faf_pct = f.get("pct_of_national_tons", 0)
        cfs_pct = c.get("pct_of_shipment_tons", 0)
        score = _transport_score(faf_pct, cfs_pct, carrier_n, insp_total)

        nodes.append(
            {
                "sctg": sctg,
                "commodity": label,
                "transport_score": score,
                "faf5": f or None,
                "cfs_2022": c or None,
                "fmcsa_carriers_certified": carrier_n,
                "inspection_tie_count": insp_total,
                "top_shipper_carrier_ties": ties[:5],
                "wiring": {
                    "faf5": bool(f),
                    "cfs": bool(c),
                    "fmcsa": carrier_n > 0,
                    "inspections": bool(ties),
                },
            }
        )

    nodes.sort(key=lambda n: n["transport_score"], reverse=True)

    csv_path = EXPORTS_DIR / "transport_economy_sctg_v1.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "sctg",
        "commodity",
        "transport_score",
        "faf5_thousand_tons",
        "faf5_pct",
        "cfs_million_tons",
        "cfs_billion_usd",
        "fmcsa_carriers",
        "inspection_ties",
        "top_shipper",
        "top_carrier",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for n in nodes:
            top = (n.get("top_shipper_carrier_ties") or [None])[0] or {}
            w.writerow(
                {
                    "sctg": n["sctg"],
                    "commodity": n["commodity"],
                    "transport_score": n["transport_score"],
                    "faf5_thousand_tons": (n.get("faf5") or {}).get("thousand_tons"),
                    "faf5_pct": (n.get("faf5") or {}).get("pct_of_national_tons"),
                    "cfs_million_tons": (n.get("cfs_2022") or {}).get("million_tons"),
                    "cfs_billion_usd": (n.get("cfs_2022") or {}).get("billion_usd"),
                    "fmcsa_carriers": n["fmcsa_carriers_certified"],
                    "inspection_ties": n["inspection_tie_count"],
                    "top_shipper": top.get("shipper"),
                    "top_carrier": top.get("carrier"),
                }
            )

    national_faf_kt = sum(v.get("thousand_tons", 0) for v in faf.values())
    receipt = {
        "scan_type": "transport_economy_v1",
        "algorithm": "sctg_spine_faf5_cfs_fmcsa_inspections",
        "as_of": utc_now()[:10],
        "thesis": (
            "Physical economy wired through transportation evidence: modeled flows (FAF5), "
            "shipment survey (CFS), operator registry (FMCSA), documented stops (MCMIS)."
        ),
        "spine_key": "SCTG",
        "sources": {
            "faf5": str(get_faf_csv().relative_to(ROOT)) if get_faf_csv().exists() else None,
            "cfs_2022": str(get_cfs_csv().relative_to(ROOT)) if get_cfs_csv().exists() else None,
            "fmcsa_census": str(get_fmcsa_census().relative_to(ROOT)) if get_fmcsa_census().exists() else None,
            "fmcsa_inspections": str(get_inspection_file().relative_to(ROOT)) if get_inspection_file().exists() else None,
            "source_truth": resolved_sources_dict(),
        },
        "national_totals": {
            "faf5_billion_tons": round(national_faf_kt / 1_000_000, 3),
            "cfs_commodity_codes": len(cfs),
            "sctg_nodes_wired": len(nodes),
        },
        "nodes": nodes,
        "top_10": nodes[:10],
        "export_csv": str(csv_path.relative_to(ROOT)),
        "commands": {
            "run": "bin/mabel-catalog transport-economy",
            "find_cargo": "bin/mabel-catalog find-cargo",
            "money_spider": "bin/mabel-catalog money-spider",
        },
        "next_layers": ["phmsa_pipeline", "shipper_name_normalization"],
        "stb_ep724_addon": stb_addon,
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} transport_economy_v1.json nodes={len(nodes)}",
    )
    return receipt
