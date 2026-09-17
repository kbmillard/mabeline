"""Validation for Mabeline signal pipeline."""

from __future__ import annotations

import csv
from pathlib import Path

from catalog.config import BUILD_REPORTS, ROOT

REQUIRED_TRUCK_COLS = {
    "signal_id", "dot_number", "carrier_name", "shipper_name", "commodity_inferred",
    "sctg2", "commodity_confidence", "market_signal_score", "evidence_strength",
}
REQUIRED_OPP_COLS = {
    "opportunity_id", "asymmetry_score", "can_lose_100_percent", "risk_score",
    "evidence_files", "repro_query_path", "notes",
}
BANNED_PHRASES = ("buy now", "sell now", "strong buy", "strong sell", "hold recommendation")


def validate_outputs() -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    truck = ROOT / "exports" / "commodity_truck_signal_v1.csv"
    radar = ROOT / "exports" / "market_trend_radar_v1.csv"
    opp = ROOT / "exports" / "dollar_to_million_opportunities_v1.csv"

    for path in (truck, radar, opp):
        if not path.exists():
            errors.append(f"missing:{path.name}")

    if truck.exists():
        with truck.open(encoding="utf-8") as fh:
            cols = set(csv.DictReader(fh).fieldnames or [])
        missing = REQUIRED_TRUCK_COLS - cols
        if missing:
            errors.append(f"truck_missing_cols:{missing}")

    if opp.exists():
        with opp.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            cols = set(reader.fieldnames or [])
            miss = REQUIRED_OPP_COLS - cols
            if miss:
                errors.append(f"opp_missing_cols:{miss}")
            for row in reader:
                if str(row.get("can_lose_100_percent", "")).lower() not in ("true", "1", "yes"):
                    errors.append("opp_missing_can_lose_100")
                    break
                text = " ".join(str(v) for v in row.values()).lower()
                if any(p in text for p in BANNED_PHRASES):
                    errors.append("opp_contains_banned_recommendation_language")
                    break

    packs = ROOT / "exports" / "evidence_packs"
    if not packs.is_dir() or not any(packs.iterdir()):
        warnings.append("no_evidence_packs")

    return {"errors": errors, "warnings": warnings, "ok": not errors}


def run_validation() -> int:
    result = validate_outputs()
    out = BUILD_REPORTS / "signal_validation_v1.json"
    import json

    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["ok"] else 1
