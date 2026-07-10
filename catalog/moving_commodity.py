"""
Moving Commodity v1 — tie what's moving a lot.

Simple thesis:
  commodity moving a lot = the signal

Tie path:
  SCTG code
    ├─ FAF5 thousand tons + % of national flow (2024)
    ├─ CFS million tons + % of shipments (2022)
    ├─ primary mode (truck / rail / pipeline / water)
    └─ top corridor (where that commodity moves most)

Run: bin/mabel-catalog moving-commodity
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any

import duckdb

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.freight_movement import MODE_LABELS, SCTG2_LABELS, _corridor, _zone, get_faf_csv
from catalog.source_truth import require_path, resolved_sources_dict
from catalog.transport_economy import _cfs_by_sctg, _faf5_by_sctg
from catalog.util import append_log, write_json

RECEIPT_PATH = BUILD_REPORTS / "moving_commodity_v1.json"
TRANSPORT_RECEIPT = BUILD_REPORTS / "transport_economy_v1.json"
EXPORTS_DIR = ROOT / "exports"
CSV_OPTS = "header=true, ignore_errors=true"


def get_cfs_csv() -> Path:
    return require_path("cfs_2022_pums")


def _faf5_top_corridors(con: duckdb.DuckDBPyConnection, sctg: str, year: str = "2024", limit: int = 3) -> list[dict]:
    faf = get_faf_csv()
    if not faf.exists():
        return []
    tons_col = f"tons_{year}"
    path = str(faf)
    rows = con.execute(
        f"""
        SELECT dms_orig, dms_dest,
          ROUND(SUM(TRY_CAST({tons_col} AS DOUBLE)), 2) AS ktons
        FROM read_csv_auto(?, {CSV_OPTS})
        WHERE sctg2 = ?
        GROUP BY 1, 2 ORDER BY 3 DESC LIMIT ?
        """,
        [path, sctg, limit],
    ).fetchall()
    return [
        {
            "corridor": _corridor(o, d),
            "thousand_tons": float(kt),
        }
        for o, d, kt in rows
    ]


def _moving_score(faf_pct: float, cfs_pct: float) -> float:
    """Higher = moving more (blend national modeled flow + shipment survey)."""
    return round(0.6 * faf_pct + 0.4 * cfs_pct, 2)


def run_moving_commodity(*, faf_year: str = "2024") -> dict[str, Any]:
    t0 = time.monotonic()
    con = duckdb.connect()

    faf = _faf5_by_sctg(con, faf_year)
    cfs = _cfs_by_sctg(con)

    all_sctg = set(faf) | set(cfs)
    tied: list[dict[str, Any]] = []

    for sctg in all_sctg:
        f = faf.get(sctg, {})
        c = cfs.get(sctg, {})
        faf_pct = float(f.get("pct_of_national_tons") or 0)
        cfs_pct = float(c.get("pct_of_shipment_tons") or 0)
        if faf_pct == 0 and cfs_pct == 0:
            continue

        modes = f.get("top_modes") or []
        primary_mode = modes[0]["mode"] if modes else None
        corridors = _faf5_top_corridors(con, sctg, faf_year, limit=3)

        tied.append(
            {
                "sctg": sctg,
                "commodity": SCTG2_LABELS.get(sctg, f"SCTG {sctg}"),
                "moving_a_lot_score": _moving_score(faf_pct, cfs_pct),
                "faf5_thousand_tons": f.get("thousand_tons"),
                "faf5_pct_of_national": faf_pct,
                "cfs_million_tons": c.get("million_tons"),
                "cfs_pct_of_shipments": cfs_pct,
                "primary_mode": primary_mode,
                "top_corridor": corridors[0]["corridor"] if corridors else None,
                "top_corridors": corridors,
                "tie": {
                    "spine": "SCTG",
                    "faf5": bool(f),
                    "cfs_2022": bool(c),
                    "aligned": bool(f and c),
                },
            }
        )

    tied.sort(key=lambda x: x["moving_a_lot_score"], reverse=True)
    for i, row in enumerate(tied, 1):
        row["rank"] = i

    csv_path = EXPORTS_DIR / "moving_commodity_v1.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "rank",
        "sctg",
        "commodity",
        "moving_a_lot_score",
        "faf5_thousand_tons",
        "faf5_pct_of_national",
        "cfs_million_tons",
        "cfs_pct_of_shipments",
        "primary_mode",
        "top_corridor",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in tied:
            w.writerow({k: row.get(k) for k in fields})

    receipt = {
        "scan_type": "moving_commodity_v1",
        "thesis": "commodity moving a lot = the signal",
        "tie_method": "SCTG spine: FAF5 national tonnage % + CFS shipment tonnage %",
        "as_of": utc_now()[:10],
        "faf_year": faf_year,
        "sources": {
            "faf5": str(get_faf_csv().relative_to(ROOT)) if get_faf_csv().exists() else None,
            "cfs_2022": str(get_cfs_csv().relative_to(ROOT)) if get_cfs_csv().exists() else None,
            "source_truth": resolved_sources_dict(),
        },
        "moving_a_lot": tied,
        "top_10": tied[:10],
        "count": len(tied),
        "export_csv": str(csv_path.relative_to(ROOT)),
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)

    # back-link into transport economy if present
    if TRANSPORT_RECEIPT.exists():
        import json

        te = json.loads(TRANSPORT_RECEIPT.read_text(encoding="utf-8"))
        te["moving_commodity_tie"] = {
            "receipt": str(RECEIPT_PATH.relative_to(ROOT)),
            "top_3": [
                {"sctg": r["sctg"], "commodity": r["commodity"], "score": r["moving_a_lot_score"]}
                for r in tied[:3]
            ],
        }
        write_json(TRANSPORT_RECEIPT, te)

    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} moving_commodity_v1.json tied={len(tied)}",
    )
    return receipt
