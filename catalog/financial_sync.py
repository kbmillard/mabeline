"""
Sync build_reports receipts into the financial/ Next.js dashboard.

Copies and normalizes penny, moneyball, freight, and return-scan JSON so the
dashboard can import them from src/data/ without manual cp steps.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.util import append_log, write_json

FINANCIAL_ROOT = ROOT / "financial"
SRC_DATA = FINANCIAL_ROOT / "src" / "data"
PUBLIC_DATA = FINANCIAL_ROOT / "public" / "data"

RECEIPT_SOURCES: dict[str, Path] = {
    "return_scan_receipt_v1.json": BUILD_REPORTS / "return_scan_receipt_v1.json",
    "penny_forward_screen_v1.json": BUILD_REPORTS / "penny_forward_screen_v1.json",
    "moneyball_aggregate_v1.json": BUILD_REPORTS / "moneyball_aggregate_v1.json",
    "moneyball_supplements_v1.json": BUILD_REPORTS / "moneyball_supplements_v1.json",
    "dollar_to_million_playbook_v1.json": BUILD_REPORTS / "dollar_to_million_playbook_v1.json",
    "market_scan_returns_v1.json": BUILD_REPORTS / "market_scan_returns_v1.json",
    "penny_forward_full_v1.json": BUILD_REPORTS / "penny_forward_full_v1.json",
    "moneyball_price_refresh_v1.json": BUILD_REPORTS / "moneyball_price_refresh_v1.json",
    "freight_movement_receipt_v1.json": BUILD_REPORTS / "freight_movement_receipt_v1.json",
    "commodity_economy_v1.json": BUILD_REPORTS / "commodity_economy_v1.json",
    "transport_economy_v1.json": BUILD_REPORTS / "transport_economy_v1.json",
    "moving_commodity_v1.json": BUILD_REPORTS / "moving_commodity_v1.json",
    "money_spider_v1.json": BUILD_REPORTS / "money_spider_v1.json",
    "thg_iran_oil_v1.json": BUILD_REPORTS / "thg_iran_oil_v1.json",
}

SYNC_RECEIPT = BUILD_REPORTS / "financial_sync_receipt_v1.json"


def _load(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_penny_for_dashboard(raw: dict) -> dict:
    """Map candidates (legacy) or top (3-phase) into dashboard PennyForwardReceipt shape."""
    rows = raw.get("top") or raw.get("candidates") or []
    top = []
    for i, row in enumerate(rows):
        px = row.get("px") or row.get("price_now")
        upside = row.get("upside_pct") or row.get("proj_upside_pct")
        score = row.get("score")
        if score is None and upside is not None:
            score = float(upside) / 100.0
        if score is None:
            score = max(0.0, 100.0 - i)
        top.append(
            {
                "ticker": row.get("ticker", ""),
                "name": row.get("name", ""),
                "px": float(px) if px is not None else 0.0,
                "score": float(score),
                "ret_1y": float(row.get("ret_1y") or 0),
                "ret_3m": float(row.get("ret_3m") or 0),
                "upside_pct": float(upside) if upside is not None else None,
                "sector": row.get("sector"),
                "exchange": row.get("exchange"),
            }
        )
    return {
        "scan_type": raw.get("scan_type", "penny_forward_screen_v1"),
        "as_of": raw.get("as_of") or raw.get("created_at", "")[:10],
        "survivor_count": raw.get("survivor_count") or len(rows),
        "top_k": raw.get("top_k") or len(top),
        "method": raw.get("method", ""),
        "elapsed_sec": raw.get("elapsed_sec"),
        "top": top,
        "artv_reference": raw.get("artv_reference"),
        "algorithm": raw.get("algorithm"),
    }


def sync_financial_dashboard(*, normalize_penny: bool = True) -> dict[str, Any]:
    if not FINANCIAL_ROOT.is_dir():
        raise FileNotFoundError(f"financial app not found: {FINANCIAL_ROOT}")

    SRC_DATA.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)

    copied: list[dict[str, Any]] = []
    missing: list[str] = []

    for name, src in RECEIPT_SOURCES.items():
        if not src.exists():
            missing.append(name)
            continue

        payload: dict | str
        if name == "penny_forward_screen_v1.json" and normalize_penny:
            raw = _load(src)
            payload = normalize_penny_for_dashboard(raw or {})
        else:
            payload = json.loads(src.read_text(encoding="utf-8"))

        for dest_root in (SRC_DATA, PUBLIC_DATA):
            dest = dest_root / name
            dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        copied.append({"file": name, "bytes": src.stat().st_size, "source": str(src.relative_to(ROOT))})

    receipt = {
        "scan_type": "financial_sync_v1",
        "status": "ok" if copied else "partial",
        "destinations": [str(SRC_DATA.relative_to(ROOT)), str(PUBLIC_DATA.relative_to(ROOT))],
        "copied": copied,
        "missing": missing,
        "created_at": utc_now(),
    }
    write_json(SYNC_RECEIPT, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} financial_sync_receipt_v1.json copied={len(copied)} missing={len(missing)}",
    )
    return receipt


def run_financial_pipeline(
    *,
    run_screen: bool = False,
    screen_cfg: Any = None,
    moneyball_cfg: Any = None,
) -> dict[str, Any]:
    """forward-screen (optional) → moneyball → sync-financial."""
    from catalog.commodity_economy import run_commodity_economy
    from catalog.forward_screen import ScreenConfig, run_forward_screen
    from catalog.moneyball import MoneyballConfig, aggregate_moneyball
    from catalog.transport_economy import run_transport_economy
    from catalog.moving_commodity import run_moving_commodity

    steps: list[dict[str, Any]] = []

    if run_screen:
        cfg = screen_cfg or ScreenConfig()
        penny = run_forward_screen(cfg)
        steps.append({"step": "forward-screen", "survivors": penny.get("survivor_count")})
    else:
        steps.append({"step": "forward-screen", "skipped": True})

    te = run_transport_economy()
    steps.append({"step": "transport-economy", "nodes": len(te["nodes"])})

    mc = run_moving_commodity()
    steps.append({"step": "moving-commodity", "tied": mc["count"], "top": mc["top_10"][0]["commodity"] if mc["top_10"] else None})

    ce = run_commodity_economy()
    steps.append(
        {
            "step": "commodity-economy",
            "slate": len(ce["unified_commodity_slate"]),
            "gaps": ce["gaps"],
        }
    )

    from catalog.moneyball import write_dollar_to_million_playbook

    mb_cfg = moneyball_cfg or MoneyballConfig()
    mb = aggregate_moneyball(mb_cfg)
    steps.append(
        {
            "step": "moneyball",
            "scored": mb["summary"]["scored"],
            "cent_zone": mb["summary"]["cent_zone_count"],
        }
    )

    playbook = write_dollar_to_million_playbook(moneyball=mb, cfg=mb_cfg)
    steps.append(
        {
            "step": "dollar-to-million-playbook",
            "goal_usd": playbook.get("goal_usd"),
            "stock_paths": len(playbook.get("paths", {}).get("sec_penny_stocks", {}).get("stock_paths_from_moneyball", [])),
        }
    )

    sync = sync_financial_dashboard()
    steps.append({"step": "sync-financial", "copied": len(sync["copied"]), "missing": sync["missing"]})

    receipt = {
        "scan_type": "financial_pipeline_v1",
        "status": "ok",
        "steps": steps,
        "created_at": utc_now(),
    }
    write_json(BUILD_REPORTS / "financial_pipeline_receipt_v1.json", receipt)
    append_log(ROOT / "reports" / "build_status.log", f"{utc_now()} financial_pipeline_v1.json status=ok")
    return receipt
