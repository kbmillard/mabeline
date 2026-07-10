"""
Movement intelligence cards — JSON-first schema for facility/company/lane/opportunity.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.shipper_carriers import run_dollar_general_carriers
from catalog.source_truth import resolved_sources_dict
from catalog.util import write_json

CARDS_DIR = BUILD_REPORTS / "intelligence_cards"
SCHEMA_VERSION = "movement_intelligence_card_v1"


def _evidence(
    *,
    source_family: str,
    path: str,
    row_count: int | None = None,
    query_count: int | None = None,
    confidence: str,
) -> dict[str, Any]:
    return {
        "source_family": source_family,
        "path": path,
        "row_count": row_count,
        "query_count": query_count,
        "confidence": confidence,
    }


def build_sample_cards(*, dg_receipt: dict | None = None) -> dict[str, Any]:
    """Emit first JSON cards from compiler pass proof artifacts."""
    if dg_receipt is None:
        dg_receipt = run_dollar_general_carriers()

    sources = resolved_sources_dict()
    cards: list[dict[str, Any]] = []

    # Company card — Dollar General carrier ecosystem
    cards.append(
        {
            "schema": SCHEMA_VERSION,
            "card_type": "company_card",
            "entity": {"name": "Dollar General", "entity_class": "shipper"},
            "summary": (
                f"{dg_receipt['distinct_carriers']} distinct motor carriers documented "
                f"hauling for Dollar General on FMCSA inspection stops."
            ),
            "evidence": [
                _evidence(
                    source_family="fmcsa_carriers",
                    path=sources.get("fmcsa_inspections", ""),
                    row_count=None,
                    query_count=dg_receipt["distinct_carriers"],
                    confidence="high — inspection SHIPPER_NAME match",
                ),
            ],
            "market_implication": (
                "Retail general freight lane is competitively served by dedicated and asset carriers; "
                "useful for carrier sales, lane capacity, and retail logistics intelligence."
            ),
            "next_action": "Normalize shipper aliases; export top lanes by state",
            "created_at": utc_now(),
        }
    )

    # Lane card — general freight from transport spine
    mc_path = BUILD_REPORTS / "moving_commodity_v1.json"
    lane_summary = "General freight / mixed retail logistics dominates inspection-documented ties"
    if mc_path.exists():
        mc = json.loads(mc_path.read_text(encoding="utf-8"))
        top = (mc.get("top_10") or mc.get("moving_a_lot") or [])[:1]
        if top:
            lane_summary = (
                f"Top moving commodity SCTG {top[0].get('sctg')} {top[0].get('commodity')}: "
                f"score {top[0].get('moving_a_lot_score')}"
            )

    cards.append(
        {
            "schema": SCHEMA_VERSION,
            "card_type": "lane_card",
            "entity": {"lane": "general_freight", "sctg_hint": "31"},
            "summary": lane_summary,
            "evidence": [
                _evidence(
                    source_family="faf5_freight",
                    path=sources.get("faf5_csv", ""),
                    confidence="medium — modeled national flow, not stop-level",
                ),
                _evidence(
                    source_family="fmcsa_carriers",
                    path=sources.get("fmcsa_inspections", ""),
                    confidence="high — documented shipper stops",
                ),
            ],
            "market_implication": "Retail-driven truck demand; inspection ties outperform census CRGO flags",
            "next_action": "Wire shipper normalization; add corridor OD from FAF5",
            "created_at": utc_now(),
        }
    )

    # Facility card — proof template (Kill Creek example from prior research)
    cards.append(
        {
            "schema": SCHEMA_VERSION,
            "card_type": "facility_card",
            "entity": {
                "address": "18905 Kill Creek Rd, Edgerton, KS 66021",
                "operator": "Smart Warehousing LLC",
                "naics_hint": "493110",
            },
            "summary": "Class-A warehouse at LPKC; OSHA inspection 2024 with documented violations",
            "evidence": [
                _evidence(
                    source_family="osha_enforcement",
                    path="_unwrapped/osha_enforcement/",
                    query_count=1,
                    confidence="high — exact-address OSHA IMIS 1783117.015",
                ),
            ],
            "market_implication": "Intermodal-adjacent warehousing with regulatory exposure; verify tenant churn",
            "next_action": "Pull Johnson County APN deed; join FMCSA shippers near corridor",
            "created_at": utc_now(),
        }
    )

    # Opportunity card — Jul 9 source refresh
    cards.append(
        {
            "schema": SCHEMA_VERSION,
            "card_type": "opportunity_card",
            "entity": {"opportunity": "wire_release_2026_07_09_spine"},
            "summary": "PET imports, EIA coal, STB EP724 on disk ahead of catalog receipts — compiler pass wires resolver",
            "evidence": [
                _evidence(
                    source_family="maritime",
                    path=sources.get("pet_imports", ""),
                    confidence="high — source truth selected",
                ),
                _evidence(
                    source_family="rail",
                    path=sources.get("eia_coal", ""),
                    confidence="high — source truth selected",
                ),
                _evidence(
                    source_family="stb_rail",
                    path=sources.get("stb_ep724_public", ""),
                    row_count=None,
                    confidence="high — 1.43M row EP724 staged",
                ),
            ],
            "market_implication": "Newest energy and rail performance layers ready for commodity spine refresh",
            "next_action": "Re-run transport-economy; add EP724 rail addon to receipts",
            "created_at": utc_now(),
        }
    )

    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for i, card in enumerate(cards):
        fname = f"{card['card_type']}_{i + 1}_v1.json"
        dest = CARDS_DIR / fname
        write_json(dest, card)
        written.append(str(dest.relative_to(ROOT)))

    manifest = {
        "scan_type": "movement_intelligence_cards_manifest_v1",
        "schema": SCHEMA_VERSION,
        "card_count": len(cards),
        "cards": written,
        "created_at": utc_now(),
    }
    write_json(CARDS_DIR / "manifest_v1.json", manifest)
    return manifest
