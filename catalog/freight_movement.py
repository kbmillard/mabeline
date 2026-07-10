"""
FAF5 freight movement analysis — real tonnage and ton-miles from on-disk data.

Uses BTS Freight Analysis Framework (FAF5.7.1): origin-destination flows by mode,
commodity (SCTG2), and distance band. Units in source file are thousand tons,
million dollars, million ton-miles.
"""

from __future__ import annotations

import time
from pathlib import Path

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.source_truth import require_path, resolved_sources_dict
from catalog.util import append_log, write_json

RECEIPT_PATH = BUILD_REPORTS / "freight_movement_receipt_v1.json"


def get_faf_csv() -> Path:
    return require_path("faf5_csv")

MODE_LABELS = {
    "1": "Truck",
    "2": "Rail",
    "3": "Water",
    "4": "Air",
    "5": "Multiple modes",
    "6": "Pipeline",
    "7": "Other/unknown",
}

# Top zones seen in analysis + common hubs (FAF5 domestic region codes)
ZONE_LABELS = {
    "050": "Arkansas",
    "061": "Los Angeles-Long Beach, CA",
    "064": "San Jose-SF-Oakland, CA",
    "129": "Remainder of Illinois",
    "171": "Chicago-Naperville, IL",
    "179": "Remainder of Indiana",
    "190": "Remainder of Iowa",
    "319": "Remainder of Missouri",
    "341": "Remainder of New York",
    "380": "Remainder of Ohio",
    "419": "Remainder of Pennsylvania",
    "484": "Dallas-Fort Worth, TX",
    "486": "Houston-The Woodlands, TX",
    "489": "Remainder of Texas",
    "559": "Remainder of Wisconsin",
}

SCTG2_LABELS = {
    "01": "Animal feed",
    "02": "Cereal grains",
    "03": "Other ag products",
    "07": "Meat",
    "11": "Natural sands",
    "12": "Gasoline & jet fuel",
    "15": "Nonmetal minerals",
    "16": "Natural gas",
    "17": "Petroleum products",
    "18": "Chemical products",
    "19": "Coal",
    "31": "Mixed freight",
    "41": "Waste/scrap",
}


def _zone(code: str | None) -> str:
    if not code:
        return "unknown"
    return ZONE_LABELS.get(code, f"FAF zone {code}")


def _corridor(orig: str, dest: str) -> str:
    return f"{_zone(orig)} → {_zone(dest)}"


def run_freight_movement(*, year: str = "2024") -> dict:
    faf = get_faf_csv()
    if not faf.exists():
        raise FileNotFoundError(f"FAF5 file missing: {faf}")

    tons_col = f"tons_{year}"
    tmiles_col = f"tmiles_{year}"
    value_col = f"value_{year}"
    prior_year = str(int(year) - 1)
    prior_tons = f"tons_{prior_year}"

    con = duckdb.connect()
    t0 = time.monotonic()
    path = str(faf)

    totals = con.execute(
        f"""
        SELECT
          COUNT(*)::BIGINT AS rows,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS total_ktons,
          ROUND(SUM(TRY_CAST({tmiles_col} AS DOUBLE)), 2) AS total_mtmiles,
          ROUND(SUM(TRY_CAST({value_col} AS DOUBLE)), 2) AS total_musd
        FROM read_csv_auto(?, header=true)
        """,
        [path],
    ).fetchone()

    by_mode = con.execute(
        f"""
        SELECT
          dms_mode,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons,
          ROUND(SUM(TRY_CAST({tmiles_col} AS DOUBLE)), 2) AS mtmiles,
          ROUND(100.0 * SUM(TRY_CAST({tons_col} AS DOUBLE))
            / SUM(SUM(TRY_CAST({tons_col} AS DOUBLE))) OVER (), 2) AS pct_tons
        FROM read_csv_auto(?, header=true)
        GROUP BY 1
        ORDER BY ktons DESC
        """,
        [path],
    ).fetchall()

    corridors = con.execute(
        f"""
        SELECT
          dms_orig,
          dms_dest,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons,
          ROUND(SUM(TRY_CAST({tmiles_col} AS DOUBLE)), 2) AS mtmiles
        FROM read_csv_auto(?, header=true)
        WHERE dms_orig IS NOT NULL AND dms_dest IS NOT NULL
        GROUP BY 1, 2
        ORDER BY ktons DESC
        LIMIT 20
        """,
        [path],
    ).fetchall()

    commodities = con.execute(
        f"""
        SELECT
          sctg2,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons,
          ROUND(SUM(TRY_CAST({tmiles_col} AS DOUBLE)), 2) AS mtmiles
        FROM read_csv_auto(?, header=true)
        GROUP BY 1
        ORDER BY ktons DESC
        LIMIT 15
        """,
        [path],
    ).fetchall()

    yoy_modes = con.execute(
        f"""
        SELECT
          dms_mode,
          ROUND(SUM(TRY_CAST({prior_tons} AS DOUBLE)), 2) AS ktons_prior,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons,
          ROUND(100.0 * (SUM(TRY_CAST({tons_col} AS DOUBLE)) - SUM(TRY_CAST({prior_tons} AS DOUBLE)))
            / NULLIF(SUM(TRY_CAST({prior_tons} AS DOUBLE)), 0), 2) AS yoy_pct
        FROM read_csv_auto(?, header=true)
        GROUP BY 1
        ORDER BY yoy_pct DESC
        """,
        [path],
    ).fetchall()

    elapsed = round(time.monotonic() - t0, 2)

    receipt = {
        "scan_type": "freight_movement_faf5_v1",
        "source": str(faf.relative_to(ROOT)),
        "source_truth": resolved_sources_dict().get("faf5_csv"),
        "dataset": "FAF5.7.1 — BTS/FHWA Freight Analysis Framework",
        "year": year,
        "units": {
            "tons": "thousand tons (kt)",
            "tmiles": "million ton-miles (M tm)",
            "value": "million USD",
        },
        "what_this_is": (
            "Modeled national freight flows by origin-destination FAF zone, mode, "
            "and commodity. Not live telemetry and not company-level shipment ledgers."
        ),
        "what_this_is_not": [
            "Real-time freight in motion",
            "Per-carrier tonnage (use FMCSA census for fleet registry only)",
            "Port TEU / rail carload event streams",
        ],
        "totals": {
            "rows": int(totals[0]),
            "thousand_tons": float(totals[1]),
            "million_ton_miles": float(totals[2]),
            "million_usd_value": float(totals[3]),
            "billion_tons_equiv": round(float(totals[1]) / 1_000_000, 3),
        },
        "by_mode": [
            {
                "mode": MODE_LABELS.get(str(m) if m else "", str(m) or "unknown"),
                "thousand_tons": float(t),
                "million_ton_miles": float(tm),
                "pct_of_tons": float(p),
            }
            for m, t, tm, p in by_mode
            if m
        ],
        "top_corridors": [
            {
                "orig": o,
                "dest": d,
                "corridor": _corridor(o, d),
                "thousand_tons": float(t),
                "million_ton_miles": float(tm),
            }
            for o, d, t, tm in corridors
        ],
        "top_commodities_sctg2": [
            {
                "sctg2": s,
                "commodity": SCTG2_LABELS.get(s, f"SCTG {s}"),
                "thousand_tons": float(t),
                "million_ton_miles": float(tm),
            }
            for s, t, tm in commodities
        ],
        "yoy_mode_growth": [
            {
                "mode": MODE_LABELS.get(str(m) if m else "", str(m) or "unknown"),
                f"thousand_tons_{prior_year}": float(p),
                f"thousand_tons_{year}": float(c),
                "yoy_pct": float(y) if y is not None else None,
            }
            for m, p, c, y in yoy_modes
            if m
        ],
        "elapsed_sec": elapsed,
        "dedupe_method": "aggregate_sum_by_dimension",
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} freight_movement_receipt_v1.json status=ok",
    )
    return receipt
