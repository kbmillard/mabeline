"""
Full commodity economy aggregate — physical flows from on-disk national sources.

Layers (all local, no API):
  - FAF5.7.1 modeled freight by SCTG2, mode, corridor (2024)
  - Census CFS 2022 PUMS shipment weights/values by SCTG and sector
  - EIA PET_IMPORTS maritime crude import flows by origin region
  - USGS MRDS mineral deposit inventory by commodity

Produces a unified commodity slate ranking physical-economy weight across layers.
NOT live commodity prices, futures, or company-level ledgers.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.freight_movement import SCTG2_LABELS, get_faf_csv, run_freight_movement
from catalog.source_truth import require_path, resolved_sources_dict
from catalog.util import append_log, write_json

RECEIPT_PATH = BUILD_REPORTS / "commodity_economy_v1.json"


def get_cfs_csv() -> Path:
    return require_path("cfs_2022_pums")


def get_usgs_commodity() -> Path:
    return require_path("usgs_commodity")


def get_pet_imports() -> Path:
    return require_path("pet_imports")


def get_census_trade_imports() -> Path | None:
    from catalog.source_truth import resolve_path

    p = resolve_path("census_hs_trade")
    return p

# CFS sector = NAICS-ish 2-digit ranges in survey
SECTOR_LABELS = {
    "11": "Agriculture",
    "21": "Mining",
    "22": "Utilities",
    "23": "Construction",
    "31-33": "Manufacturing",
    "42": "Wholesale trade",
    "44-45": "Retail trade",
    "48-49": "Transportation & warehousing",
    "51": "Information",
    "52": "Finance",
    "53": "Real estate",
    "54": "Professional services",
    "56": "Administrative services",
    "61": "Education",
    "62": "Health care",
    "71": "Arts & entertainment",
    "72": "Accommodation & food",
    "81": "Other services",
    "92": "Public administration",
}

ORIGIN_REGION_LABELS = {
    "REG_CA": "Canada",
    "REG_MX": "Mexico",
    "REG_SA": "South America",
    "REG_ME": "Middle East",
    "REG_AF": "Africa",
    "REG_EU": "Europe",
    "REG_OA": "Other Americas",
    "REG_AP": "Asia-Pacific",
    "WORLD": "World total",
}


def _sctg_label(code: str | None) -> str:
    if not code:
        return "unknown"
    s = str(code).zfill(2)[:2]
    return SCTG2_LABELS.get(s, f"SCTG {s}")


def _layer_status(path: Path) -> dict[str, Any]:
    if path.exists():
        return {"status": "present", "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size}
    return {"status": "missing", "path": str(path.relative_to(ROOT))}


def _analyze_faf5(con: duckdb.DuckDBPyConnection, year: str) -> dict[str, Any]:
    tons_col = f"tons_{year}"
    path = str(get_faf_csv())

    by_commodity = con.execute(
        f"""
        SELECT sctg2,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons
        FROM read_csv_auto(?, header=true)
        GROUP BY 1 ORDER BY 2 DESC
        """,
        [path],
    ).fetchall()

    total_kt = sum(float(t) for _, t in by_commodity if t)
    top = [
        {
            "sctg2": s,
            "commodity": _sctg_label(s),
            "thousand_tons": float(t),
            "pct_of_tons": round(100.0 * float(t) / total_kt, 2) if total_kt else 0,
        }
        for s, t in by_commodity[:20]
        if s
    ]

    commodity_mode = con.execute(
        f"""
        SELECT sctg2, dms_mode,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons
        FROM read_csv_auto(?, header=true)
        WHERE sctg2 IN (SELECT sctg2 FROM (
          SELECT sctg2, SUM(TRY_CAST({tons_col} AS DOUBLE)) t
          FROM read_csv_auto(?, header=true) GROUP BY 1 ORDER BY t DESC LIMIT 8
        ))
        GROUP BY 1, 2 ORDER BY 1, 3 DESC
        """,
        [path, path],
    ).fetchall()

    mode_map = {"1": "Truck", "2": "Rail", "3": "Water", "4": "Air", "5": "Multiple", "6": "Pipeline", "7": "Other"}
    by_commodity_mode: dict[str, list] = {}
    for sctg, mode, kt in commodity_mode:
        key = _sctg_label(sctg)
        by_commodity_mode.setdefault(key, []).append(
            {"mode": mode_map.get(str(mode), str(mode)), "thousand_tons": float(kt)}
        )

    return {
        "layer": "faf5_freight",
        "year": year,
        "total_thousand_tons": round(total_kt, 2),
        "billion_tons_equiv": round(total_kt / 1_000_000, 3),
        "top_commodities": top,
        "top_commodity_modes": by_commodity_mode,
    }


def _analyze_cfs(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    path = str(get_cfs_csv())
    totals = con.execute(
        """
        SELECT COUNT(*)::BIGINT AS shipments,
          ROUND(SUM(TRY_CAST(SHIPMT_WGHT AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e6, 2) AS million_tons,
          ROUND(SUM(TRY_CAST(SHIPMT_VALUE AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e9, 2) AS billion_usd
        FROM read_csv_auto(?, header=true)
        """,
        [path],
    ).fetchone()

    by_sctg = con.execute(
        """
        SELECT SCTG,
          ROUND(SUM(TRY_CAST(SHIPMT_WGHT AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e6, 2) AS million_tons,
          ROUND(SUM(TRY_CAST(SHIPMT_VALUE AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e9, 2) AS billion_usd
        FROM read_csv_auto(?, header=true)
        GROUP BY 1 ORDER BY 2 DESC LIMIT 20
        """,
        [path],
    ).fetchall()

    by_sector = con.execute(
        """
        SELECT SECTOR,
          ROUND(SUM(TRY_CAST(SHIPMT_WGHT AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e6, 2) AS million_tons,
          ROUND(SUM(TRY_CAST(SHIPMT_VALUE AS DOUBLE)*TRY_CAST(WGT_FACTOR AS DOUBLE))/1e9, 2) AS billion_usd
        FROM read_csv_auto(?, header=true)
        GROUP BY 1 ORDER BY 3 DESC LIMIT 15
        """,
        [path],
    ).fetchall()

    total_mt = float(totals[1]) if totals[1] else 0
    return {
        "layer": "census_cfs_2022",
        "survey_year": 2022,
        "shipments": int(totals[0]),
        "million_tons_weighted": total_mt,
        "billion_usd_value_weighted": float(totals[2]),
        "by_sctg": [
            {
                "sctg": s,
                "commodity": _sctg_label(s),
                "million_tons": float(mt),
                "billion_usd": float(usd),
                "pct_of_tons": round(100.0 * float(mt) / total_mt, 2) if total_mt else 0,
            }
            for s, mt, usd in by_sctg
        ],
        "by_sector": [
            {
                "sector": sec,
                "label": SECTOR_LABELS.get(str(sec), str(sec)),
                "million_tons": float(mt),
                "billion_usd": float(usd),
            }
            for sec, mt, usd in by_sector
        ],
    }


def _analyze_usgs(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    path = str(get_usgs_commodity())
    rows = con.execute(
        """
        SELECT commod, commod_group, commod_tp,
          COUNT(DISTINCT dep_id)::BIGINT AS deposit_sites
        FROM read_csv_auto(?, header=true, delim='\t', quote='"')
        GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 25
        """,
        [path],
    ).fetchall()

    total = con.execute(
        """
        SELECT COUNT(DISTINCT dep_id)::BIGINT FROM read_csv_auto(?, header=true, delim='\t', quote='"')
        """,
        [path],
    ).fetchone()[0]

    by_type = con.execute(
        """
        SELECT commod_tp, COUNT(DISTINCT dep_id)::BIGINT n
        FROM read_csv_auto(?, header=true, delim='\t', quote='"')
        GROUP BY 1 ORDER BY 2 DESC
        """,
        [path],
    ).fetchall()

    return {
        "layer": "usgs_mrds_minerals",
        "distinct_deposit_sites": int(total),
        "top_commodities": [
            {
                "commodity": c,
                "group": g,
                "type": t,
                "deposit_sites": int(n),
            }
            for c, g, t, n in rows
        ],
        "by_mineral_type": [{"type": t, "deposit_sites": int(n)} for t, n in by_type],
    }


def _parse_pet_imports() -> dict[str, Any]:
    pet = get_pet_imports()
    if not pet.exists():
        return {"layer": "petroleum_imports", "status": "missing"}

    region_series: dict[str, dict] = {}
    world_total = None

    with pet.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = obj.get("series_id", "")
            if not sid.endswith("-US-ALL.M"):
                continue
            m = re.match(r"PET_IMPORTS\.(REG_[A-Z]{2}|WORLD)-US-ALL\.M", sid)
            if not m:
                continue
            region_key = m.group(1)
            data = obj.get("data") or []
            if not data:
                continue
            latest = data[0]
            prior = data[1] if len(data) > 1 else None
            entry = {
                "region": ORIGIN_REGION_LABELS.get(region_key, region_key),
                "region_code": region_key,
                "latest_month": latest[0],
                "thousand_barrels": int(latest[1]),
                "prior_month_kbbl": int(prior[1]) if prior else None,
                "units": obj.get("units", "thousand barrels"),
            }
            if region_key == "WORLD":
                world_total = entry
            else:
                region_series[region_key] = entry

    origins = sorted(region_series.values(), key=lambda x: x["thousand_barrels"], reverse=True)
    return {
        "layer": "petroleum_imports",
        "source": str(pet.relative_to(ROOT)),
        "product": "crude oil imports to Total U.S.",
        "latest_month": world_total["latest_month"] if world_total else None,
        "world_total_kbbl": world_total["thousand_barrels"] if world_total else None,
        "by_origin_region": origins,
        "note": "EIA PET_IMPORTS via maritime release; monthly thousand barrels",
    }


def _build_unified_slate(faf: dict, cfs: dict, usgs: dict) -> list[dict]:
    """Rank commodities by combined physical-economy signal (FAF tonnage + CFS weight)."""
    faf_by_sctg = {str(r["sctg2"]).zfill(2)[:2]: r for r in faf.get("top_commodities", [])}
    cfs_by_sctg = {str(r["sctg"]).zfill(2)[:2]: r for r in cfs.get("by_sctg", [])}

    all_codes = set(faf_by_sctg) | set(cfs_by_sctg)
    slate = []
    for code in all_codes:
        f = faf_by_sctg.get(code, {})
        c = cfs_by_sctg.get(code, {})
        faf_pct = float(f.get("pct_of_tons") or 0)
        cfs_pct = float(c.get("pct_of_tons") or 0)
        economy_score = round(faf_pct * 0.55 + cfs_pct * 0.45, 2)
        modes = faf.get("top_commodity_modes", {}).get(_sctg_label(code), [])
        primary_mode = modes[0]["mode"] if modes else None
        slate.append(
            {
                "sctg": code,
                "commodity": _sctg_label(code),
                "economy_score": economy_score,
                "faf5_thousand_tons": f.get("thousand_tons"),
                "faf5_pct": faf_pct or None,
                "cfs_million_tons": c.get("million_tons"),
                "cfs_billion_usd": c.get("billion_usd"),
                "cfs_pct": cfs_pct or None,
                "primary_mode": primary_mode,
            }
        )

    slate.sort(key=lambda x: x["economy_score"], reverse=True)
    return slate[:25]


def run_commodity_economy(*, faf_year: str = "2024", refresh_faf_receipt: bool = False) -> dict[str, Any]:
    t0 = time.monotonic()
    gaps: list[str] = []
    layers: dict[str, Any] = {}

    faf = get_faf_csv()
    cfs = get_cfs_csv()
    usgs = get_usgs_commodity()
    census_trade = get_census_trade_imports()

    if refresh_faf_receipt and faf.exists():
        run_freight_movement(year=faf_year)

    con = duckdb.connect()

    if faf.exists():
        layers["faf5"] = _analyze_faf5(con, faf_year)
    else:
        gaps.append("faf5_freight missing")

    if cfs.exists():
        layers["cfs_2022"] = _analyze_cfs(con)
    else:
        gaps.append("census_cfs_2022 missing")

    if usgs.exists():
        layers["usgs_minerals"] = _analyze_usgs(con)
    else:
        gaps.append("usgs_mrds missing")

    layers["petroleum"] = _parse_pet_imports()
    if layers["petroleum"].get("status") == "missing":
        gaps.append("petroleum_imports missing")

    if census_trade and census_trade.exists():
        text = census_trade.read_text(encoding="utf-8")[:200]
        if "Missing Key" in text or "<html>" in text:
            gaps.append("census_hs_trade requires API key; not loaded")
            layers["census_trade"] = {"layer": "census_hs_trade", "status": "deferred", "reason": "API key missing"}
        else:
            layers["census_trade"] = {"layer": "census_hs_trade", "status": "present"}

    unified = _build_unified_slate(
        layers.get("faf5", {}),
        layers.get("cfs_2022", {}),
        layers.get("usgs_minerals", {}),
    )

    physical = {
        "faf5_billion_tons": layers.get("faf5", {}).get("billion_tons_equiv"),
        "cfs_million_tons": layers.get("cfs_2022", {}).get("million_tons_weighted"),
        "cfs_billion_usd_shipment_value": layers.get("cfs_2022", {}).get("billion_usd_value_weighted"),
        "usgs_deposit_sites": layers.get("usgs_minerals", {}).get("distinct_deposit_sites"),
        "crude_imports_kbbl_latest": layers.get("petroleum", {}).get("world_total_kbbl"),
    }

    receipt = {
        "scan_type": "commodity_economy_v1",
        "algorithm": "aggregate_physical_commodity_layers",
        "as_of": utc_now()[:10],
        "what_this_is": (
            "Unified physical commodity economy from FAF5 freight, Census CFS shipments, "
            "EIA crude import flows, and USGS mineral deposit inventory."
        ),
        "what_this_is_not": [
            "Live commodity futures or spot prices",
            "Company revenue or inventory ledgers",
            "Real-time port/rail telemetry",
        ],
        "sources": {
            "faf5": _layer_status(faf),
            "cfs_2022": _layer_status(cfs),
            "usgs_commodity": _layer_status(usgs),
            "pet_imports": _layer_status(get_pet_imports()),
            "census_trade": _layer_status(census_trade) if census_trade and census_trade.exists() else {"status": "missing"},
            "source_truth": resolved_sources_dict(),
        },
        "physical_economy_totals": physical,
        "layers": layers,
        "unified_commodity_slate": unified,
        "energy_snapshot": {
            "top_freight_commodity": unified[0] if unified else None,
            "pipeline_share_faf5_pct": next(
                (m["pct_of_tons"] for m in layers.get("faf5", {}).get("top_commodities", []) if m.get("sctg2") == "16"),
                None,
            ),
            "crude_imports_by_origin": layers.get("petroleum", {}).get("by_origin_region", [])[:6],
        },
        "gaps": gaps,
        "dedupe_method": "aggregate_sum_by_sctg_and_region",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} commodity_economy_v1.json status=ok slate={len(unified)}",
    )
    return receipt
