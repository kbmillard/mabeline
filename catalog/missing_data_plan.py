"""Post-exhaust open-source scan — only report gaps after disk + download pass."""

from __future__ import annotations

import csv
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, UNWRAPPED, today_id
from catalog.gaps import STUB_BYTES, _discovered_open_sources, _is_bad_on_disk, fill_gaps
from catalog.path_resolver import is_valid_data_file, unwrapped_root
from catalog.signals._common import CommandTimer, EXPORTS_DIR, write_receipt

RECEIPT_PATH = BUILD_REPORTS / "missing_data_plan_v1.json"
CSV_PATH = EXPORTS_DIR / "missing_data_plan_v1.csv"
VERSION = "missing_data_plan_v2"

# Wiring debt only — sources on disk but not yet in THG (post 2026-07-09 wire pass).
WIRING_DEBT: list[dict[str, Any]] = [
    {
        "id": "sam_open_bulk_deferred",
        "priority": "P2",
        "status": "policy_deferred",
        "path": "sam.gov entity API",
        "why": "No stable open SAM entity bulk without policy key",
        "action": "LEI/SEC wired; SAM when bulk URL confirmed",
    },
]

POLICY_EXCLUSIONS: list[dict[str, Any]] = [
    {
        "id": "commercial_enrichment",
        "priority": "DEFERRED",
        "status": "not_on_disk",
        "path": "_unwrapped/commercial/",
        "why": "No free national bulk for D&B/ZoomInfo",
        "action": "SAM/FPDS/LEI only",
    },
    {
        "id": "overture_places",
        "priority": "EXTERNAL",
        "status": "excluded",
        "path": "postgres sweeper_dev.overture_places",
        "why": "Facility POI anchoring lives outside _unwrapped by policy",
        "action": "Connector stub; disabled by default",
    },
    {
        "id": "wikidata_parquet_deferred",
        "priority": "P3",
        "status": "deferred",
        "path": "_unwrapped/wikidata/",
        "why": "95GB bz2 dump deferred for parquet conversion",
        "action": "Streaming claims subset only",
    },
    {
        "id": "cfs_2023",
        "priority": "P3",
        "status": "not_released",
        "path": "_unwrapped/trade/",
        "why": "CFS 2023 survey not published yet",
        "action": "Watch census.gov CFS datasets page",
    },
]


def _scan_open_source_targets(release_id: str, gap_register: dict[str, Any]) -> list[dict[str, Any]]:
    """Build gap rows from exhaust pass + disk validation only."""
    rows: list[dict[str, Any]] = []

    for gap in gap_register.get("gaps", []):
        name = gap.get("source_name", "")
        rows.append(
            {
                "id": name,
                "priority": gap.get("priority", "P2"),
                "status": gap.get("current_status", "unknown"),
                "path": name,
                "why": gap.get("missing_reason", ""),
                "source": "open_source_exhaust",
                "action": "Re-run bin/mabel-catalog gaps",
                "category": "remaining_gap",
            }
        )

    seen_errors: set[str] = set()
    for err in gap_register.get("download_attempts", []):
        if err.get("status") != "error":
            continue
        err_id = f"download_error/{err['family']}/{err['dest']}"
        if err_id in seen_errors:
            continue
        seen_errors.add(err_id)
        rows.append(
            {
                "id": err_id,
                "priority": "P2",
                "status": "download_error",
                "path": f"_unwrapped/{err['family']}/{err['dest']}",
                "why": err.get("error", ""),
                "source": err.get("url", ""),
                "action": "Retry gaps; URL is public bulk",
                "category": "download_error",
            }
        )

    discovered = _discovered_open_sources(release_id)
    for item in discovered:
        rows.append(
            {
                "id": f"resolved/{item.get('family')}/{item.get('path', item.get('carrier', ''))}",
                "priority": "RESOLVED",
                "status": "on_disk_valid",
                "path": item.get("path", f"stb_rail R1-{item.get('carrier')}-2025"),
                "why": "Found valid after open-source exhaust",
                "source": "disk_scan",
                "action": "Wire into spine; do not re-list as gap",
                "category": "resolved",
            }
        )

    for debt in WIRING_DEBT:
        rel = debt["path"]
        full = ROOT / rel if not rel.startswith("catalog") else ROOT / rel
        valid = False
        bytes_size = 0
        if full.exists():
            if full.is_file():
                valid, _ = is_valid_data_file(full)
                bytes_size = full.stat().st_size
            else:
                valid = any(
                    not _is_bad_on_disk(p)
                    for p in full.rglob("*")
                    if p.is_file() and not p.name.endswith(".unwrap.done")
                )
        rows.append({**debt, "bytes": bytes_size, "valid_on_disk": valid, "category": "wiring_debt"})

    for excl in POLICY_EXCLUSIONS:
        rows.append({**excl, "bytes": 0, "valid_on_disk": False, "category": "policy"})

    return rows


def run_missing_data_plan(*, exhaust_first: bool = True) -> dict[str, Any]:
    timer = CommandTimer()
    release_id = today_id()

    gap_register: dict[str, Any] = {}
    if exhaust_first:
        gap_register = fill_gaps()

    rows = _scan_open_source_targets(release_id, gap_register)

    if rows:
        fields = list(rows[0].keys())
        for row in rows[1:]:
            for k in row:
                if k not in fields:
                    fields.append(k)
        with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    remaining = [r for r in rows if r.get("category") in ("remaining_gap", "download_error")]
    resolved = [r for r in rows if r.get("category") == "resolved"]
    wiring = [r for r in rows if r.get("category") == "wiring_debt" and r.get("priority") in ("P0", "P1")]

    receipt = write_receipt(
        RECEIPT_PATH,
        command="missing-data-plan",
        version=VERSION,
        started_at=timer.started_at,
        input_files=[str(unwrapped_root())],
        input_fingerprints={},
        output_files=[str(CSV_PATH.relative_to(ROOT))],
        row_counts={
            "total_rows": len(rows),
            "remaining_gaps": len(remaining),
            "resolved_on_disk": len(resolved),
            "wiring_debt": len(wiring),
        },
        warnings=[],
        missing_data_flags=[r["id"] for r in remaining[:20]],
        success=True,
        extra={
            "scan_type": VERSION,
            "creed": "exhaust_open_sources_before_gaps",
            "release_id": release_id,
            "exhaust_first": exhaust_first,
            "discovered_count": len(resolved),
            "top_remaining": remaining[:10],
            "top_wiring": wiring[:10],
            "elapsed_sec": timer.elapsed_sec,
        },
    )
    return receipt
