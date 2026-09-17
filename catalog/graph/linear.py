"""Linear vertical slice: schema → build → baseline → radar → dtm."""

from __future__ import annotations

from typing import Any

from catalog.graph.iran_oil import build_iran_oil_receipt
from catalog.graph.temporal_baseline import run_temporal_baseline
from catalog.graph.thg_builder import run_thg_build
from catalog.signals.dollar_to_million import run_dollar_to_million
from catalog.signals.market_trend_radar import run_market_trend_radar


def run_thg_linear(*, from_month: str = "202401", min_stops: int = 2, top_n: int = 50) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    build = run_thg_build(from_month=from_month, min_stops=min_stops)
    steps.append({"step": "thg-build", "events": build["row_counts"].get("events", 0)})

    baseline = run_temporal_baseline()
    steps.append({"step": "thg-baseline", "scores": baseline["row_counts"].get("change_scores", 0)})

    iran = build_iran_oil_receipt()
    steps.append({"step": "iran-oil", "join": iran.get("join"), "eia_last": iran["eia_iran"].get("last_month")})

    radar = run_market_trend_radar()
    steps.append({"step": "market-trend-radar", "trends": radar["row_counts"].get("trends", 0)})

    dtm = run_dollar_to_million(top_n=top_n)
    steps.append({"step": "dollar-to-million", "opportunities": dtm["row_counts"].get("opportunities", 0)})

    return {
        "scan_type": "thg_linear_v1",
        "steps": steps,
        "build": build,
        "baseline": baseline,
        "iran_oil": iran,
        "radar": radar,
        "dtm": dtm,
    }
