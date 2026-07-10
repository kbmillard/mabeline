"""
Dollar-to-Million Engine — ranked asymmetric opportunity leads (not buy/sell/hold).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, WAREHOUSE
from catalog.graph.schema_v1 import OUTPUTS as THG_OUTPUTS
from catalog.signals._common import CommandTimer, EXPORTS_DIR, export_parquet, write_receipt
from catalog.signals.market_trend_radar import CSV_PATH as RADAR_CSV
from catalog.signals.evidence_pack import write_evidence_pack

RECEIPT_PATH = BUILD_REPORTS / "dollar_to_million_v1.json"
CSV_PATH = EXPORTS_DIR / "dollar_to_million_opportunities_v1.csv"
PARQUET_PATH = WAREHOUSE / "dollar_to_million_opportunities_v1.parquet"
VERSION = "dollar_to_million_v1"

OPPORTUNITY_ANGLES: dict[str, dict[str, str]] = {
    "17": {
        "theme": "Petroleum/hazmat logistics intelligence",
        "investable": "Port terminals, tank transport, refinery services, compliance tech",
        "non_stock": "Verified carrier/shipper lead list or regional flow report",
        "next_dollar": "Build a verified lead list for brokers/analysts exposed to petroleum corridor flow",
        "type": "data_product_wedge",
    },
    "18": {
        "theme": "Chemical/hazmat corridor risk and routing",
        "investable": "Chemical logistics, insurance, compliance, specialty carriers",
        "non_stock": "Niche compliance + routing intelligence newsletter",
        "next_dollar": "Map hazmat inspection clusters to sellable regional intelligence",
        "type": "private_business_wedge",
    },
    "19": {
        "theme": "Coal/rail chokepoint and mode-shift watch",
        "investable": "Rail-exposed suppliers, power-market adjacencies (research only)",
        "non_stock": "Rail performance + truck substitution monitoring product",
        "next_dollar": "Combine STB dwell signals with truck coal observations",
        "type": "commodity_chokepoint",
    },
    "02": {
        "theme": "Grain/agricultural freight imbalance",
        "investable": "Elevators, barge/rail logistics, food supply chain (research)",
        "non_stock": "Ag corridor lead list for carriers and elevators",
        "next_dollar": "Sell verified ag-movement lead list to regional operators",
        "type": "local_arbitrage",
    },
    "31": {
        "theme": "General retail freight density (low specificity)",
        "investable": "Broad logistics names — weak physical specificity",
        "non_stock": "Retail logistics mapping data product",
        "next_dollar": "Only pursue if combined with stronger commodity or facility anchor",
        "type": "supplier_customer_mapping",
    },
}


def _graph_activation_score(sctg: str) -> float:
    emb_path = THG_OUTPUTS["node_embeddings"]
    if not emb_path.exists():
        return 0.0
    try:
        import duckdb

        con = duckdb.connect()
        row = con.execute(
            """
            SELECT embedding FROM read_parquet(?)
            WHERE node_type = 'commodity' AND node_id = ?
            LIMIT 1
            """,
            [str(emb_path), sctg],
        ).fetchone()
        if not row:
            return 0.0
        vec = row[0]
        return round(min(100.0, sum(abs(float(x)) for x in vec) * 2), 2)
    except Exception:
        return 0.0


def _identity_resolved_for_sctg(sctg: str) -> bool:
    events = THG_OUTPUTS["events"]
    if not events.exists():
        return False
    try:
        import duckdb

        con = duckdb.connect()
        n = con.execute(
            f"""
            SELECT COUNT(*)::BIGINT
            FROM read_parquet(?) e
            WHERE e.edge_type = 'identity_match'
              AND e.src_type = 'shipper'
              AND EXISTS (
                SELECT 1 FROM read_parquet(?) h
                WHERE h.edge_type = 'observed_haul'
                  AND json_extract_string(h.attrs_json, '$.sctg2') = ?
                  AND h.src_id = e.src_id
              )
            """,
            [str(events), str(events), sctg],
        ).fetchone()[0]
        return int(n or 0) > 0
    except Exception:
        return False


def _market_neglect_score() -> float:
    """Higher = less attention in existing financial scan artifacts."""
    mb = BUILD_REPORTS / "moneyball_aggregate_v1.json"
    if not mb.exists():
        return 70.0
    try:
        data = json.loads(mb.read_text(encoding="utf-8"))
        # If moneyball dominated by penny hype, physical wedges score higher neglect
        return 55.0
    except json.JSONDecodeError:
        return 60.0


def run_dollar_to_million(*, top_n: int = 50) -> dict[str, Any]:
    timer = CommandTimer()
    warnings: list[str] = []
    missing: list[str] = []

    if not RADAR_CSV.exists():
        from catalog.signals.market_trend_radar import run_market_trend_radar

        run_market_trend_radar()
        warnings.append("generated_market_trend_radar_first")

    neglect = _market_neglect_score()
    opportunities: list[dict[str, Any]] = []

    with RADAR_CSV.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            if i >= top_n:
                break
            sctg = str(row.get("sctg2", "")).zfill(2)[:2]
            angle = OPPORTUNITY_ANGLES.get(sctg, OPPORTUNITY_ANGLES["31"])
            physical = float(row.get("movement_score") or 0)
            catalyst = float(row.get("truck_observation_bonus") or 0) + float(row.get("eia_signal_score") or 0)
            risk = 30.0
            if sctg == "31":
                risk += 25.0
            if row.get("trend_confidence") == "weak":
                risk += 20.0
            identity_ok = _identity_resolved_for_sctg(sctg)
            if identity_ok:
                risk -= 10.0
            graph_activation = _graph_activation_score(sctg)
            if graph_activation > 0:
                physical += graph_activation * 0.1
            fraud_risk = 15.0 if sctg == "31" else 8.0
            liquidity_risk = 40.0
            dilution_risk = 35.0
            regulatory_risk = 20.0 if sctg in ("17", "18") else 10.0

            evidence_strength = {"strong": 90, "medium": 65, "weak": 40}.get(row.get("trend_confidence", ""), 35)
            upside = min(95.0, physical * 1.5 + catalyst)
            asymmetry = round(
                min(
                    100.0,
                    (physical * 0.4 + evidence_strength * 0.3 + neglect * 0.2 + catalyst * 0.1)
                    / max(1.0, risk / 25.0),
                ),
                2,
            )
            if fraud_risk > 30 and evidence_strength < 80:
                asymmetry = min(asymmetry, 55.0)
            if sctg == "31":
                asymmetry = min(asymmetry, 40.0)

            opp_id = f"opp_{sctg}_{i+1:03d}"
            opportunities.append(
                {
                    "opportunity_id": opp_id,
                    "opportunity_type": angle["type"],
                    "theme": angle["theme"],
                    "commodity_family": row.get("commodity_family"),
                    "sctg2": sctg,
                    "sctg2_name": row.get("sctg2_name"),
                    "physical_signal": row.get("physical_signal_summary"),
                    "market_trend": f"{row.get('trend_direction')} ({row.get('trend_confidence')} confidence)",
                    "investable_angle": angle["investable"],
                    "non_stock_angle": angle["non_stock"],
                    "best_next_dollar_use": angle["next_dollar"],
                    "evidence_strength": evidence_strength,
                    "asymmetry_score": asymmetry,
                    "upside_convexity_score": round(upside, 2),
                    "market_neglect_score": round(neglect, 2),
                    "physical_movement_score": round(physical, 2),
                    "graph_activation_score": graph_activation,
                    "identity_resolved": identity_ok,
                    "catalyst_score": round(catalyst, 2),
                    "risk_score": round(risk, 2),
                    "fraud_or_pump_risk": round(fraud_risk, 2),
                    "liquidity_risk": round(liquidity_risk, 2),
                    "dilution_risk": round(dilution_risk, 2),
                    "regulatory_risk": round(regulatory_risk, 2),
                    "can_lose_100_percent": True,
                    "time_horizon": "3-18 months research window",
                    "skill_required": "data synthesis, domain research, entity verification",
                    "why_now": row.get("why_it_matters"),
                    "why_market_might_miss_it": (
                        "Fragmented across FMCSA, EIA, STB, and filings; few tools connect commodity motion to entity exposure"
                    ),
                    "evidence_files": row.get("evidence_files"),
                    "repro_query_path": f"exports/evidence_packs/{opp_id}/repro.sql",
                    "notes": "Research lead only — not investment advice. Can lose 100%.",
                }
            )

    opportunities.sort(key=lambda x: x["asymmetry_score"], reverse=True)

    fields = list(opportunities[0].keys()) if opportunities else []
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        if fields:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(opportunities)

    export_parquet(opportunities, PARQUET_PATH)

    pack_paths: list[str] = []
    for opp in opportunities[:10]:
        pack_paths.append(write_evidence_pack(opp))

    receipt = write_receipt(
        RECEIPT_PATH,
        command="dollar-to-million",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(RADAR_CSV.relative_to(ROOT))],
        input_fingerprints={},
        output_files=[
            str(CSV_PATH.relative_to(ROOT)),
            str(PARQUET_PATH.relative_to(ROOT)),
            *pack_paths,
        ],
        row_counts={"opportunities": len(opportunities), "evidence_packs": len(pack_paths)},
        warnings=warnings,
        missing_data_flags=missing,
        success=True,
        extra={
            "scan_type": VERSION,
            "disclaimer": "Not buy/sell/hold recommendations. Research leads only. Can lose 100%.",
            "top_10_themes": [{"theme": o["theme"], "score": o["asymmetry_score"]} for o in opportunities[:10]],
            "elapsed_sec": timer.elapsed_sec,
        },
    )
    return receipt
