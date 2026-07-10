"""Iran–oil origin pressure: EIA crude + Census IMDB → THG + public receipt."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, UNWRAPPED
from catalog.graph.schema_v1 import OUTPUTS
from catalog.source_truth import require_path
from catalog.util import write_json

RECEIPT_PATH = BUILD_REPORTS / "thg_iran_oil_v1.json"
IRAN_CTY = "5070"
IRAN_ISO = "IRN"
SCTG_PET = "17"
EIA_US_MONTHLY = "PET_IMPORTS.CTY_IR-US-ALL.M"
EIA_US_ANNUAL = "PET_IMPORTS.CTY_IR-US-ALL.A"
EIA_HOUSTON_MONTHLY = "PET_IMPORTS.CTY_IR-PT_5301-ALL.M"


def _pet_path() -> Path:
    return require_path("pet_imports")


def _imdb_zip() -> Path | None:
    trade = UNWRAPPED / "trade"
    for release_dir in sorted(trade.glob("release=*"), reverse=True):
        for z in sorted(release_dir.glob("IMDB*.ZIP"), reverse=True):
            if z.stat().st_size > 1_000_000:
                return z
    return None


def parse_eia_iran(pet: Path | None = None) -> dict[str, Any]:
    path = pet or _pet_path()
    monthly: list[dict[str, Any]] = []
    annual: list[dict[str, Any]] = []
    houston: list[dict[str, Any]] = []
    last_updated = None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or "CTY_IR-" not in line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("geography") != IRAN_ISO:
                continue
            sid = obj.get("series_id", "")
            last_updated = obj.get("last_updated") or last_updated
            points = [
                {"period": str(p), "kbbl": float(v)}
                for p, v in (obj.get("data") or [])
                if v is not None
            ]
            if sid == EIA_US_MONTHLY:
                monthly = sorted(points, key=lambda r: r["period"])
            elif sid == EIA_US_ANNUAL:
                annual = sorted(points, key=lambda r: r["period"])
            elif sid == EIA_HOUSTON_MONTHLY:
                houston = sorted(points, key=lambda r: r["period"])
    return {
        "source_path": str(path.relative_to(ROOT)),
        "source_mtime": path.stat().st_mtime,
        "last_updated": last_updated,
        "monthly": monthly,
        "annual": annual,
        "houston_monthly": houston,
    }


def parse_imdb_iran(zip_path: Path | None = None) -> dict[str, Any]:
    zpath = zip_path or _imdb_zip()
    if not zpath:
        return {"source_path": None, "country": None, "detail": []}

    country_row = None
    detail: list[dict[str, Any]] = []
    with zipfile.ZipFile(zpath) as zf:
        names = {n.upper(): n for n in zf.namelist()}
        cty_name = names.get("IMP_CTY.TXT")
        if cty_name:
            with zf.open(cty_name) as fh:
                for raw in fh:
                    line = raw.decode("latin-1", errors="ignore")
                    if not line.startswith(IRAN_CTY):
                        continue
                    year = line[34:38].strip()
                    month = line[38:40].strip()
                    country_row = {
                        "cty_code": IRAN_CTY,
                        "cty_name": line[4:34].strip(),
                        "month": f"{year}{month}",
                        "cards_mo": int(line[40:55].strip() or 0),
                        "con_val_mo": int(line[55:70].strip() or 0),
                        "gen_val_mo": int(line[130:145].strip() or 0),
                        "ves_val_mo": int(line[220:235].strip() or 0),
                        "ves_wgt_mo": int(line[235:250].strip() or 0),
                        "con_val_yr": int(line[325:340].strip() or 0),
                    }
                    break
        detl_name = names.get("IMP_DETL.TXT")
        if detl_name:
            with zf.open(detl_name) as fh:
                for raw in fh:
                    line = raw.decode("latin-1", errors="ignore")
                    if line[10:14] != IRAN_CTY:
                        continue
                    hs = line[0:10].strip()
                    year = line[22:26].strip()
                    month = line[26:28].strip()
                    cards = int(line[28:43].strip() or 0)
                    con_val = int(line[73:88].strip() or 0)
                    if con_val <= 0 and cards <= 0:
                        continue
                    detail.append(
                        {
                            "hs": hs,
                            "month": f"{year}{month}",
                            "cards": cards,
                            "con_val": con_val,
                        }
                    )

    detail.sort(key=lambda r: -r["con_val"])
    return {
        "source_path": str(zpath.relative_to(ROOT)),
        "source_mtime": zpath.stat().st_mtime,
        "country": country_row,
        "detail": detail[:20],
    }


def _truck_pet_context(month: str | None = None) -> dict[str, Any]:
    from catalog.graph.month_picker import pick_snapshot_month

    scores = OUTPUTS["change_scores"]
    events = OUTPUTS["events"]
    out: dict[str, Any] = {
        "snapshot_month": month,
        "truck_observation_delta_pct": None,
        "truck_weight": None,
        "prior_weight": None,
    }
    if not scores.exists():
        out.update(
            {
                "snapshot_month": "202606",
                "truck_observation_delta_pct": 55.1,
                "truck_weight": 1576.0,
                "prior_weight": 1016.0,
                "prior_month": "202605",
                "source": "demo_fallback",
            }
        )
        return out

    con = duckdb.connect()
    if not month and events.exists():
        month = pick_snapshot_month(events, con=con)
    if not month:
        month = con.execute(
            f"SELECT MAX(snapshot_month) FROM read_parquet('{scores}') WHERE sctg2 = '{SCTG_PET}' AND state IS NULL"
        ).fetchone()[0]

    row = con.execute(
        f"""
        SELECT snapshot_month, truck_observation_delta_pct, truck_weight, prior_weight
        FROM read_parquet('{scores}')
        WHERE sctg2 = '{SCTG_PET}' AND snapshot_month = ?
          AND (state IS NULL OR CAST(state AS VARCHAR) = '')
        LIMIT 1
        """,
        [month],
    ).fetchone()
    if not row:
        row = con.execute(
            f"""
            SELECT snapshot_month, truck_observation_delta_pct, truck_weight, prior_weight
            FROM read_parquet('{scores}')
            WHERE sctg2 = '{SCTG_PET}' AND snapshot_month = ?
            LIMIT 1
            """,
            [month],
        ).fetchone()
    if row:
        out = {
            "snapshot_month": row[0],
            "truck_observation_delta_pct": float(row[1] or 0),
            "truck_weight": float(row[2] or 0),
            "prior_weight": float(row[3] or 0) if row[3] is not None else None,
            "source": "temporal_change_scores",
        }
    return out


def classify_join(eia_months: set[str], truck_month: str | None) -> str:
    if not truck_month:
        return "no_truck_window"
    if not eia_months:
        return "no_iran_eia"
    if truck_month in eia_months:
        return "aligned"
    # same calendar year window soft check
    if any(m[:4] == truck_month[:4] for m in eia_months):
        return "diverge"
    return "no_iran_eia_in_window"


def build_iran_oil_receipt(*, truck_month: str | None = None) -> dict[str, Any]:
    eia = parse_eia_iran()
    imdb = parse_imdb_iran()
    truck = _truck_pet_context(truck_month)
    eia_months = {r["period"] for r in eia["monthly"]}
    snap = truck.get("snapshot_month")
    join = classify_join(eia_months, snap)
    last = eia["monthly"][-1] if eia["monthly"] else None
    country = imdb.get("country") or {}

    receipt = {
        "scan_type": "thg_iran_oil_v1",
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "thesis": "truck=sensor commodity=signal; Iran origin_pressure tags geopolitics onto SCTG 17",
        "sctg2": SCTG_PET,
        "sctg2_name": "Petroleum products",
        "join": join,
        "join_note": (
            "US truck petroleum haul delta and EIA Iran crude do not share the same month — "
            "do not claim Iran caused the truck spike."
            if join in {"diverge", "no_iran_eia_in_window"}
            else "Iran EIA crude and truck snapshot share a month window."
        ),
        "eia_iran": {
            "last_month": last["period"] if last else None,
            "last_kbbl": last["kbbl"] if last else None,
            "series": EIA_US_MONTHLY,
            "monthly": eia["monthly"],
            "annual": eia["annual"],
            "houston_monthly": eia["houston_monthly"],
            "source_path": eia["source_path"],
            "series_last_updated": eia["last_updated"],
        },
        "census_iran": {
            "cty_code": IRAN_CTY,
            "month": country.get("month"),
            "con_val_mo": country.get("con_val_mo"),
            "con_val_yr": country.get("con_val_yr"),
            "ves_val_mo": country.get("ves_val_mo"),
            "ves_wgt_mo": country.get("ves_wgt_mo"),
            "top_hs": imdb.get("detail") or [],
            "source_path": imdb.get("source_path"),
            "note": "May 2026 Iran→US goods are non-oil (e.g. carpets); vessel crude weight is zero in IMDB month.",
        },
        "truck_petroleum": truck,
        "public_url": "https://mabeline.vercel.app/iran",
    }
    write_json(RECEIPT_PATH, receipt)
    return receipt


def append_iran_oil_events(
    con: duckdb.DuckDBPyConnection,
    *,
    input_files: list[str],
    warnings: list[str],
) -> int:
    count = 0
    try:
        eia = parse_eia_iran()
        pet_rel = eia["source_path"]
        pet_mtime = eia["source_mtime"]
        input_files.append(pet_rel)

        rows: list[tuple[str, str, float, str]] = []
        for r in eia["monthly"]:
            rows.append((r["period"], SCTG_PET, r["kbbl"], "month"))
        for r in eia["annual"]:
            rows.append((r["period"], SCTG_PET, r["kbbl"], "year"))

        if rows:
            values = ",".join(
                f"('{m}','{s}',{w},'{g}')" for m, s, w, g in rows
            )
            con.execute(
                f"""
                CREATE OR REPLACE TABLE iran_eia AS
                SELECT * FROM (VALUES {values})
                AS t(event_month, sctg2, weight, event_grain)
                """
            )
            con.execute(
                """
                INSERT INTO all_events
                SELECT
                  md5('origin_pressure|IRN|' || event_grain || '|' || event_month) AS event_id,
                  'origin_pressure' AS edge_type,
                  'country' AS src_type, 'IRN' AS src_id,
                  'commodity' AS dst_type, sctg2 AS dst_id,
                  event_month AS event_time, event_grain,
                  weight, 'strong' AS confidence,
                  'eia_pet_imports_iran_us' AS inference_method,
                  'maritime' AS source_family,
                  ? AS source_path, ?::BIGINT AS source_mtime,
                  json_object(
                    'origin', 'IRN',
                    'destination', 'US',
                    'series', 'PET_IMPORTS.CTY_IR-US-ALL',
                    'units', 'thousand_barrels',
                    'port_hint', 'Houston'
                  ) AS attrs_json
                FROM iran_eia
                """,
                [pet_rel, int(pet_mtime)],
            )
            count += len(rows)
    except FileNotFoundError:
        warnings.append("eia_iran_missing")

    imdb = parse_imdb_iran()
    if not imdb.get("source_path"):
        warnings.append("imdb_iran_missing")
        return count

    input_files.append(imdb["source_path"])
    country = imdb.get("country")
    detail = imdb.get("detail") or []
    trade_rows: list[tuple[str, str, float, str]] = []
    if country and country.get("con_val_mo", 0) > 0:
        trade_rows.append(
            (
                country["month"],
                SCTG_PET if (country.get("ves_wgt_mo") or 0) > 0 else "31",
                float(country["con_val_mo"]),
                "country_total",
            )
        )
    for d in detail:
        hs = d["hs"]
        sctg = SCTG_PET if hs.startswith("27") else "31"
        trade_rows.append((d["month"], sctg, float(d["con_val"]), hs))

    if trade_rows:
        # dedupe by month+sctg+hs key via md5 in SQL
        values = ",".join(
            f"('{m}','{s}',{w},'{h}')" for m, s, w, h in trade_rows
        )
        con.execute(
            f"""
            CREATE OR REPLACE TABLE iran_imdb AS
            SELECT * FROM (VALUES {values})
            AS t(event_month, sctg2, weight, hs_or_total)
            """
        )
        con.execute(
            """
            INSERT INTO all_events
            SELECT
              md5('trade_import|IRN|' || sctg2 || '|' || event_month || '|' || hs_or_total) AS event_id,
              'trade_import' AS edge_type,
              'country' AS src_type, 'IRN' AS src_id,
              'commodity' AS dst_type, sctg2 AS dst_id,
              event_month AS event_time, 'month' AS event_grain,
              weight, 'medium' AS confidence,
              'census_imdb_iran_5070' AS inference_method,
              'trade' AS source_family,
              ? AS source_path, ?::BIGINT AS source_mtime,
              json_object(
                'cty_code', '5070',
                'cty_name', 'Iran',
                'hs_or_total', hs_or_total,
                'units', 'usd_con_val'
              ) AS attrs_json
            FROM iran_imdb
            """,
            [imdb["source_path"], int(imdb["source_mtime"])],
        )
        count += len(trade_rows)

    return count
