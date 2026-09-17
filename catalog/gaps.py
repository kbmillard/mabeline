from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from catalog.config import BUILD_REPORTS, UNWRAPPED, today_id, utc_now
from catalog.util import append_log, file_signature, write_json

SSL_CTX = ssl.create_default_context()
DOWNLOAD_QUEUE_PATH = BUILD_REPORTS / "newest_first_download_queue_v1.json"
STUB_BYTES = 500
USER_AGENT = "mabel-catalog/1.0 (+local; census-imdb-bulk)"

def _download_specs(release_id: str) -> list[dict]:
    """Gap-fill download targets; release_id is UTC YYYY-MM-DD (today_id())."""
    return [
    {
        "family": "fmcsa_carriers",
        "url": "https://data.transportation.gov/api/views/az4n-8mr2/rows.csv?accessType=DOWNLOAD",
        "dest": "company_census.csv",
        "optional": True,
        "refresh_after_days": 7,
        "cadence": "weekly",
        "transport": True,
        "timeout": 600,
    },
    {
        "family": "fmcsa_carriers",
        "url": "https://data.transportation.gov/api/views/fx4q-ay7w/rows.csv?accessType=DOWNLOAD",
        "dest": "mcmis/vehicle_inspection_file.csv",
        "optional": True,
        "refresh_after_days": 7,
        "cadence": "weekly",
        "transport": True,
        "timeout": 900,
    },
    {
        "family": "maritime",
        "url": "https://www.eia.gov/opendata/bulk/PET_IMPORTS.zip",
        "dest": f"release={release_id}/PET_IMPORTS.zip",
        "optional": True,
        "refresh_after_days": 30,
        "cadence": "monthly",
        "transport": True,
        "timeout": 300,
    },
    {
        "family": "rail",
        "url": "https://www.eia.gov/opendata/bulk/COAL.zip",
        "dest": f"release={release_id}/COAL.zip",
        "optional": True,
        "refresh_after_days": 30,
        "cadence": "monthly",
        "transport": True,
        "timeout": 300,
    },
    {
        "family": "stb_rail",
        "url": "https://opendata.stb.gov/api/explore/v2.1/catalog/datasets/ep724-element-10/exports/csv?delimiter=%2C&list_separator=%3B",
        "dest": f"release={release_id}/ep724-element-10.csv",
        "optional": True,
        "refresh_after_days": 7,
        "cadence": "weekly",
        "transport": True,
        "timeout": 120,
    },
    {
        "family": "stb_rail",
        "url": "https://opendata.stb.gov/api/explore/v2.1/catalog/datasets/ep724-average-terminal-dwell-time/exports/csv?delimiter=%2C&list_separator=%3B",
        "dest": f"release={release_id}/ep724-average-terminal-dwell-time.csv",
        "optional": True,
        "refresh_after_days": 7,
        "cadence": "weekly",
        "transport": True,
        "timeout": 180,
    },
    {
        "family": "stb_rail",
        "url": "https://opendata.stb.gov/api/explore/v2.1/catalog/datasets/ep724-public-data/exports/csv?delimiter=%2C&list_separator=%3B",
        "dest": f"release={release_id}/ep724-public-data.csv",
        "optional": True,
        "refresh_after_days": 7,
        "cadence": "weekly",
        "transport": True,
        "timeout": 1800,
    },
    {
        "family": "sec_filings",
        "url": "https://www.sec.gov/files/company_tickers.json",
        "dest": "company_tickers.json",
        "optional": False,
        "refresh_after_days": 30,
        "cadence": "monthly",
        "transport": False,
        "timeout": 120,
    },
    {
        "family": "epa_toxics",
        "url": "https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2024_US/csv",
        "dest": f"release={release_id}/tri_2024_US_basic.csv",
        "optional": True,
        "refresh_after_days": 365,
        "cadence": "annual",
        "transport": False,
        "timeout": 120,
    },
    {
        "family": "nrc_nuclear",
        "url": "https://www.nrc.gov/reading-rm/doc-collections/maps/reactors-operating.xls",
        "dest": "reactors-operating.xls",
        "optional": True,
        "refresh_after_days": 7,
        "cadence": "weekly",
        "transport": False,
        "timeout": 120,
    },
    {
        "family": "offshore_energy",
        "url": "https://www.data.bsee.gov/Platform/Files/platmastfixed.zip",
        "dest": f"release={release_id}/bsee_platmastfixed.zip",
        "optional": True,
        "refresh_after_days": 30,
        "cadence": "monthly",
        "transport": True,
        "timeout": 120,
    },
    {
        "family": "offshore_energy",
        "url": "https://www.data.bsee.gov/Platform/Files/platstrufixed.zip",
        "dest": f"release={release_id}/bsee_platstrufixed.zip",
        "optional": True,
        "refresh_after_days": 30,
        "cadence": "monthly",
        "transport": True,
        "timeout": 120,
    },
    ]


# Transport-first, newest-first. refresh_after_days=0 means only fetch if missing.
DOWNLOADS = _download_specs  # backwards-compat alias; call with today_id()

MANUAL_DOWNLOADS: list[dict] = [
    {
        "priority": "P3",
        "source": "cfs_2023_survey",
        "why": "Next Census shipment microdata — beats CFS 2022 when released",
        "action": "Watch https://www.census.gov/programs-surveys/cfs/data/datasets.html",
        "dest_hint": "_unwrapped/trade/release={date}/cfs_2023_pums/",
        "note": "Not published yet as of Jul 2026 — only true wait-state source",
    },
    {
        "priority": "OPTIONAL",
        "source": "census_trade_api_key",
        "why": "Optional JSON API slice if IMDB/EXDB bulk is insufficient",
        "action": "Sign up free at https://api.census.gov/data/key_signup.html",
        "env_var": "CENSUS_API_KEY",
        "then": "Re-run: bin/mabel-catalog gaps (adds API JSON alongside IMDB bulk)",
        "note": "IMDB/EXDB monthly ZIPs at census.gov/foreign-trade/data/IMDB.html need no key",
    },
]

GAP_REGISTER_PATH = BUILD_REPORTS / "open_source_gap_register_v1.json"

KNOWN_GAPS = [
    {
        "source_name": "cfs_2023",
        "priority": "P3",
        "current_status": "not_released",
        "missing_reason": "Latest CFS on disk is 2022 survey; 2023 not published yet",
        "build_blocker": False,
    },
    {
        "source_name": "commercial_enrichment_bulk",
        "priority": "DEFERRED",
        "current_status": "not_on_disk",
        "missing_reason": "No free national bulk for D&B/ZoomInfo/Pitchbook/etc.",
        "build_blocker": False,
    },
    {
        "source_name": "overture_places_conus",
        "priority": "EXTERNAL",
        "current_status": "postgres_sweeper_dev",
        "missing_reason": "Excluded from _unwrapped by policy; lives in Postgres sweeper_dev.overture_places",
        "build_blocker": False,
    },
    {
        "source_name": "wikidata_full_parquet",
        "priority": "DEFERRED",
        "current_status": "local_reference_exists",
        "missing_reason": "95GB bz2 dump deferred for parquet conversion in this run",
        "build_blocker": False,
    },
]


def _file_age_days(path: Path) -> float | None:
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return (datetime.now(timezone.utc) - mtime).total_seconds() / 86400


def _is_html_stub(path: Path) -> bool:
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:400].lower()
    except OSError:
        return True
    return "<html" in head or "missing key" in head or "api key" in head


def _is_bad_on_disk(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return True
    if path.stat().st_size < STUB_BYTES:
        return True
    if _is_html_stub(path):
        return True
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path, "r") as zf:
                if zf.testzip() is not None:
                    return True
        except (zipfile.BadZipFile, OSError):
            return True
    return False


def _needs_refresh(path: Path, refresh_after_days: int) -> bool:
    if _is_bad_on_disk(path):
        return True
    if refresh_after_days <= 0:
        return False
    age = _file_age_days(path)
    if age is None:
        return True
    return age >= refresh_after_days


def _download(url: str, dest: Path, timeout: int = 60) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as resp:
        data = resp.read()
    if len(data) < 512 and b"Missing Key" in data:
        raise ValueError("response looks like missing API key page")
    if len(data) < STUB_BYTES and b"<html" in data[:512].lower():
        raise ValueError("response looks like HTML error page")
    dest.write_bytes(data)
    if dest.suffix.lower() == ".zip":
        with zipfile.ZipFile(dest, "r") as zf:
            if zf.testzip() is not None:
                dest.unlink(missing_ok=True)
                raise ValueError("downloaded zip failed integrity check")


def _recent_trade_months(count: int = 3) -> list[tuple[int, int]]:
    """Walk backward from prior calendar month for Census IMDB/EXDB bulk."""
    now = datetime.now(timezone.utc)
    year, month = now.year, now.month - 1
    out: list[tuple[int, int]] = []
    for _ in range(count):
        if month == 0:
            month = 12
            year -= 1
        out.append((year, month))
        month -= 1
    return out


def _census_trade_bulk_specs(release_id: str) -> list[dict]:
    """Public IMDB/EXDB monthly ZIPs — no API key (census.gov/foreign-trade/data/IMDB.html)."""
    base = f"release={release_id}"
    specs: list[dict] = []
    for year, month in _recent_trade_months(3):
        code = f"{year % 100:02d}{month:02d}"
        specs.extend(
            [
                {
                    "family": "trade",
                    "url": f"https://www.census.gov/trade/downloads/{year}/Merch/im_m/IMDB{code}.ZIP",
                    "dest": f"{base}/IMDB{code}.ZIP",
                    "optional": True,
                    "refresh_after_days": 30,
                    "cadence": "monthly",
                    "transport": True,
                    "timeout": 900,
                },
                {
                    "family": "trade",
                    "url": f"https://www.census.gov/trade/downloads/{year}/Merch/ex_m/EXDB{code}.ZIP",
                    "dest": f"{base}/EXDB{code}.ZIP",
                    "optional": True,
                    "refresh_after_days": 30,
                    "cadence": "monthly",
                    "transport": True,
                    "timeout": 900,
                },
            ]
        )
    return specs


def _stb_r1_specs() -> list[dict]:
    """Class I R-1 / S250 direct from stb.gov/wp-content/uploads (not opendata API)."""
    uploads = [
        ("R1-BNSF-2025.xlsx", "https://www.stb.gov/wp-content/uploads/R1-BNSF-2025.xlsx"),
        ("R1-NS-2025.xlsx", "https://www.stb.gov/wp-content/uploads/R1-NS-2025.xlsx"),
        ("R1-GTC-2025.xlsx", "https://www.stb.gov/wp-content/uploads/R1-GTC-2025.xlsx"),
        ("R1-SOO-KCSR-2025.xlsx", "https://www.stb.gov/wp-content/uploads/R1-SOO-KCSR-2025.xlsx"),
        ("R1-CSX-2025.zip", "https://www.stb.gov/wp-content/uploads/R1-CSX-2025.zip"),
        ("R1-UP-2025.zip", "https://www.stb.gov/wp-content/uploads/R1-UP-2025.zip"),
        ("S250-BNSF-2025.xlsx", "https://www.stb.gov/wp-content/uploads/S250-BNSF-2025.xlsx"),
        ("S250-NS-2025.xlsx", "https://www.stb.gov/wp-content/uploads/S250-NS-2025.xlsx"),
        ("S250-GTC-2025.xlsx", "https://www.stb.gov/wp-content/uploads/S250-GTC-2025.xlsx"),
        ("S250-SOO-KCSR-2025.xlsx", "https://www.stb.gov/wp-content/uploads/S250-SOO-KCSR-2025.xlsx"),
        ("S250-CSX-2025.xlsx", "https://www.stb.gov/wp-content/uploads/S250-CSX-2025.xlsx"),
        ("S250-UP-2025.xlsx", "https://www.stb.gov/wp-content/uploads/S250-UP-2025.xlsx"),
    ]
    return [
        {
            "family": "stb_rail",
            "url": url,
            "dest": dest,
            "optional": True,
            "refresh_after_days": 30,
            "cadence": "annual",
            "transport": True,
            "timeout": 600,
        }
        for dest, url in uploads
    ]


def _census_trade_specs(release_id: str) -> list[dict]:
    key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not key:
        return []
    # Latest complete month: prior month from today
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month - 1
    if month == 0:
        month = 12
        year -= 1
    mm = f"{month:02d}"
    base = f"release={release_id}"
    return [
        {
            "family": "trade",
            "url": (
                "https://api.census.gov/data/timeseries/intltrade/exports/hs"
                f"?get=E_COMMODITY,E_COMMODITY_LDESC,ALL_VAL_MO&YEAR={year}&MONTH={mm}&key={key}"
            ),
            "dest": f"{base}/census_exports_hs_{year}-{mm}.json",
            "optional": True,
            "refresh_after_days": 30,
            "cadence": "monthly",
            "transport": True,
            "timeout": 120,
        },
        {
            "family": "trade",
            "url": (
                "https://api.census.gov/data/timeseries/intltrade/imports/hs"
                f"?get=I_COMMODITY,I_COMMODITY_LDESC,ALL_VAL_MO&YEAR={year}&MONTH={mm}&key={key}"
            ),
            "dest": f"{base}/census_imports_hs_{year}-{mm}.json",
            "optional": True,
            "refresh_after_days": 30,
            "cadence": "monthly",
            "transport": True,
            "timeout": 120,
        },
    ]


def fill_gaps(log_path: Path | None = None) -> dict:
    release_id = today_id()
    results = []
    specs = (
        _download_specs(release_id)
        + _census_trade_bulk_specs(release_id)
        + _stb_r1_specs()
        + _census_trade_specs(release_id)
    )

    for spec in specs:
        family = spec["family"]
        dest = UNWRAPPED / family / spec["dest"]
        refresh_days = spec.get("refresh_after_days", 0)
        entry = {
            "family": family,
            "dest": spec["dest"],
            "url": spec["url"],
            "cadence": spec.get("cadence"),
            "transport": spec.get("transport", False),
            "status": "skipped",
        }

        if dest.exists() and not _needs_refresh(dest, refresh_days):
            entry["status"] = "fresh"
            entry["age_days"] = round(_file_age_days(dest) or 0, 1)
            entry.update(file_signature(dest, with_md5=False))
            results.append(entry)
            continue

        if dest.exists():
            entry["prior_age_days"] = round(_file_age_days(dest) or 0, 1)
            if _is_bad_on_disk(dest):
                entry["prior_status"] = "stub_or_corrupt"
                marker = Path(str(dest) + ".unwrap.done")
                marker.unlink(missing_ok=True)

        try:
            timeout = spec.get("timeout", 30 if spec.get("optional", True) else 120)
            t0 = time.time()
            _download(spec["url"], dest, timeout=timeout)
            entry["status"] = "downloaded"
            entry["elapsed_sec"] = round(time.time() - t0, 1)
            entry.update(file_signature(dest, with_md5=False))
            if log_path:
                append_log(log_path, f"gap_fill downloaded {family}/{spec['dest']}")
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            entry["status"] = "error"
            entry["error"] = repr(exc)
            if not spec.get("optional", True):
                entry["status"] = "required_error"
            if log_path:
                append_log(log_path, f"gap_fill error {family}/{spec['dest']}: {exc}")
        results.append(entry)

    manual = list(MANUAL_DOWNLOADS)
    for item in manual:
        if item.get("env_var") == "CENSUS_API_KEY" and not os.environ.get("CENSUS_API_KEY"):
            item["status"] = "optional"

    discovered_on_disk = _discovered_open_sources(release_id)

    queue = {
        "scan_type": "newest_first_download_queue_v1",
        "creed": "newest_first",
        "release_id": release_id,
        "automated_attempts": results,
        "manual_downloads": manual,
        "discovered_on_disk": discovered_on_disk,
        "on_disk_already_newest": [
            {"source": "faf5_freight", "vintage": "FAF5.7.1 tons_2024", "note": "latest national modeled year"},
            {"source": "trade/cfs_2022_pums", "vintage": "2022 survey", "note": "newest CFS until 2023 releases"},
            {"source": "fmc_maritime/oti_licensed_active.csv", "vintage": "on_disk", "note": "600KB active OTI list present"},
            {"source": "nrc_nuclear/reactors-operating.csv", "vintage": "on_disk", "note": "operating reactor registry present"},
            {"source": "atf_firearms/ffl_list_complete_0124.txt", "vintage": "on_disk", "note": "11MB FFL national txt present"},
        ],
        "updated_at": utc_now(),
    }
    write_json(DOWNLOAD_QUEUE_PATH, queue)

    remaining = _remaining_gaps_after_exhaust(release_id, results, discovered_on_disk)

    gap_register = {
        "updated_at": utc_now(),
        "creed": "newest_first",
        "release_id": release_id,
        "gaps": KNOWN_GAPS + remaining,
        "download_attempts": results,
        "manual_queue": str(DOWNLOAD_QUEUE_PATH.relative_to(UNWRAPPED.parent)),
        "exhaust_note": "Open bulk URLs tried before gap register; API key only optional for Census JSON",
    }
    write_json(GAP_REGISTER_PATH, gap_register)
    return gap_register


def _discovered_open_sources(release_id: str) -> list[dict]:
    """Sources already valid on disk — do not list as gaps."""
    checks = [
        ("fmc_maritime", "oti_licensed_active.csv"),
        ("fmc_maritime", "vocc_active.csv"),
        ("nrc_nuclear", "reactors-operating.csv"),
        ("atf_firearms", "ffl_list_complete_0124.txt"),
        ("atf_firearms", "0526-ffl-list.csv"),
        ("fmcsa_carriers", "company_census.csv"),
        ("fmcsa_carriers", "mcmis/vehicle_inspection_file.csv"),
        ("fmcsa_carriers", "insurance/actpendinsur_all_with_history.csv"),
        ("trade", f"release={release_id}/cfs_2022_pums/cfs_2022_pums.csv"),
    ]
    found: list[dict] = []
    for family, rel in checks:
        path = UNWRAPPED / family / rel
        if path.is_file() and not _is_bad_on_disk(path):
            found.append(
                {
                    "family": family,
                    "path": str(path.relative_to(UNWRAPPED.parent)),
                    "bytes": path.stat().st_size,
                }
            )
    trade_release = UNWRAPPED / "trade" / f"release={release_id}"
    if trade_release.is_dir():
        imdb = sorted(trade_release.glob("IMDB*.ZIP"))
        exdb = sorted(trade_release.glob("EXDB*.ZIP"))
        for z in imdb + exdb:
            if not _is_bad_on_disk(z):
                found.append(
                    {
                        "family": "trade",
                        "path": str(z.relative_to(UNWRAPPED.parent)),
                        "bytes": z.stat().st_size,
                        "note": "census_imdb_exdb_bulk",
                    }
                )
    for carrier in ("BNSF", "NS", "GTC", "CSX", "UP", "SOO-KCSR"):
        r1_dir = UNWRAPPED / "stb_rail" / f"R1-{carrier}-2025"
        xlsx = UNWRAPPED / "stb_rail" / f"R1-{carrier}-2025.xlsx"
        zip_path = UNWRAPPED / "stb_rail" / f"R1-{carrier}-2025.zip"
        ok = False
        if zip_path.is_file() and not _is_bad_on_disk(zip_path):
            ok = True
        elif xlsx.is_file() and not _is_bad_on_disk(xlsx):
            ok = True
        elif r1_dir.is_dir() and any(
            p.stat().st_size >= STUB_BYTES for p in r1_dir.rglob("*") if p.is_file() and not p.name.endswith(".unwrap.done")
        ):
            ok = True
        if ok:
            found.append({"family": "stb_rail", "carrier": carrier, "vintage": "R1-2025"})
    return found


def _remaining_gaps_after_exhaust(
    release_id: str,
    attempts: list[dict],
    discovered: list[dict],
) -> list[dict]:
    """Only emit gaps that failed automated open-source fetch or are genuinely absent."""
    remaining: list[dict] = []
    trade_release = UNWRAPPED / "trade" / f"release={release_id}"
    has_imdb = any(
        not _is_bad_on_disk(p) for p in trade_release.glob("IMDB*.ZIP")
    ) if trade_release.is_dir() else False

    errors = [a for a in attempts if a.get("status") == "error"]
    if has_imdb:
        # Census publishes with lag; 404 on current month is normal when prior months exist.
        errors = [
            e
            for e in errors
            if not (e.get("family") == "trade" and e.get("dest", "").endswith(".ZIP"))
        ]
    for err in errors:
        remaining.append(
            {
                "source_name": f"{err['family']}/{err['dest']}",
                "priority": "P2",
                "current_status": "download_error",
                "missing_reason": err.get("error", "unknown"),
                "build_blocker": False,
            }
        )
    if not has_imdb:
        remaining.append(
            {
                "source_name": "census_hs_trade_bulk",
                "priority": "P1",
                "current_status": "download_pending",
                "missing_reason": "IMDB/EXDB bulk not yet on disk after exhaust pass",
                "build_blocker": False,
            }
        )
    stb_carriers = {d.get("carrier") for d in discovered if d.get("family") == "stb_rail"}
    for carrier in ("BNSF", "NS", "GTC"):
        if carrier not in stb_carriers:
            remaining.append(
                {
                    "source_name": f"stb_r1_{carrier.lower()}_2025",
                    "priority": "P1",
                    "current_status": "stub_or_missing",
                    "missing_reason": f"R1-{carrier}-2025 not valid after stb.gov direct fetch",
                    "build_blocker": False,
                }
            )
    offshore_release = UNWRAPPED / "offshore_energy" / f"release={release_id}"
    if offshore_release.is_dir():
        bad_zips = [p for p in offshore_release.glob("*.zip") if _is_bad_on_disk(p)]
        if bad_zips:
            remaining.append(
                {
                    "source_name": "offshore_energy_bsee",
                    "priority": "P2",
                    "current_status": "corrupt_or_stub",
                    "missing_reason": f"{len(bad_zips)} BSEE zip(s) still invalid",
                    "build_blocker": False,
                }
            )
    return remaining
