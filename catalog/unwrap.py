from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from catalog.config import UNWRAPPED, utc_now
from catalog.util import append_log, rel_under, write_json


def unwrap_family(family_dir: Path, log_path: Path | None = None) -> dict:
    family = family_dir.name
    unwrapped = 0
    skipped = 0
    errors: list[str] = []

    for zpath in sorted(family_dir.rglob("*.zip")):
        marker = Path(str(zpath) + ".unwrap.done")
        if marker.exists():
            skipped += 1
            continue
        dest_dir = zpath.parent / zpath.stem
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zpath, "r") as zf:
                zf.extractall(dest_dir)
            marker.write_text("ok\n", encoding="utf-8")
            unwrapped += 1
            if log_path:
                append_log(log_path, f"unwrap {family}: {rel_under(UNWRAPPED, zpath)}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{zpath}: {exc}")

    return {
        "family": family,
        "unwrapped": unwrapped,
        "skipped": skipped,
        "errors": errors,
        "updated_at": utc_now(),
    }


def unwrap_all(log_path: Path | None = None) -> dict:
    results = []
    for family_dir in sorted(p for p in UNWRAPPED.iterdir() if p.is_dir()):
        results.append(unwrap_family(family_dir, log_path))
    return {
        "updated_at": utc_now(),
        "families": results,
        "unwrapped": sum(r["unwrapped"] for r in results),
        "errors": [e for r in results for e in r["errors"]],
    }
