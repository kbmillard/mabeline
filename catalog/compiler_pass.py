"""
Mabeline Compiler Pass V1 — orchestrate source truth, spine refresh, proofs, cards.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from catalog.cargo_inspection import run_cargo_inspection
from catalog.commodity_economy import run_commodity_economy
from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.financial_sync import sync_financial_dashboard
from catalog.intelligence_cards import build_sample_cards
from catalog.moving_commodity import run_moving_commodity
from catalog.shipper_carriers import run_dollar_general_carriers
from catalog.source_truth import (
    REJECTED_MANIFEST,
    SELECTED_MANIFEST,
    run_source_truth_engine,
)
from catalog.stb_ep724 import run_stb_ep724_staging
from catalog.transport_economy import run_transport_economy
from catalog.util import append_log, write_json

PASS_RECEIPT = BUILD_REPORTS / "mabeline_compiler_pass_v1.json"


def _files_changed() -> list[str]:
    changed = [
        "catalog/source_truth.py",
        "catalog/compiler_pass.py",
        "catalog/shipper_carriers.py",
        "catalog/stb_ep724.py",
        "catalog/intelligence_cards.py",
        "catalog/freight_movement.py",
        "catalog/commodity_economy.py",
        "catalog/moving_commodity.py",
        "catalog/transport_economy.py",
        "catalog/cargo_inspection.py",
        "catalog/__main__.py",
    ]
    return [p for p in changed if (ROOT / p).exists()]


def run_compiler_pass_v1(*, skip_financial_sync: bool = False) -> dict[str, Any]:
    t0 = time.monotonic()
    commands_run: list[str] = []
    steps: list[dict[str, Any]] = []
    stale_replaced: list[str] = []
    exports_created: list[str] = []
    errors: list[str] = []

    # 1. Source Truth Engine
    try:
        truth = run_source_truth_engine()
        commands_run.append("source_truth_engine")
        steps.append(
            {
                "step": "source_truth",
                "selected": truth["selected"]["selected_count"],
                "rejected": truth["rejected"]["rejected_count"],
                "missing": truth["selected"].get("missing_required", []),
            }
        )
    except Exception as exc:
        errors.append(f"source_truth: {exc}")
        raise

    # 2. Transport spine refresh
    spine_commands = [
        ("moving-commodity", run_moving_commodity),
        ("commodity-economy", lambda: run_commodity_economy(refresh_faf_receipt=False)),
        ("transport-economy", run_transport_economy),
        ("cargo-inspection", run_cargo_inspection),
    ]
    for name, fn in spine_commands:
        try:
            receipt = fn()
            commands_run.append(name)
            steps.append({"step": name, "status": "ok", "keys": list(receipt.keys())[:6]})
            out = BUILD_REPORTS / f"{name.replace('-', '_')}_v1.json"
            # map receipt filenames
            fname_map = {
                "moving-commodity": "moving_commodity_v1.json",
                "commodity-economy": "commodity_economy_v1.json",
                "transport-economy": "transport_economy_v1.json",
                "cargo-inspection": "cargo_inspection_v1.json",
            }
            stale_replaced.append(fname_map.get(name, name))
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            steps.append({"step": name, "status": "error", "error": str(exc)})

    if not skip_financial_sync:
        try:
            sync = sync_financial_dashboard()
            commands_run.append("sync-financial")
            steps.append({"step": "sync-financial", "copied": len(sync["copied"])})
        except Exception as exc:
            errors.append(f"sync-financial: {exc}")

    dg: dict[str, Any] | None = None
    ep724: dict[str, Any] | None = None

    # 3. Dollar General proof
    try:
        dg = run_dollar_general_carriers()
        commands_run.append("shipper-carriers --shipper 'DOLLAR GENERAL'")
        exports_created.append(dg["export_csv"])
        steps.append(
            {
                "step": "dollar_general_carriers",
                "distinct_carriers": dg["distinct_carriers"],
                "export": dg["export_csv"],
            }
        )
    except Exception as exc:
        errors.append(f"dollar_general: {exc}")

    # 4. STB EP724 staging
    try:
        ep724 = run_stb_ep724_staging()
        commands_run.append("stb-ep724-staging")
        steps.append({"step": "stb_ep724", "total_rows": ep724["total_rows"]})
    except Exception as exc:
        errors.append(f"stb_ep724: {exc}")

    # 5. Intelligence cards
    try:
        cards = build_sample_cards(dg_receipt=dg)
        commands_run.append("intelligence-cards")
        exports_created.extend(cards.get("cards", []))
        steps.append({"step": "intelligence_cards", "card_count": cards["card_count"]})
    except Exception as exc:
        errors.append(f"intelligence_cards: {exc}")

    remaining_stale = [
        g
        for g in [
            "CFS 2023 not published",
            "shipper_name_normalization not built",
            "entity_resolution_graph not built",
            "phmsa_pipelines not wired",
        ]
    ]

    pass_receipt = {
        "scan_type": "mabeline_compiler_pass_v1",
        "mission": "movement-to-market intelligence compiler pass",
        "status": "ok" if not errors else "partial",
        "commands_run": commands_run,
        "files_changed": _files_changed(),
        "source_families_selected": [
            s["logical"] for s in truth["selected"]["selected"]
        ],
        "source_families_rejected_sample": [
            r.get("reason") for r in truth["rejected"]["rejected"][:20]
        ],
        "manifests": {
            "selected": str(SELECTED_MANIFEST.relative_to(ROOT)),
            "rejected": str(REJECTED_MANIFEST.relative_to(ROOT)),
        },
        "stale_receipts_replaced": stale_replaced,
        "exports_created": exports_created,
        "steps": steps,
        "row_file_counts": {
            "selected_sources": truth["selected"]["selected_count"],
            "rejected_artifacts": truth["rejected"]["rejected_count"],
            "dollar_general_carriers": dg.get("distinct_carriers") if dg else None,
            "stb_ep724_rows": ep724.get("total_rows") if ep724 else None,
        },
        "known_false_stale_remaining": remaining_stale,
        "errors": errors,
        "next_highest_leverage": "shipper_name_normalization + entity graph + PHMSA wire",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }
    write_json(PASS_RECEIPT, pass_receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} mabeline_compiler_pass_v1.json status={pass_receipt['status']}",
    )
    return pass_receipt
