"""
Newest-first path resolution for Mabeline catalog.

Ranks candidates by: exists → today symlink freshness → mtime → release date → size.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from catalog.config import ROOT, UNWRAPPED, today_dir, today_id
from catalog.util import file_signature

RELEASE_RE = re.compile(r"release=(\d{4}-\d{2}-\d{2})")
TODAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEFAULT_STUB_BYTES = 500


def repo_root() -> Path:
    return ROOT


def unwrapped_root() -> Path:
    return UNWRAPPED


def today_root(day: str | None = None) -> Path:
    return today_dir(day)


def latest_release_dir(base: Path, prefix: str = "release=") -> Path | None:
    if not base.is_dir():
        return None
    candidates: list[tuple[str, Path]] = []
    for child in base.iterdir():
        if child.is_dir() and child.name.startswith(prefix):
            date_part = child.name[len(prefix) :]
            if TODAY_RE.match(date_part):
                candidates.append((date_part, child))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _release_date_from_path(path: Path) -> str:
    m = RELEASE_RE.search(str(path))
    return m.group(1) if m else ""


def _is_html_stub(path: Path) -> bool:
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:400].lower()
    except OSError:
        return True
    return "<html" in head or "missing key" in head or "api key" in head


def is_valid_data_file(path: Path, *, stub_bytes: int = DEFAULT_STUB_BYTES) -> tuple[bool, str | None]:
    if not path.is_file():
        return False, "not_a_file"
    if path.name == "manifest.json":
        return False, "manifest_only"
    size = path.stat().st_size
    if size == 0:
        return False, "empty_file"
    if size < stub_bytes:
        return False, f"below_stub_threshold({size}<{stub_bytes})"
    if _is_html_stub(path):
        return False, "html_stub"
    if path.suffix.lower() == ".zip":
        return False, "unextracted_zip"
    return True, None


def file_fingerprint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    sig = file_signature(path, with_md5=False)
    real = path.resolve() if path.is_symlink() else path
    return {
        "exists": True,
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "bytes": sig["bytes"],
        "mtime": sig["mtime"],
        "release_date": _release_date_from_path(real),
        "is_symlink": path.is_symlink(),
        "resolved": str(real.relative_to(ROOT)) if real.is_relative_to(ROOT) else str(real),
    }


def _candidate_score(path: Path, *, stub_bytes: int) -> tuple[int, dict[str, Any]] | None:
    ok, reason = is_valid_data_file(path, stub_bytes=stub_bytes)
    if not ok:
        return None
    real = path.resolve() if path.is_symlink() else path
    mtime = path.stat().st_mtime
    release = _release_date_from_path(real)
    under_today = "/today/" in str(path)
    score = 0
    if under_today:
        score += 1_000_000_000
    score += int(mtime)
    if release:
        score += int(release.replace("-", "")) * 10
    score += min(path.stat().st_size, 10_000_000_000)
    meta = {
        "path": path,
        "real": real,
        "mtime": mtime,
        "release_date": release,
        "under_today": under_today,
        "bytes": path.stat().st_size,
    }
    return score, meta


def resolve_newest(candidates: list[Path], *, required: bool = True, stub_bytes: int = DEFAULT_STUB_BYTES) -> Path:
    ranked: list[tuple[int, dict[str, Any]]] = []
    for cand in candidates:
        if not cand:
            continue
        scored = _candidate_score(cand, stub_bytes=stub_bytes)
        if scored:
            ranked.append(scored)
    if not ranked:
        if required:
            raise FileNotFoundError(f"resolve_newest: no valid candidate among {[str(c) for c in candidates]}")
        return Path()
    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked[0][1]["real"]


def build_family_candidates(
    family: str,
    rel: str,
    *,
    root_level: bool = False,
    day: str | None = None,
) -> list[Path]:
    """Build candidate paths: today symlink, root file, release=* dirs."""
    out: list[Path] = []
    day = day or today_id()
    today_path = today_root(day) / family / rel
    if today_path.exists():
        out.append(today_path)
    family_dir = unwrapped_root() / family
    if root_level:
        root_file = family_dir / rel
        if root_file.exists():
            out.append(root_file)
    release = latest_release_dir(family_dir)
    if release:
        rp = release / rel
        if rp.exists():
            out.append(rp)
    for _, rel_dir in _all_release_dirs(family_dir):
        p = rel_dir / rel
        if p.exists() and p not in out:
            out.append(p)
    return out


def _all_release_dirs(family_dir: Path) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    if not family_dir.is_dir():
        return out
    for child in family_dir.iterdir():
        if child.is_dir():
            m = RELEASE_RE.match(child.name)
            if m:
                out.append((m.group(1), child))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def resolve_family_file(
    family: str,
    rel: str,
    *,
    root_level: bool = False,
    min_bytes: int = DEFAULT_STUB_BYTES,
    required: bool = True,
) -> Path | None:
    cands = build_family_candidates(family, rel, root_level=root_level)
    try:
        return resolve_newest(cands, required=required, stub_bytes=min_bytes)
    except FileNotFoundError:
        return None
