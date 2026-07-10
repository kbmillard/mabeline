"""DTM guardrail tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from catalog.config import ROOT


def test_evidence_can_lose_100_percent():
    packs = ROOT / "exports" / "evidence_packs"
    if not packs.is_dir():
        return
    for risk in packs.glob("*/risk_flags.json"):
        data = json.loads(risk.read_text(encoding="utf-8"))
        assert data.get("can_lose_100_percent") is True


def test_dtm_opportunities_flag():
    csv_path = ROOT / "exports" / "dollar_to_million_opportunities_v1.csv"
    if not csv_path.exists():
        return
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            assert row.get("can_lose_100_percent") in ("True", "true", True)
