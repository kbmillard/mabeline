"""
Today ingest: gaps → unwrap → absorb into _unwrapped/today/YYYY-MM-DD/.

Folder date is UTC (same as release=YYYY-MM-DD). Evening US runs often land on
the next UTC day — e.g. 8pm Jul 8 CDT → 2026-07-09.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from catalog.config import BUILD_REPORTS, ROOT, UNWRAPPED, today_dir, today_id, utc_now
from catalog.gaps import fill_gaps
from catalog.unwrap import unwrap_family
from catalog.util import append_log, file_signature, rel_under, write_json

TODAY_RECEIPT = BUILD_REPORTS / "today_ingest_receipt_v1.json"

# Root-level files refreshed on a gaps run (not under release=).
_ROOT_ABSORB: dict[str, list[str]] = {
    "fmcsa_carriers": ["company_census.csv"],
}

_TRANSPORT_FAMILIES = ("fmcsa_carriers", "maritime", "rail", "stb_rail", "epa_toxics", "trade")


def _symlink_or_copy(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    try:
        rel = os.path.relpath(src, dest.parent)
        dest.symlink_to(rel)
        return "symlink"
    except OSError:
        shutil.copy2(src, dest)
        return "copy"


def _absorb_file(src: Path, day_root: Path, family: str, label: str) -> dict:
    rel = label.replace("\\", "/")
    dest = day_root / family / rel
    method = _symlink_or_copy(src, dest)
    sig = file_signature(src, with_md5=False)
    return {
        "family": family,
        "source": str(src.relative_to(ROOT)),
        "today_path": str(dest.relative_to(ROOT)),
        "method": method,
        "bytes": sig["bytes"],
    }


def absorb_today(day: str | None = None) -> dict:
    """Link/copy everything under release={day} (+ root refreshes) into today/{day}/."""
    day = day or today_id()
    root = today_dir(day)
    root.mkdir(parents=True, exist_ok=True)
    absorbed: list[dict] = []

    release_tag = f"release={day}"
    for family_dir in sorted(p for p in UNWRAPPED.iterdir() if p.is_dir() and p.name != "today"):
        family = family_dir.name
        release_dir = family_dir / release_tag
        if release_dir.is_dir():
            for path in sorted(release_dir.rglob("*")):
                if not path.is_file() or path.name.endswith(".unwrap.done"):
                    continue
                if path.suffix == ".zip" and (path.parent / f"{path.name}.unwrap.done").exists():
                    continue
                rel = rel_under(release_dir, path)
                absorbed.append(_absorb_file(path, root, family, rel))

        for name in _ROOT_ABSORB.get(family, []):
            src = family_dir / name
            if not src.is_file() or src.stat().st_size == 0:
                continue
            mtime_day = __import__("datetime").datetime.fromtimestamp(
                src.stat().st_mtime, tz=__import__("datetime").timezone.utc
            ).strftime("%Y-%m-%d")
            if mtime_day == day:
                absorbed.append(_absorb_file(src, root, family, name))

    manifest = {
        "scan_type": "today_ingest_manifest_v1",
        "day": day,
        "timezone": "UTC",
        "path": str(root.relative_to(ROOT)),
        "file_count": len(absorbed),
        "total_bytes": sum(a["bytes"] for a in absorbed),
        "files": absorbed,
        "updated_at": utc_now(),
    }
    write_json(root / "manifest.json", manifest)
    return manifest


def run_today(*, absorb_only: bool = False, day: str | None = None) -> dict:
    """Full today pipeline: gaps → unwrap transport zips → absorb → receipt."""
    day = day or today_id()
    log = ROOT / "reports" / "catalog_run.log"
    steps: list[dict] = []

    if not absorb_only:
        gaps = fill_gaps(log_path=log)
        downloaded = sum(1 for r in gaps["download_attempts"] if r["status"] == "downloaded")
        fresh = sum(1 for r in gaps["download_attempts"] if r["status"] == "fresh")
        steps.append({"step": "gaps", "downloaded": downloaded, "fresh": fresh})

        unwrapped = 0
        errors: list[str] = []
        for fam in _TRANSPORT_FAMILIES:
            fam_dir = UNWRAPPED / fam
            if not fam_dir.is_dir():
                continue
            result = unwrap_family(fam_dir, log_path=log)
            unwrapped += result["unwrapped"]
            errors.extend(result["errors"])
        steps.append({"step": "unwrap", "unwrapped": unwrapped, "errors": errors})

    manifest = absorb_today(day)
    steps.append(
        {
            "step": "absorb",
            "day": day,
            "path": manifest["path"],
            "files": manifest["file_count"],
            "bytes": manifest["total_bytes"],
        }
    )

    receipt = {
        "scan_type": "today_ingest_receipt_v1",
        "creed": "newest_first",
        "day": day,
        "timezone": "UTC",
        "note": "Folder date is UTC. US evening runs may show tomorrow's date vs local clock.",
        "today_path": manifest["path"],
        "steps": steps,
        "manifest": manifest,
        "created_at": utc_now(),
    }
    write_json(TODAY_RECEIPT, receipt)
    append_log(log, f"{utc_now()} today ingest day={day} files={manifest['file_count']}")
    return receipt
