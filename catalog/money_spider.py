"""
Money Spider — one orchestrator connecting everything on disk into money threads.

Not another dashboard. One spider, many legs, three output types:
  1. B2B lead CSVs (FMCSA carriers × commodity lanes) — invoice tomorrow
  2. Market signal bundle (moneyball + matured pattern + freight public names)
  3. Master receipt with explicit edges (what connects to what)

Legs:
  physical    → commodity_economy_v1 (FAF5, CFS, PET, USGS)
  market      → moneyball_aggregate_v1 + return_scan_receipt_v1
  operators   → FMCSA company_census (carriers by cargo + fleet)
  inspections → MCMIS shipper→carrier→commodity lane ties
  pattern     → ARTV/UNFI matured references (what already ran)

Run: bin/mabel-catalog money-spider
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import duckdb

from catalog.cargo_inspection import run_cargo_inspection
from catalog.commodity_economy import run_commodity_economy
from catalog.config import BUILD_REPORTS, ROOT, UNWRAPPED, utc_now
from catalog.moneyball import aggregate_moneyball
from catalog.util import append_log, write_json

FMCSA_CENSUS = UNWRAPPED / "fmcsa_carriers" / "company_census.csv"
EXPORTS_DIR = ROOT / "exports"
RECEIPT_PATH = BUILD_REPORTS / "money_spider_v1.json"
FMCSA_CSV_OPTS = "header=true, ignore_errors=true"

COMMODITY_RECEIPT = BUILD_REPORTS / "commodity_economy_v1.json"
MONEYBALL_RECEIPT = BUILD_REPORTS / "moneyball_aggregate_v1.json"
RETURN_RECEIPT = BUILD_REPORTS / "return_scan_receipt_v1.json"

# Public names previously validated against freight/food/commodity lanes
FREIGHT_PUBLIC = {
    "UNFI": {"lane": "food_distribution", "commodity_sctg": "02", "note": "prior basket +103%"},
    "JBHT": {"lane": "truck_intermodal", "commodity_sctg": "31"},
    "ODFL": {"lane": "truck_ltl", "commodity_sctg": "31"},
    "KNX": {"lane": "truck", "commodity_sctg": "31"},
    "WERN": {"lane": "truck", "commodity_sctg": "31"},
    "XPO": {"lane": "truck_logistics", "commodity_sctg": "31"},
    "CHRW": {"lane": "broker", "commodity_sctg": "31"},
    "UPS": {"lane": "parcel", "commodity_sctg": "31"},
    "FDX": {"lane": "parcel_air", "commodity_sctg": "31"},
}

CARGO_THREAD_MAP = {
    "metal_scrap": {
        "label": "Metal & scrap haulers",
        "commodity": "Waste/scrap",
        "sctg": "41",
        "cargo_flags": ("CRGO_METALSHEET", "CRGO_GARBAGE", "CRGO_DRYBULK"),
        "inspection_lanes": ("metal_sheet", "waste_scrap"),
        "invoice_pattern": "norfolk_metal_leads",
    },
    "grain_feed": {
        "label": "Grain & feed carriers",
        "commodity": "Cereal grains",
        "sctg": "02",
        "cargo_flags": ("CRGO_GRAINFEED", "CRGO_FARMSUPP", "CRGO_PRODUCE"),
        "inspection_lanes": ("grain_feed",),
        "invoice_pattern": "ag_logistics_leads",
    },
    "petroleum": {
        "label": "Petroleum & chemical haulers",
        "commodity": "Petroleum products",
        "sctg": "17",
        "cargo_flags": ("CRGO_LIQGAS", "CRGO_CHEM", "CRGO_OILFIELD"),
        "inspection_lanes": ("petroleum_chem",),
        "invoice_pattern": "energy_logistics_leads",
    },
    "general_truck": {
        "label": "General freight (top fleet)",
        "commodity": "Mixed freight",
        "sctg": "31",
        "cargo_flags": ("CRGO_GENFREIGHT", "CRGO_INTERMODAL"),
        "inspection_lanes": ("general_freight",),
        "invoice_pattern": "freight_operator_leads",
    },
}


@dataclass
class SpiderLeg:
    leg_id: str
    source: str
    status: str
    node_count: int
    note: str = ""


@dataclass
class MoneyThread:
    thread_id: str
    label: str
    commodity: str
    physical_score: float
    carrier_lead_count: int
    public_tickers: list[str]
    moneyball_tickers: list[str]
    matured_reference: str | None
    spider_score: float
    invoiceable: str
    export_csv: str | None = None
    inspection_tie_count: int = 0
    inspection_export: str | None = None
    top_shipper_ties: list[dict] = field(default_factory=list)


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _carrier_leads(
    con: duckdb.DuckDBPyConnection,
    cargo_flags: tuple[str, ...],
    *,
    min_power_units: int = 20,
    limit: int = 200,
) -> list[dict[str, Any]]:
    if not FMCSA_CENSUS.exists():
        return []

    flag_sql = " OR ".join(f"UPPER(TRIM(COALESCE({f}, ''))) = 'X'" for f in cargo_flags)
    path = str(FMCSA_CENSUS)

    rows = con.execute(
        f"""
        SELECT
          DOT_NUMBER,
          LEGAL_NAME,
          DBA_NAME,
          PHY_CITY,
          PHY_STATE,
          TRY_CAST(POWER_UNITS AS INTEGER) AS power_units,
          PHONE,
          COMPANY_OFFICER_1,
          FLEETSIZE
        FROM read_csv_auto(?, {FMCSA_CSV_OPTS})
        WHERE ({flag_sql})
          AND TRY_CAST(POWER_UNITS AS INTEGER) >= ?
          AND LEGAL_NAME IS NOT NULL
          AND TRIM(LEGAL_NAME) != ''
        ORDER BY power_units DESC
        LIMIT ?
        """,
        [path, min_power_units, limit],
    ).fetchall()

    out = []
    for dot, legal, dba, city, state, pu, phone, officer, fleet in rows:
        out.append(
            {
                "dot_number": str(dot),
                "legal_name": legal,
                "dba_name": dba,
                "city": city,
                "state": state,
                "power_units": int(pu) if pu else 0,
                "phone": phone,
                "officer": officer,
                "fleet_size": fleet,
            }
        )
    return out


def _write_lead_csv(path: Path, leads: list[dict], thread_id: str, commodity: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "thread_id",
        "commodity_lane",
        "dot_number",
        "legal_name",
        "dba_name",
        "city",
        "state",
        "power_units",
        "phone",
        "officer",
        "fleet_size",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in leads:
            w.writerow(
                {
                    "thread_id": thread_id,
                    "commodity_lane": commodity,
                    **row,
                }
            )


def _physical_score_for_sctg(commodity: dict, sctg: str) -> float:
    for row in commodity.get("unified_commodity_slate", []):
        if str(row.get("sctg")) == sctg:
            return float(row.get("economy_score") or 0)
    return 0.0


def _moneyball_by_ticker(moneyball: dict) -> dict[str, dict]:
    return {str(r["ticker"]).upper(): r for r in moneyball.get("top", [])}


def run_money_spider(*, refresh_layers: bool = False) -> dict[str, Any]:
    t0 = time.monotonic()
    con = duckdb.connect()

    legs: list[SpiderLeg] = []

    if refresh_layers or not COMMODITY_RECEIPT.exists():
        commodity = run_commodity_economy()
    else:
        commodity = _load_json(COMMODITY_RECEIPT) or run_commodity_economy()
    legs.append(
        SpiderLeg(
            "physical",
            str(COMMODITY_RECEIPT.relative_to(ROOT)),
            "ok",
            len(commodity.get("unified_commodity_slate", [])),
            "FAF5+CFS+PET+USGS",
        )
    )

    if refresh_layers or not MONEYBALL_RECEIPT.exists():
        moneyball = aggregate_moneyball()
    else:
        moneyball = _load_json(MONEYBALL_RECEIPT) or aggregate_moneyball()
    legs.append(
        SpiderLeg(
            "market",
            str(MONEYBALL_RECEIPT.relative_to(ROOT)),
            "ok",
            moneyball.get("summary", {}).get("scored", 0),
            "penny moneyball slate",
        )
    )

    returns = _load_json(RETURN_RECEIPT)
    matured = None
    if returns:
        h = (returns.get("runs", {}).get("sanity_sec_scan_full") or {}).get("highest") or {}
        matured = h.get("ticker")
        basket = (returns.get("prior_validated_basket") or {}).get("highest") or {}
    legs.append(
        SpiderLeg(
            "pattern",
            str(RETURN_RECEIPT.relative_to(ROOT)) if returns else "missing",
            "ok" if returns else "missing",
            2 if returns else 0,
            f"matured={matured} freight_basket={basket.get('ticker') if returns else None}",
        )
    )

    carrier_count = 0
    if FMCSA_CENSUS.exists():
        carrier_count = con.execute(
            f"SELECT COUNT(*) FROM read_csv_auto(?, {FMCSA_CSV_OPTS})",
            [str(FMCSA_CENSUS)],
        ).fetchone()[0]
    legs.append(
        SpiderLeg(
            "operators",
            str(FMCSA_CENSUS.relative_to(ROOT)),
            "ok" if FMCSA_CENSUS.exists() else "missing",
            int(carrier_count),
            "FMCSA company census",
        )
    )

    inspection_summary = run_cargo_inspection(min_inspections=10, limit=2000)
    legs.append(
        SpiderLeg(
            "inspections",
            "build_reports/cargo_inspection_v1.json",
            "ok",
            inspection_summary["tie_count"],
            f"shipper_documented={inspection_summary['coverage']['documented_shipper']:,}",
        )
    )

    mb_map = _moneyball_by_ticker(moneyball)
    threads: list[MoneyThread] = []
    exports_written: list[str] = []

    for thread_id, spec in CARGO_THREAD_MAP.items():
        leads = _carrier_leads(con, spec["cargo_flags"])
        csv_name = f"spider_leads_{thread_id}_v1.csv"
        csv_path = EXPORTS_DIR / csv_name
        if leads:
            _write_lead_csv(csv_path, leads, thread_id, spec["commodity"])
            exports_written.append(str(csv_path.relative_to(ROOT)))

        phys = _physical_score_for_sctg(commodity, spec["sctg"])
        public = [t for t, meta in FREIGHT_PUBLIC.items() if meta.get("commodity_sctg") == spec["sctg"]]
        mb_overlap = [t for t in public if t in mb_map]

        matured_ref = None
        if thread_id == "grain_feed" and returns:
            matured_ref = (returns.get("prior_validated_basket") or {}).get("highest", {}).get("ticker")

        insp_ties: list[dict] = []
        insp_export = None
        for lane in spec.get("inspection_lanes", ()):
            lane_receipt = run_cargo_inspection(
                min_inspections=15,
                limit=150,
                lane=lane,
                export_name=f"spider_inspection_{thread_id}_{lane}_v1.csv",
            )
            insp_ties.extend(lane_receipt.get("top_ties", []))
            if lane_receipt.get("export_csv"):
                exports_written.append(lane_receipt["export_csv"])
                insp_export = Path(lane_receipt["export_csv"]).name

        insp_ties.sort(key=lambda x: x.get("inspection_count", 0), reverse=True)
        insp_count = sum(t.get("inspection_count", 0) for t in insp_ties[:50])

        lead_score = min(40, len(leads) / 5)
        insp_score = min(35, insp_count / 200)
        market_score = len(mb_overlap) * 15 + len(public) * 5
        spider_score = round(phys * 0.35 + lead_score + insp_score + market_score, 1)

        threads.append(
            MoneyThread(
                thread_id=thread_id,
                label=spec["label"],
                commodity=spec["commodity"],
                physical_score=phys,
                carrier_lead_count=len(leads),
                public_tickers=public,
                moneyball_tickers=mb_overlap,
                matured_reference=matured_ref,
                spider_score=spider_score,
                invoiceable=spec["invoice_pattern"],
                export_csv=csv_name if leads else None,
                inspection_tie_count=insp_count,
                inspection_export=insp_export,
                top_shipper_ties=insp_ties[:5],
            )
        )

    threads.sort(key=lambda t: t.spider_score, reverse=True)

    # Personal capital leg — moneyball names with commodity context (your trading thread)
    capital_signals = []
    for pick in moneyball.get("top", [])[:10]:
        capital_signals.append(
            {
                "ticker": pick["ticker"],
                "moneyball_score": pick["moneyball_score"],
                "price": pick["price_now"],
                "stake_for_100": pick.get("stake_needed_for_goal_usd"),
                "cent_zone": pick.get("cent_zone"),
                "leg": "market",
                "note": "pre-run screen; not advice",
            }
        )

    actions = []
    best_insp = max(threads, key=lambda t: t.inspection_tie_count, default=None)
    if best_insp and best_insp.inspection_export:
        top = best_insp.top_shipper_ties[0] if best_insp.top_shipper_ties else {}
        actions.append(
            {
                "priority": 1,
                "action": "sell_inspection_ties",
                "thread": best_insp.thread_id,
                "file": f"exports/{best_insp.inspection_export}",
                "count": best_insp.inspection_tie_count,
                "example": f"{top.get('shipper')} → {top.get('carrier_entity')}",
                "pitch": (
                    f"Documented shipper→carrier→commodity ties from FMCSA inspections "
                    f"({best_insp.label})"
                ),
            }
        )
    if threads and threads[0].export_csv:
        actions.append(
            {
                "priority": 2,
                "action": "sell_leads",
                "thread": threads[0].thread_id,
                "file": f"exports/{threads[0].export_csv}",
                "count": threads[0].carrier_lead_count,
                "pitch": f"{threads[0].carrier_lead_count} {threads[0].label} with phone/DOT — weekly refresh",
            }
        )
    if capital_signals:
        actions.append(
            {
                "priority": 3,
                "action": "personal_capital_watch",
                "tickers": [c["ticker"] for c in capital_signals[:3]],
                "leg": "market",
            }
        )
    if commodity.get("energy_snapshot", {}).get("crude_imports_by_origin"):
        actions.append(
            {
                "priority": 4,
                "action": "freight_intel_brief",
                "topic": "crude import origins + truck commodity share",
                "source": "commodity_economy_v1",
            }
        )

    receipt = {
        "scan_type": "money_spider_v1",
        "as_of": utc_now()[:10],
        "story": (
            "One spider: physical economy + FMCSA operators + inspection shipper ties "
            "+ moneyball market screen + matured patterns. "
            "Sell inspection CSVs (shipper→carrier→commodity). Sell carrier leads. "
            "Watch market leg."
        ),
        "legs": [asdict(l) for l in legs],
        "inspection_coverage": inspection_summary.get("coverage"),
        "threads": [asdict(t) for t in threads],
        "capital_signals": capital_signals,
        "actions_today": actions,
        "matured_pattern": {
            "biotech_runner": matured,
            "freight_food_runner": (returns or {}).get("prior_validated_basket", {}).get("highest"),
            "lesson": "ARTV matured on market leg; UNFI on freight/food; spider hunts pre-run + sells operator leads",
        },
        "exports": exports_written,
        "commands": {
            "run": "bin/mabel-catalog money-spider",
            "refresh_all": "bin/mabel-catalog money-spider --refresh",
            "find_cargo": "bin/mabel-catalog find-cargo",
            "financial": "bin/mabel-catalog financial",
        },
        "dedupe_method": "thread_unique_carrier_dot_rank",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} money_spider_v1.json threads={len(threads)} exports={len(exports_written)}",
    )
    return receipt
