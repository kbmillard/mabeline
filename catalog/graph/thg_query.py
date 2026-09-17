"""Ad-hoc THG queries for developers."""

from __future__ import annotations

from typing import Any

import duckdb

from catalog.freight_movement import SCTG2_LABELS
from catalog.graph.iran_oil import build_iran_oil_receipt
from catalog.graph.month_picker import pick_snapshot_month
from catalog.graph.schema_v1 import OUTPUTS
from catalog.signals._common import CSV_OPTS


def run_thg_query(*, sctg2: str, month: str | None = None) -> dict[str, Any]:
    sctg = str(sctg2).zfill(2)[:2]
    events_path = OUTPUTS["events"]
    scores_path = OUTPUTS["change_scores"]
    corridor_path = OUTPUTS["change_scores_corridor"]

    if not events_path.exists():
        raise FileNotFoundError(f"Run thg-build first: {events_path}")

    con = duckdb.connect()
    if not month:
        month = pick_snapshot_month(events_path, con=con)

    score_row = None
    if scores_path.exists():
        score_row = con.execute(
            """
            SELECT change_score, truck_observation_delta_pct, truck_vs_faf_residual, truck_weight
            FROM read_parquet(?)
            WHERE sctg2 = ? AND snapshot_month = ?
            """,
            [str(scores_path), sctg, month],
        ).fetchone()

    corridors = []
    if corridor_path.exists():
        corridors = con.execute(
            """
            SELECT state, change_score, truck_observation_delta_pct, truck_weight
            FROM read_parquet(?)
            WHERE sctg2 = ? AND snapshot_month = ?
            ORDER BY change_score DESC
            LIMIT 5
            """,
            [str(corridor_path), sctg, month],
        ).fetchall()

    events_s = str(events_path)
    top_carriers = con.execute(
        f"""
        SELECT dst_id AS dot_number, SUM(weight) AS w
        FROM read_parquet('{events_s}')
        WHERE edge_type = 'observed_haul'
          AND event_time = ?
          AND json_extract_string(attrs_json, '$.sctg2') = ?
        GROUP BY 1
        ORDER BY w DESC
        LIMIT 5
        """,
        [month, sctg],
    ).fetchall()

    result = {
        "sctg2": sctg,
        "sctg2_name": SCTG2_LABELS.get(sctg, sctg),
        "snapshot_month": month,
        "national": {
            "change_score": float(score_row[0]) if score_row else None,
            "truck_observation_delta_pct": float(score_row[1] or 0) if score_row else None,
            "truck_vs_faf_residual": float(score_row[2] or 0) if score_row else None,
            "truck_weight": float(score_row[3] or 0) if score_row else None,
        },
        "top_corridors": [
            {
                "state": r[0],
                "change_score": float(r[1] or 0),
                "truck_observation_delta_pct": float(r[2] or 0),
                "truck_weight": float(r[3] or 0),
            }
            for r in corridors
        ],
        "top_carriers": [{"dot_number": r[0], "inspection_weight": float(r[1])} for r in top_carriers],
    }
    if sctg == "17":
        iran = build_iran_oil_receipt(truck_month=month)
        result["iran_oil"] = {
            "join": iran["join"],
            "join_note": iran["join_note"],
            "eia_last_month": iran["eia_iran"]["last_month"],
            "eia_last_kbbl": iran["eia_iran"]["last_kbbl"],
            "imdb_month": iran["census_iran"]["month"],
            "imdb_con_val_mo": iran["census_iran"]["con_val_mo"],
            "public_url": iran["public_url"],
        }
    return result


def format_thg_query(result: dict[str, Any]) -> str:
    nat = result["national"]
    lines = [
        f"SCTG {result['sctg2']} {result['sctg2_name']} @ {result['snapshot_month']}",
        f"  truck_delta_pct={nat.get('truck_observation_delta_pct')}% "
        f"faf_residual={nat.get('truck_vs_faf_residual')} change_score={nat.get('change_score')}",
        "  top corridors:",
    ]
    for c in result["top_corridors"]:
        lines.append(
            f"    {c['state']}: score={c['change_score']} delta={c['truck_observation_delta_pct']}%"
        )
    lines.append("  top carriers:")
    for c in result["top_carriers"]:
        lines.append(f"    DOT {c['dot_number']}: weight={c['inspection_weight']}")
    iran = result.get("iran_oil")
    if iran:
        lines.append(
            f"  iran_oil: join={iran['join']} eia={iran['eia_last_month']} "
            f"({iran['eia_last_kbbl']} kbbl) imdb=${iran['imdb_con_val_mo']} "
            f"→ {iran['public_url']}"
        )
        lines.append(f"    {iran['join_note']}")
    return "\n".join(lines)
