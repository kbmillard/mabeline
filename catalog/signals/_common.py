"""Shared helpers for Mabeline signal pipeline."""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from catalog.config import BUILD_REPORTS, ROOT, WAREHOUSE, utc_now
from catalog.path_resolver import file_fingerprint
from catalog.util import write_json

EXPORTS_DIR = ROOT / "exports"
CSV_OPTS = "header=true, ignore_errors=true"

LANE_TO_SCTG: dict[str, tuple[str, str, str]] = {
    "grain_feed": ("02", "Cereal grains", "strong"),
    "petroleum_chem": ("17", "Petroleum products", "strong"),
    "coal_coke": ("19", "Coal", "strong"),
    "waste_scrap": ("41", "Waste/scrap", "medium"),
    "metal_sheet": ("11", "Nonmetal minerals", "medium"),
    "general_freight": ("31", "Mixed freight", "weak"),
    "hazmat": ("18", "Chemical products", "medium"),
    "tanker": ("17", "Petroleum products", "medium"),
    "unknown": ("", "Unknown", "unknown"),
}

SHIPPER_COMMODITY_HINTS: list[tuple[re.Pattern[str], str, str, str]] = [
    (re.compile(r"PETROLEUM|OIL\s|REFINER|TANK|PIPELINE|VALERO|MARATHON|PHILLIPS", re.I), "petroleum_chem", "17", "Petroleum products"),
    (re.compile(r"GRAIN|FEED|MILL|AGRI|FARM|COOP|CARGILL|ADM\b", re.I), "grain_feed", "02", "Cereal grains"),
    (re.compile(r"COAL|COKE|MINING", re.I), "coal_coke", "19", "Coal"),
    (re.compile(r"CHEM|PLAST|DOW\b|LYONDELL", re.I), "hazmat", "18", "Chemical products"),
    (re.compile(r"STEEL|METAL|SCRAP|ALUMIN", re.I), "metal_sheet", "11", "Nonmetal minerals"),
    (re.compile(r"WASTE|LANDFILL|RECYCL", re.I), "waste_scrap", "41", "Waste/scrap"),
]


def normalize_shipper(name: str | None) -> str:
    if not name:
        return ""
    s = name.upper().strip()
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for drop in (" LLC", " INC", " CORP", " CO ", " LTD", " LP"):
        s = s.replace(drop, " ")
    return re.sub(r"\s+", " ", s).strip()


def infer_commodity_from_shipper(shipper_norm: str) -> tuple[str, str, str, str, str]:
    """Returns commodity_inferred, sctg2, sctg2_name, confidence, method."""
    for pat, lane, sctg, label in SHIPPER_COMMODITY_HINTS:
        if pat.search(shipper_norm):
            conf = LANE_TO_SCTG.get(lane, ("", "", "medium"))[2]
            return lane, sctg, label, conf, "shipper_name_pattern"
    return "general_freight", "31", "Mixed freight", "weak", "shipper_default_mixed_freight"


def infer_commodity_from_inspection(
    *,
    hazmat: str | None,
    cargo_tank: str | None,
    shipper_norm: str,
) -> tuple[str, str, str, str, str]:
    if hazmat and str(hazmat).upper() == "Y":
        if cargo_tank in ("406", "407", "331"):
            return "petroleum_chem", "17", "Petroleum products", "strong", "hazmat_plus_tanker_code"
        return "hazmat", "18", "Chemical products", "medium", "hazmat_placard"
    if cargo_tank in ("406", "407", "331"):
        return "tanker", "17", "Petroleum products", "medium", "cargo_tank_code"
    shipper_inf = infer_commodity_from_shipper(shipper_norm)
    if shipper_inf[3] in ("strong", "medium"):
        return shipper_inf
    return "general_freight", "31", "Mixed freight", "weak", "inspection_context_default"


def stable_id(*parts: str) -> str:
    raw = "|".join(p for p in parts if p)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def write_receipt(
    path: Path,
    *,
    command: str,
    version: str,
    started_at: str,
    input_files: list[str],
    input_fingerprints: dict[str, Any],
    output_files: list[str],
    row_counts: dict[str, int],
    warnings: list[str],
    missing_data_flags: list[str],
    success: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "command": command,
        "version": version,
        "started_at": started_at,
        "finished_at": utc_now(),
        "repo_root": str(ROOT),
        "input_files": input_files,
        "input_file_fingerprints": input_fingerprints,
        "output_files": output_files,
        "row_counts": row_counts,
        "warnings": warnings,
        "missing_data_flags": missing_data_flags,
        "success": success,
    }
    if extra:
        payload.update(extra)
    write_json(path, payload)
    return payload


def export_parquet(rows: list[dict[str, Any]], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        pq.write_table(pa.table({}), dest)
        return
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, dest)


def fingerprint_paths(paths: list[Path]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for p in paths:
        if p and p.exists():
            key = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
            out[key] = file_fingerprint(p)
    return out


class CommandTimer:
    def __init__(self) -> None:
        self.started_at = utc_now()
        self._t0 = time.monotonic()

    @property
    def elapsed_sec(self) -> float:
        return round(time.monotonic() - self._t0, 2)
