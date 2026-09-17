"""
Source Truth Engine — resolve newest valid on-disk sources.

Prefer today/ symlinks when they point to real files; otherwise newest release=*.
Reject HTML stubs, tiny placeholders, corrupt shells, manifest-only artifacts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, UNWRAPPED, today_dir, utc_now
from catalog.util import write_json

SELECTED_MANIFEST = BUILD_REPORTS / "selected_source_manifest_v1.json"
REJECTED_MANIFEST = BUILD_REPORTS / "rejected_source_manifest_v1.json"

RELEASE_RE = re.compile(r"^release=(\d{4}-\d{2}-\d{2})$")
TODAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Logical sources used by the transport / commodity spine.
SOURCE_SPECS: dict[str, dict[str, Any]] = {
    "faf5_csv": {
        "family": "faf5_freight",
        "rel": "faf5_csv/FAF5.7.1.csv",
        "min_bytes": 500_000_000,
        "transport": True,
    },
    "cfs_2022_pums": {
        "family": "trade",
        "rel": "cfs_2022_pums/cfs_2022_pums.csv",
        "min_bytes": 500_000_000,
        "transport": True,
    },
    "pet_imports": {
        "family": "maritime",
        "rel": "PET_IMPORTS/PET_IMPORTS.txt",
        "min_bytes": 1_000_000,
        "transport": True,
    },
    "eia_coal": {
        "family": "rail",
        "rel": "COAL/COAL.txt",
        "min_bytes": 10_000_000,
        "transport": True,
    },
    "fmcsa_census": {
        "family": "fmcsa_carriers",
        "rel": "company_census.csv",
        "min_bytes": 500_000_000,
        "root_level": True,
        "transport": True,
    },
    "fmcsa_inspections": {
        "family": "fmcsa_carriers",
        "rel": "mcmis/vehicle_inspection_file.csv",
        "min_bytes": 500_000_000,
        "root_level": True,
        "transport": True,
    },
    "usgs_commodity": {
        "family": "usgs_minerals",
        "rel": "usgs_mrds_relational_compact/Commodity.txt",
        "min_bytes": 100_000,
        "transport": False,
    },
    "census_hs_trade": {
        "family": "trade",
        "rel": "IMDB*.ZIP",
        "min_bytes": 1_000_000,
        "transport": True,
        "glob": True,
        "allow_zip": True,
        "optional": True,
    },
    "stb_ep724_public": {
        "family": "stb_rail",
        "rel": "ep724-public-data.csv",
        "min_bytes": 1_000_000,
        "transport": True,
    },
    "stb_ep724_dwell": {
        "family": "stb_rail",
        "rel": "ep724-average-terminal-dwell-time.csv",
        "min_bytes": 10_000,
        "transport": True,
    },
    "stb_ep724_element10": {
        "family": "stb_rail",
        "rel": "ep724-element-10.csv",
        "min_bytes": 1_000,
        "transport": True,
    },
    "epa_tri_2024": {
        "family": "epa_toxics",
        "rel": "tri_2024_US_basic.csv",
        "min_bytes": 1_000_000,
        "transport": False,
    },
}

# Module-level cache populated by run_source_truth_engine()
_RESOLVED: dict[str, "ResolvedSource"] = {}
_LAST_MANIFEST: dict[str, Any] | None = None


@dataclass(frozen=True)
class ResolvedSource:
    logical: str
    path: Path
    family: str
    method: str  # today_symlink | release_dir | root_file
    release_id: str | None
    bytes: int
    valid: bool
    reject_reason: str | None = None

    def rel_path(self) -> str:
        return str(self.path.relative_to(ROOT))


def _newest_today_day() -> str | None:
    today_root = UNWRAPPED / "today"
    if not today_root.is_dir():
        return None
    days = sorted(
        (d.name for d in today_root.iterdir() if d.is_dir() and TODAY_RE.match(d.name)),
        reverse=True,
    )
    return days[0] if days else None


def _release_dirs(family_dir: Path) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    if not family_dir.is_dir():
        return out
    for child in family_dir.iterdir():
        if not child.is_dir():
            continue
        m = RELEASE_RE.match(child.name)
        if m:
            out.append((m.group(1), child))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def _is_html_stub(path: Path) -> bool:
    if path.suffix.lower() not in {".json", ".html", ".htm", ".csv", ".txt"}:
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:400]
    except OSError:
        return True
    lower = head.lower()
    return "<html" in lower or "missing key" in lower or "api key" in lower


def _validate_file(path: Path, min_bytes: int, *, allow_zip: bool = False) -> tuple[bool, str | None]:
    if not path.is_file():
        return False, "not_a_file"
    if path.name == "manifest.json":
        return False, "manifest_only"
    size = path.stat().st_size
    if size == 0:
        return False, "empty_file"
    if size < min_bytes:
        return False, f"below_min_bytes({size}<{min_bytes})"
    if _is_html_stub(path):
        return False, "html_stub"
    if path.suffix.lower() == ".zip" and not allow_zip:
        return False, "unextracted_zip"
    return True, None


def _glob_candidates(family_dir: Path, pattern: str) -> list[tuple[str, Path]]:
    """Newest release=* dir first, then root-level glob."""
    out: list[tuple[str, Path]] = []
    for release_id, release_dir in _release_dirs(family_dir):
        for p in sorted(release_dir.glob(pattern), key=lambda x: x.name, reverse=True):
            if p.is_file():
                out.append((release_id, p))
    for p in sorted(family_dir.glob(pattern), key=lambda x: x.name, reverse=True):
        if p.is_file():
            out.append(("root", p))
    return out


def _resolve_one(logical: str, spec: dict[str, Any]) -> tuple[ResolvedSource | None, list[dict]]:
    family = spec["family"]
    rel = spec["rel"]
    min_bytes = spec["min_bytes"]
    allow_zip = spec.get("allow_zip", False)
    rejected: list[dict] = []
    candidates: list[tuple[str, Path, str, str | None]] = []

    day = _newest_today_day()
    if day and not spec.get("glob"):
        today_path = today_dir(day) / family / rel
        if today_path.exists():
            real = today_path.resolve() if today_path.is_symlink() else today_path
            candidates.append(("today_symlink", real, day, day))

    family_dir = UNWRAPPED / family
    if spec.get("glob"):
        for tag, path in _glob_candidates(family_dir, rel):
            release_id = tag if tag != "root" else None
            candidates.append(("release_dir" if release_id else "root_file", path, tag, release_id))
    else:
        if spec.get("root_level"):
            root_file = family_dir / rel
            if root_file.is_file():
                candidates.append(("root_file", root_file, "root", None))

        for release_id, release_dir in _release_dirs(family_dir):
            p = release_dir / rel
            if p.is_file():
                candidates.append(("release_dir", p, release_id, release_id))

        for release_id, release_dir in _release_dirs(family_dir):
            p = release_dir / rel
            if p.is_file():
                ok, reason = _validate_file(p, min_bytes, allow_zip=allow_zip)
                if not ok:
                    rejected.append(
                        {
                            "logical": logical,
                            "path": str(p.relative_to(ROOT)),
                            "release_id": release_id,
                            "bytes": p.stat().st_size,
                            "reason": reason,
                        }
                    )

    for method, path, tag, release_id in candidates:
        ok, reason = _validate_file(path, min_bytes, allow_zip=allow_zip)
        if ok:
            return (
                ResolvedSource(
                    logical=logical,
                    path=path,
                    family=family,
                    method=method,
                    release_id=release_id if method != "root_file" else None,
                    bytes=path.stat().st_size,
                    valid=True,
                ),
                rejected,
            )
        rejected.append(
            {
                "logical": logical,
                "path": str(path.relative_to(ROOT)),
                "method": method,
                "tag": tag,
                "bytes": path.stat().st_size if path.exists() else 0,
                "reason": reason,
            }
        )

    return None, rejected


def run_source_truth_engine() -> dict[str, Any]:
    """Resolve all logical sources; emit selected/rejected manifests."""
    global _RESOLVED, _LAST_MANIFEST
    selected: list[dict] = []
    rejected: list[dict] = []
    missing: list[str] = []
    _RESOLVED.clear()

    for logical, spec in SOURCE_SPECS.items():
        resolved, rejects = _resolve_one(logical, spec)
        rejected.extend(rejects)
        if resolved:
            _RESOLVED[logical] = resolved
            selected.append(
                {
                    "logical": logical,
                    "family": resolved.family,
                    "path": resolved.rel_path(),
                    "method": resolved.method,
                    "release_id": resolved.release_id,
                    "bytes": resolved.bytes,
                    "transport": spec.get("transport", False),
                }
            )
        elif not spec.get("optional"):
            missing.append(logical)

    # Scan known stub families (STB R1 shells)
    stb_dir = UNWRAPPED / "stb_rail"
    if stb_dir.is_dir():
        for p in stb_dir.rglob("*.csv"):
            if p.stat().st_size < 500 and "release=" not in str(p):
                rejected.append(
                    {
                        "logical": "stb_r1_stub",
                        "path": str(p.relative_to(ROOT)),
                        "bytes": p.stat().st_size,
                        "reason": "stb_r1_placeholder",
                    }
                )

    sel_payload = {
        "scan_type": "selected_source_manifest_v1",
        "creed": "newest_first",
        "created_at": utc_now(),
        "today_day": _newest_today_day(),
        "selected_count": len(selected),
        "selected": selected,
        "missing_required": missing,
    }
    rej_payload = {
        "scan_type": "rejected_source_manifest_v1",
        "created_at": utc_now(),
        "rejected_count": len(rejected),
        "rejected": rejected[:500],
        "rejected_truncated": len(rejected) > 500,
    }
    write_json(SELECTED_MANIFEST, sel_payload)
    write_json(REJECTED_MANIFEST, rej_payload)
    _LAST_MANIFEST = sel_payload
    return {"selected": sel_payload, "rejected": rej_payload, "resolved": _RESOLVED}


def resolve_path(logical: str, *, refresh: bool = False) -> Path | None:
    """Return resolved path for a logical source name."""
    if refresh or logical not in _RESOLVED:
        run_source_truth_engine()
    r = _RESOLVED.get(logical)
    return r.path if r and r.valid else None


def require_path(logical: str) -> Path:
    p = resolve_path(logical)
    if not p:
        raise FileNotFoundError(f"source_truth: no valid path for {logical}")
    return p


def resolved_sources_dict() -> dict[str, str]:
    """Logical name → relative path string for receipts."""
    if not _RESOLVED:
        run_source_truth_engine()
    return {k: v.rel_path() for k, v in _RESOLVED.items() if v.valid}


def last_manifest() -> dict[str, Any] | None:
    return _LAST_MANIFEST
