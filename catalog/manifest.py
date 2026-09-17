from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from catalog.config import UNWRAPPED, utc_now
from catalog.util import file_signature, rel_under, write_json


def _format_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".geojson":
        return "geojson"
    if ext == ".jsonl":
        return "jsonl"
    if ext in {".csv", ".tsv", ".txt", ".dat"}:
        return "tabular_text"
    if ext == ".parquet":
        return "parquet"
    if ext in {".json"}:
        return "json"
    if ext in {".xlsx", ".xls"}:
        return "spreadsheet"
    if ext in {".xml"}:
        return "xml"
    return ext.lstrip(".") or "unknown"


def scan_family(family_dir: Path) -> dict:
    family = family_dir.name
    files: list[dict] = []
    formats: Counter[str] = Counter()
    total_bytes = 0

    for path in sorted(family_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "manifest.json" or path.name.endswith(".unwrap.done"):
            continue
        rel = rel_under(family_dir, path)
        sig = file_signature(path, with_md5=False)
        fmt = _format_for(path)
        formats[fmt] += 1
        total_bytes += sig["bytes"]
        files.append(
            {
                "dest": rel,
                "logical_dest": f"data/raw/{family}/{rel}",
                "status": "present",
                "format": fmt,
                **sig,
            }
        )

    return {
        "source": family,
        "updated_at": utc_now(),
        "inventory": {
            "file_count": len(files),
            "total_bytes": total_bytes,
            "formats": dict(formats),
        },
        "files": files,
    }


def merge_manifest(existing: dict | None, scanned: dict) -> dict:
    if not existing:
        return scanned

    old_by_dest: dict[str, dict] = {}
    for ent in existing.get("files", []):
        key = ent.get("dest") or ent.get("logical_dest") or ""
        if key:
            old_by_dest[key] = ent
            # also index basename-only legacy dests
            if "/" in key:
                old_by_dest[key.split("/")[-1]] = ent

    merged_files = []
    for ent in scanned["files"]:
        rel = ent["dest"]
        legacy = old_by_dest.get(rel) or old_by_dest.get(ent["logical_dest"])
        if legacy:
            merged = {**legacy, **ent}
            merged["status"] = "present" if ent["bytes"] > 0 else legacy.get("status", "present")
            merged_files.append(merged)
        else:
            merged_files.append(ent)

    # Preserve download-only entries that failed and have no on-disk substitute.
    present_dests = {e["dest"] for e in merged_files}
    for ent in existing.get("files", []):
        dest = ent.get("dest", "")
        base = Path(dest).name
        if ent.get("status") == "error" and base not in present_dests:
            merged_files.append(ent)

    out = {
        **existing,
        **scanned,
        "files": merged_files,
        "inventory": scanned["inventory"],
        "updated_at": scanned["updated_at"],
    }
    for k in ("errors", "gaps_filled", "on_disk", "policy", "release", "local_present"):
        if k in existing and k not in out:
            out[k] = existing[k]
    if "errors" not in out:
        out["errors"] = existing.get("errors", [])
    return out


def family_status(manifest: dict) -> str:
    inv = manifest.get("inventory", {})
    total_bytes = inv.get("total_bytes", 0)
    file_count = inv.get("file_count", 0)
    formats = inv.get("formats", {})

    stub_only = file_count > 0 and total_bytes < 10_000 and not formats.get("parquet")
    if file_count == 0:
        return "empty"
    if stub_only:
        return "empty"

    errors = [f for f in manifest.get("files", []) if f.get("status") == "error"]
    tabular = sum(formats.get(k, 0) for k in ("tabular_text", "csv", "json", "jsonl", "geojson", "parquet", "spreadsheet"))
    if errors and tabular == 0:
        return "empty"
    if errors:
        return "partial"
    if manifest.get("source") in {"commercial", "manual_gaps"}:
        return "pass"
    if formats.get("geojson", 0) > 100 and manifest.get("source") == "all_the_places":
        return "pass"
    if total_bytes > 0:
        return "pass"
    return "partial"


def build_family_manifest(family_dir: Path) -> dict:
    scanned = scan_family(family_dir)
    existing = None
    mf = family_dir / "manifest.json"
    if mf.exists():
        try:
            existing = json.loads(mf.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = None
    merged = merge_manifest(existing, scanned)
    merged["status"] = family_status(merged)
    return merged


def build_all_manifests() -> dict:
    families = sorted(p for p in UNWRAPPED.iterdir() if p.is_dir())
    receipts = []
    for family_dir in families:
        manifest = build_family_manifest(family_dir)
        write_json(family_dir / "manifest.json", manifest)
        receipts.append(
            {
                "family": family_dir.name,
                "status": manifest["status"],
                "file_count": manifest["inventory"]["file_count"],
                "total_bytes": manifest["inventory"]["total_bytes"],
            }
        )

    root = {
        "created_at": utc_now(),
        "policy": "_unwrapped canonical; overture_places excluded",
        "dest_unwrapped": str(UNWRAPPED),
        "family_count": len(receipts),
        "total_bytes": sum(r["total_bytes"] for r in receipts),
        "families": receipts,
    }
    write_json(UNWRAPPED.parent / "manifest.json", root)
    return {"families": receipts, "root": root}
