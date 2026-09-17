"""Evidence pack writer for dollar-to-million opportunities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import ROOT
from catalog.graph.month_picker import pick_snapshot_month
from catalog.graph.schema_v1 import OUTPUTS
from catalog.util import write_json

EVIDENCE_ROOT = ROOT / "exports" / "evidence_packs"
EVENTS_PATH = OUTPUTS["events"]


def _build_subgraph(opportunity: dict[str, Any]) -> dict[str, Any]:
    sctg = str(opportunity.get("sctg2", "")).zfill(2)[:2]
    if not EVENTS_PATH.exists():
        return {"nodes": [], "edges": [], "note": "thg_not_built"}

    con = duckdb.connect()
    month = pick_snapshot_month(EVENTS_PATH, con=con)
    events_s = str(EVENTS_PATH)

    edges = con.execute(
        f"""
        SELECT edge_type, src_type, src_id, dst_type, dst_id, event_time, weight, confidence, attrs_json
        FROM read_parquet('{events_s}')
        WHERE (
          edge_type IN ('observed_haul', 'hauls_commodity', 'commodity_pressure', 'trade_import')
          AND (
            json_extract_string(attrs_json, '$.sctg2') = ?
            OR (edge_type = 'hauls_commodity' AND dst_id = ?)
            OR (edge_type = 'trade_import' AND dst_id = ?)
            OR (edge_type = 'commodity_pressure' AND src_id = ?)
          )
        )
        OR (edge_type = 'identity_match' AND src_type = 'shipper')
        ORDER BY weight DESC
        LIMIT 500
        """,
        [sctg, sctg, sctg, sctg],
    ).fetchall()

    node_set: set[tuple[str, str]] = set()
    edge_rows: list[dict[str, Any]] = []
    for e in edges:
        node_set.add((e[1], e[2]))
        node_set.add((e[3], e[4]))
        edge_rows.append(
            {
                "edge_type": e[0],
                "src_type": e[1],
                "src_id": e[2],
                "dst_type": e[3],
                "dst_id": e[4],
                "event_time": e[5],
                "weight": float(e[6] or 0),
                "confidence": e[7],
                "attrs_json": e[8],
            }
        )

    nodes = [{"node_type": nt, "node_id": nid} for nt, nid in sorted(node_set)]
    return {
        "opportunity_id": opportunity.get("opportunity_id"),
        "sctg2": sctg,
        "snapshot_month": month,
        "node_count": len(nodes),
        "edge_count": len(edge_rows),
        "nodes": nodes[:200],
        "edges": edge_rows[:200],
    }


def write_evidence_pack(opportunity: dict[str, Any]) -> str:
    opp_id = opportunity["opportunity_id"]
    pack_dir = EVIDENCE_ROOT / opp_id
    pack_dir.mkdir(parents=True, exist_ok=True)
    sctg = str(opportunity.get("sctg2", "")).zfill(2)[:2]
    events_rel = str(EVENTS_PATH.relative_to(ROOT)) if EVENTS_PATH.exists() else "warehouse/th_graph_v1/temporal_edge_events_v1.parquet"
    scores_rel = str(OUTPUTS["change_scores"].relative_to(ROOT)) if OUTPUTS["change_scores"].exists() else ""

    summary = f"""# {opportunity.get('theme')}

## What changed physically?
{opportunity.get('physical_signal', 'N/A')}

## What commodity is moving?
{opportunity.get('sctg2_name')} (SCTG {opportunity.get('sctg2')}) — {opportunity.get('commodity_family')}

## What is the market trend?
{opportunity.get('market_trend')}

## Why might the market miss it?
{opportunity.get('why_market_might_miss_it')}

## What is the asymmetric angle?
**Investable research angle:** {opportunity.get('investable_angle')}
**Non-stock angle:** {opportunity.get('non_stock_angle')}

## What could make this wrong?
- Weak entity resolution
- Inspection shipper field is not bill-of-lading proof
- Stale or sampled data
- Commodity inference may be weak for SCTG {opportunity.get('sctg2')}

## What data is missing?
See risk_flags.json and source_files.json

## What is the next best $1 action?
{opportunity.get('best_next_dollar_use')}

---
**Risk:** Can lose 100%. Not investment advice.
"""
    (pack_dir / "summary.md").write_text(summary, encoding="utf-8")

    evidence = {
        "opportunity_id": opp_id,
        "asymmetry_score": opportunity.get("asymmetry_score"),
        "physical_movement_score": opportunity.get("physical_movement_score"),
        "evidence_strength": opportunity.get("evidence_strength"),
        "physical_signal": opportunity.get("physical_signal"),
        "graph_activation_score": opportunity.get("graph_activation_score"),
    }
    write_json(pack_dir / "evidence.json", evidence)

    write_json(pack_dir / "subgraph.json", _build_subgraph(opportunity))

    repro = f"""-- Reproduce opportunity motif for {opp_id} against THG parquet
-- DuckDB / SQL Server CTE style

WITH events AS (
    SELECT *
    FROM read_parquet('{events_rel}')
),
scores AS (
    SELECT *
    FROM read_parquet('{scores_rel}')
    WHERE sctg2 = '{sctg}'
),
hauls AS (
    SELECT
        json_extract_string(attrs_json, '$.sctg2') AS sctg2,
        json_extract_string(attrs_json, '$.state') AS state,
        SUM(weight) AS truck_weight,
        COUNT(DISTINCT src_id) AS shippers,
        COUNT(DISTINCT dst_id) AS carriers
    FROM events
    WHERE edge_type = 'observed_haul'
      AND json_extract_string(attrs_json, '$.sctg2') = '{sctg}'
    GROUP BY 1, 2
),
macro AS (
    SELECT edge_type, SUM(weight) AS w
    FROM events
    WHERE edge_type IN ('commodity_pressure', 'trade_import', 'modeled_flow')
      AND (
        json_extract_string(attrs_json, '$.sctg2') = '{sctg}'
        OR dst_id = '{sctg}'
        OR src_id = '{sctg}'
      )
    GROUP BY 1
)
SELECT
    s.sctg2,
    s.snapshot_month,
    s.change_score,
    s.truck_observation_delta_pct,
    s.truck_vs_faf_residual,
    h.state,
    h.truck_weight,
    h.shippers,
    h.carriers
FROM scores s
LEFT JOIN hauls h ON s.sctg2 = h.sctg2
ORDER BY s.change_score DESC, h.truck_weight DESC;
"""
    (pack_dir / "repro.sql").write_text(repro, encoding="utf-8")

    sources = {
        "evidence_files": opportunity.get("evidence_files"),
        "thg_events": events_rel,
        "thg_change_scores": scores_rel,
        "repo_root": str(ROOT),
    }
    write_json(pack_dir / "source_files.json", sources)

    identity_resolved = bool(opportunity.get("identity_resolved"))
    warnings = [
        "Not buy/sell/hold recommendation",
        "Inspection shipper != cargo proof",
    ]
    if not identity_resolved:
        warnings.append("Entity resolution incomplete")

    risks = {
        "can_lose_100_percent": True,
        "risk_score": opportunity.get("risk_score"),
        "fraud_or_pump_risk": opportunity.get("fraud_or_pump_risk"),
        "liquidity_risk": opportunity.get("liquidity_risk"),
        "dilution_risk": opportunity.get("dilution_risk"),
        "regulatory_risk": opportunity.get("regulatory_risk"),
        "identity_resolved": identity_resolved,
        "warnings": warnings,
    }
    write_json(pack_dir / "risk_flags.json", risks)

    actions = f"""# Next actions for {opp_id}

1. Run: bin/mabel-catalog thg-query --sctg2 {sctg}
2. Inspect subgraph.json in this pack for carriers/shippers/pressure edges
3. Cross-check EIA/STB/IMDB layers in temporal_edge_events for SCTG {sctg}
4. Package lead list or report — do not publish without manual verification
"""
    (pack_dir / "next_actions.md").write_text(actions, encoding="utf-8")

    return str(pack_dir.relative_to(ROOT))


def run_signal_evidence_pack(*, opportunity_id: str | None = None) -> dict[str, Any]:
    """Regenerate evidence pack for one opportunity or top 10 from dollar_to_million CSV."""
    import csv

    csv_path = ROOT / "exports" / "dollar_to_million_opportunities_v1.csv"
    if not csv_path.exists():
        from catalog.signals.dollar_to_million import run_dollar_to_million

        return run_dollar_to_million()

    written: list[str] = []
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if opportunity_id and row.get("opportunity_id") != opportunity_id:
                continue
            written.append(write_evidence_pack(row))
            if not opportunity_id and len(written) >= 10:
                break

    return {"packs_written": written, "count": len(written)}
