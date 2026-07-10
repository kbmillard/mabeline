from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/kyle/Documents/mabeline")
UNWRAPPED = ROOT / "_unwrapped"
WAREHOUSE = ROOT / "warehouse" / "catalog_parquet_v1"
BUILD_REPORTS = ROOT / "build_reports"
REPORTS = ROOT / "reports"

SKIP_PARQUET_SUFFIXES = {
    ".bz2",
    ".gz",
    ".zip",
    ".pdf",
    ".xsd",
    ".shp",
    ".shx",
    ".dbf",
    ".prj",
    ".cpg",
    ".lyr",
    ".doc",
    ".html",
    ".met",
    ".ini",
    ".accdb",
    ".db",
    ".unwrap.done",
}

SKIP_PARQUET_NAMES = {"manifest.json"}

# Files above this size skip content md5 during inventory (use size+mtime only).
MD5_MAX_BYTES = 500 * 1024 * 1024

# Whole-file parquet skip (deferred bulk blobs).
PARQUET_DEFER_MIN_BYTES = 10 * 1024 * 1024 * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_id() -> str:
    """UTC calendar date for release folders (YYYY-MM-DD)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def today_dir(day: str | None = None) -> Path:
    """Dated ingest folder: _unwrapped/today/YYYY-MM-DD/."""
    return UNWRAPPED / "today" / (day or today_id())


def run_dir(run_id: str) -> Path:
    return WAREHOUSE / f"run_id={run_id}"
