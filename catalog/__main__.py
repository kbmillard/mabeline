from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from catalog.config import BUILD_REPORTS, REPORTS, today_id, utc_now
from catalog.gaps import fill_gaps
from catalog.manifest import build_all_manifests
from catalog.forward_screen import ScreenConfig, run_forward_screen
from catalog.moneyball import MoneyballConfig, aggregate_moneyball, write_dollar_to_million_playbook
from catalog.cargo_inspection import run_cargo_inspection
from catalog.commodity_economy import run_commodity_economy
from catalog.compiler_pass import run_compiler_pass_v1
from catalog.freight_movement import run_freight_movement
from catalog.money_spider import run_money_spider
from catalog.moving_commodity import run_moving_commodity
from catalog.shipper_carriers import run_shipper_carriers
from catalog.source_truth import run_source_truth_engine
from catalog.transport_economy import run_transport_economy
from catalog.parquet import parquet_all
from catalog.unwrap import unwrap_all
from catalog.financial_sync import run_financial_pipeline, sync_financial_dashboard
from catalog.missing_data_plan import run_missing_data_plan
from catalog.entity_resolution.physical_entity_matcher import run_physical_entity_matcher
from catalog.signals.commodity_truck_signal import run_commodity_truck_signal
from catalog.signals.market_trend_radar import run_market_trend_radar
from catalog.signals.dollar_to_million import run_dollar_to_million
from catalog.signals.evidence_pack import run_signal_evidence_pack
from catalog.signals.validation import run_validation
from catalog.graph.thg_builder import run_thg_build
from catalog.graph.temporal_baseline import run_temporal_baseline
from catalog.graph.linear import run_thg_linear
from catalog.graph.thg_query import format_thg_query, run_thg_query
from catalog.htgnn.train import run_htgnn_score, run_htgnn_train
from catalog.util import append_log, write_json


def _receipt(name: str, payload: dict) -> None:
    write_json(BUILD_REPORTS / name, payload)
    append_log(REPORTS / "build_status.log", f"{utc_now()} {name} status={payload.get('status', 'ok')}")


def cmd_unwrap(args: argparse.Namespace) -> int:
    log = REPORTS / "catalog_run.log"
    result = unwrap_all(log_path=log)
    _receipt(
        "catalog_unwrap_receipt_v1.json",
        {"status": "ok" if not result["errors"] else "partial", **result},
    )
    print(f"unwrapped={result['unwrapped']} errors={len(result['errors'])}")
    return 0 if not result["errors"] else 1


def cmd_today(args: argparse.Namespace) -> int:
    from catalog.today import run_today

    receipt = run_today(absorb_only=args.absorb_only, day=args.day or None)
    m = receipt["manifest"]
    print(f"today={receipt['day']} (UTC) path={receipt['today_path']}")
    print(f"  files={m['file_count']} bytes={m['total_bytes']:,}")
    for step in receipt["steps"]:
        print(f"  {step['step']}: {step}")
    return 0


def cmd_gaps(args: argparse.Namespace) -> int:
    log = REPORTS / "catalog_run.log"
    result = fill_gaps(log_path=log)
    errors = [r for r in result["download_attempts"] if r.get("status") == "required_error"]
    _receipt("catalog_gaps_receipt_v1.json", {"status": "ok" if not errors else "partial", **result})
    print(f"downloads={len(result['download_attempts'])} required_errors={len(errors)}")
    return 0 if not errors else 1


def cmd_manifest(args: argparse.Namespace) -> int:
    result = build_all_manifests()
    statuses = {}
    for fam in result["families"]:
        statuses[fam["status"]] = statuses.get(fam["status"], 0) + 1
    receipt = {
        "status": "ok",
        "updated_at": utc_now(),
        "family_count": len(result["families"]),
        "status_counts": statuses,
        "total_bytes": result["root"]["total_bytes"],
        "families": result["families"],
    }
    _receipt("catalog_manifest_receipt_v1.json", receipt)
    print(f"manifest families={receipt['family_count']} statuses={statuses}")
    return 0


def cmd_parquet(args: argparse.Namespace) -> int:
    log = REPORTS / "catalog_run.log"
    families = args.families.split(",") if args.families else None
    receipt = parquet_all(args.run_id, force=args.force, families=families, log_path=log)
    receipt["status"] = "ok" if receipt["error_count"] == 0 else "partial"
    _receipt("catalog_parquet_receipt_v1.json", receipt)
    print(
        f"parquet converted={receipt['converted_count']} "
        f"skipped={receipt['skipped_count']} errors={receipt['error_count']}"
    )
    return 0 if receipt["error_count"] == 0 else 1


def cmd_run_all(args: argparse.Namespace) -> int:
    append_log(REPORTS / "catalog_run.log", f"{utc_now()} run-all start run_id={args.run_id}")
    rc = 0
    for fn in (cmd_unwrap, cmd_gaps, cmd_manifest, cmd_parquet):
        sub = argparse.Namespace(**vars(args))
        if fn(sub) != 0:
            rc = 1
    append_log(REPORTS / "catalog_run.log", f"{utc_now()} run-all done rc={rc}")
    return rc


def cmd_sync_financial(args: argparse.Namespace) -> int:
    receipt = sync_financial_dashboard()
    print(f"sync-financial copied={len(receipt['copied'])} missing={receipt['missing']}")
    for row in receipt["copied"]:
        print(f"  {row['file']}")
    return 0 if receipt["copied"] else 1


def cmd_financial(args: argparse.Namespace) -> int:
    cfg_mb = MoneyballConfig(stake_usd=args.stake, target_dollar_goal=args.goal, top_k=args.top_k)
    receipt = run_financial_pipeline(run_screen=args.screen, moneyball_cfg=cfg_mb)
    for step in receipt["steps"]:
        print(step)
    return 0


def cmd_market_scan(args: argparse.Namespace) -> int:
    from catalog.market_scan import run_market_scan

    result = run_market_scan(
        batch_size=args.batch_size,
        sleep_between=args.sleep,
        resume=not args.no_resume,
    )
    print(
        f"market-scan universe={result['universe']} priced={result['priced']} "
        f"penny={result['penny_count']}"
    )
    if result.get("raw_max"):
        rm = result["raw_max"]
        print(f"  raw max: {rm['ticker']} {rm['ret_1y']:+.0f}% ({rm['market']})")
    print("  top sane returns:")
    for r in result["top_sane"]:
        print(f"    {r['ticker']:10} {r['ret_1y']:+7.0f}%  ${r.get('start',0):.2f}->${r.get('end',0):.2f}  {r['market']}")
    for rc in result["receipts"]:
        print(f"  receipt → {rc}")
    return 0


def cmd_million_playbook(args: argparse.Namespace) -> int:
    mb = aggregate_moneyball()
    pb = write_dollar_to_million_playbook(moneyball=mb, goal_usd=args.million_goal)
    if args.sync:
        sync = sync_financial_dashboard()
        print(f"sync-financial copied={len(sync['copied'])}")
    memecoin = pb["paths"]["memecoin_launch"]
    stocks = pb["paths"]["sec_penny_stocks"]["stock_paths_from_moneyball"]
    print(f"playbook goal=${args.million_goal:,.0f}")
    print(f"  memecoin path: feasible={memecoin['feasible_for_1_to_1m']} examples={len(memecoin['documented_examples'])}")
    if stocks:
        best = stocks[0]
        print(
            f"  best stock path: {best['ticker']} ${best['stake_needed_for_1m_usd']:,.0f} stake → $1M at target"
        )
    return 0


def cmd_moneyball(args: argparse.Namespace) -> int:
    cfg = MoneyballConfig(
        stake_usd=args.stake,
        target_dollar_goal=args.goal,
        top_k=args.top_k,
    )
    receipt = aggregate_moneyball(cfg)
    playbook = write_dollar_to_million_playbook(moneyball=receipt, cfg=cfg, goal_usd=args.million_goal)
    if args.sync:
        sync = sync_financial_dashboard()
        print(f"sync-financial copied={len(sync['copied'])}")
    print(
        f"moneyball scored={receipt['summary']['scored']} "
        f"cent_zone={receipt['summary']['cent_zone_count']} "
        f"x100={receipt['summary']['x100_feasible_count']}"
    )
    print(f"playbook $1→${args.million_goal:,.0f} written → build_reports/dollar_to_million_playbook_v1.json")
    for row in receipt["top"][:10]:
        goal_stake = row.get("stake_needed_for_goal_usd")
        path = (
            f"${row['stake_usd']:.0f}→${row['value_at_target_usd'] or 0:.0f}"
            if row.get("x100_feasible")
            else (
                f"${goal_stake:.2f}→$100"
                if goal_stake
                else f"${row['stake_usd']:.0f}→${row['value_at_target_usd'] or 0:.0f}"
            )
        )
        print(
            f"  {row['ticker']:6} ${row['price_now']:.2f} "
            f"mb={row['moneyball_score']:.0f} "
            f"{path} "
            f"x{row['upside_multiple'] or 0:.0f} "
            f"{'CENT' if row['cent_zone'] else ''} "
            f"{'100x+' if row['x100_feasible'] else ''}"
        )
    return 0


def cmd_find_cargo(args: argparse.Namespace) -> int:
    receipt = run_cargo_inspection(
        min_inspections=args.min_count,
        limit=args.limit,
        state=args.state or None,
    )
    cov = receipt["coverage"]
    print(
        f"find-cargo ties={receipt['tie_count']} "
        f"inspections={cov['total_inspections']:,} "
        f"shipper_documented={cov['documented_shipper']:,} ({cov['shipper_rate_pct']}%)"
    )
    print(f"export → {receipt['export_csv']}")
    print("\nCommodity tie path:")
    print("  inspection SHIPPER_NAME → carrier DOT → census CRGO_* lane cert")
    print("\nTop shipper → carrier → commodity lane:")
    for t in receipt["top_ties"][:12]:
        print(
            f"  {t['shipper'][:22]:22} → {t['carrier_entity'][:28]:28} "
            f"lane={t['commodity_lane_cert']:16} n={t['inspection_count']}"
        )
    return 0


def cmd_money_spider(args: argparse.Namespace) -> int:
    receipt = run_money_spider(refresh_layers=args.refresh)
    print(f"money-spider threads={len(receipt['threads'])} exports={len(receipt['exports'])}")
    insp = next((l for l in receipt["legs"] if l["leg_id"] == "inspections"), None)
    if insp:
        print(f"  inspections leg: {insp['node_count']} ties — {insp['note']}")
    print("\nTop threads (sell these):")
    for t in receipt["threads"][:4]:
        print(
            f"  {t['thread_id']:16} score={t['spider_score']:5.1f} "
            f"leads={t['carrier_lead_count']:4} insp={t.get('inspection_tie_count', 0):5}  {t['label']}"
        )
        if t.get("export_csv"):
            print(f"    carriers → exports/{t['export_csv']}")
        if t.get("inspection_export"):
            print(f"    inspections → exports/{t['inspection_export']}")
        if t.get("top_shipper_ties"):
            ex = t["top_shipper_ties"][0]
            print(f"    e.g. {ex.get('shipper')} → {ex.get('carrier_entity')}")
    print("\nActions today:")
    for a in receipt["actions_today"]:
        print(f"  [{a['priority']}] {a['action']}: {a}")
    print("\nCapital watch (your money leg):")
    for s in receipt["capital_signals"][:3]:
        print(f"  {s['ticker']} mb={s['moneyball_score']} ${s['price']} stake100=${s.get('stake_for_100')}")
    return 0


def cmd_shipper_carriers(args: argparse.Namespace) -> int:
    receipt = run_shipper_carriers(
        shipper=args.shipper,
        min_stops=args.min_stops,
        export_name=args.export or None,
    )
    print(
        f"shipper-carriers filter={receipt['shipper_filter']!r} "
        f"carriers={receipt['distinct_carriers']} → {receipt['export_csv']}"
    )
    for row in receipt["top_10"][:5]:
        print(f"  DOT {row['dot_number']} {row['carrier_name'][:40]:40} stops={row['stop_count']}")
    return 0


def cmd_compiler_pass(args: argparse.Namespace) -> int:
    receipt = run_compiler_pass_v1(skip_financial_sync=args.skip_sync)
    print(f"compiler-pass status={receipt['status']} elapsed={receipt['elapsed_sec']}s")
    print(f"receipt → build_reports/mabeline_compiler_pass_v1.json")
    print(f"selected sources: {receipt['row_file_counts']['selected_sources']}")
    if receipt.get("errors"):
        print("errors:", receipt["errors"])
    for step in receipt["steps"]:
        print(f"  {step['step']}: {step}")
    return 0 if receipt["status"] == "ok" else 1


def cmd_thg_build(args: argparse.Namespace) -> int:
    run_source_truth_engine()
    receipt = run_thg_build(from_month=args.from_month, min_stops=args.min_stops)
    print(f"thg-build events={receipt['row_counts']['events']} nodes={receipt['row_counts']['nodes']}")
    for k, v in receipt.get("events_by_type", {}).items():
        print(f"  {k}: {v}")
    return 0


def cmd_thg_baseline(args: argparse.Namespace) -> int:
    receipt = run_temporal_baseline()
    print(f"thg-baseline scores={receipt['row_counts']['change_scores']}")
    for t in receipt.get("top_change_scores", [])[:5]:
        print(f"  SCTG {t['sctg2']} {t['sctg2_name']}: change={t['change_score']} delta={t['truck_observation_delta_pct']}%")
    return 0


def cmd_thg_linear(args: argparse.Namespace) -> int:
    run_source_truth_engine()
    result = run_thg_linear(from_month=args.from_month, min_stops=args.min_stops, top_n=args.top_n)
    for step in result["steps"]:
        print(f"  {step['step']}: {step}")
    radar = result["radar"]
    print(f"thg-linear done input={radar.get('input_source')} trends={radar['row_counts']['trends']}")
    return 0


def cmd_thg_query(args: argparse.Namespace) -> int:
    result = run_thg_query(sctg2=args.sctg2, month=args.month)
    print(format_thg_query(result))
    return 0


def cmd_htgnn_train(args: argparse.Namespace) -> int:
    receipt = run_htgnn_train(epochs=args.epochs, snapshot_month=args.snapshot_month, limit=args.limit)
    print(
        f"htgnn-train nodes={receipt['row_counts']['nodes']} "
        f"edges={receipt['row_counts']['edges_subsample']} month={receipt.get('snapshot_month')}"
    )
    return 0


def cmd_htgnn_score(args: argparse.Namespace) -> int:
    result = run_htgnn_score()
    print(f"htgnn-score nodes={result['nodes']} path={result['path']}")
    return 0


def cmd_commodity_truck_signal(args: argparse.Namespace) -> int:
    receipt = run_commodity_truck_signal(min_inspections=args.min_inspections, limit=args.limit)
    print(f"commodity-truck-signal rows={receipt['row_counts']['signals']} elapsed={receipt['elapsed_sec']}s")
    return 0


def cmd_market_trend_radar(args: argparse.Namespace) -> int:
    receipt = run_market_trend_radar()
    src = receipt.get("input_source", "unknown")
    print(f"market-trend-radar trends={receipt['row_counts']['trends']} input={src} elapsed={receipt['elapsed_sec']}s")
    for t in receipt.get("top_10", [])[:5]:
        print(f"  {t.get('sctg2_name')}: score={t.get('commodity_market_signal_score')} dir={t.get('trend_direction')}")
    return 0


def cmd_dollar_to_million(args: argparse.Namespace) -> int:
    if args.full_pipeline:
        run_source_truth_engine()
        result = run_thg_linear(top_n=args.top_n)
        receipt = result["dtm"]
    else:
        receipt = run_dollar_to_million(top_n=args.top_n)
    print(f"dollar-to-million opportunities={receipt['row_counts']['opportunities']} packs={receipt['row_counts']['evidence_packs']}")
    print("DISCLAIMER: Research leads only. Not buy/sell/hold. Can lose 100%.")
    for t in receipt.get("top_10_themes", [])[:10]:
        print(f"  [{t['score']:.1f}] {t['theme']}")
    if args.validate:
        return run_validation()
    return 0


def cmd_missing_data_plan(args: argparse.Namespace) -> int:
    receipt = run_missing_data_plan()
    rc = receipt["row_counts"]
    print(
        f"missing-data-plan rows={rc['total_rows']} "
        f"remaining={rc['remaining_gaps']} resolved={rc['resolved_on_disk']} "
        f"wiring={rc['wiring_debt']}"
    )
    for b in receipt.get("extra", {}).get("top_remaining", [])[:10]:
        print(f"  [{b['priority']}] {b['id']}: {b['status']}")
    return 0


def cmd_signal_evidence_pack(args: argparse.Namespace) -> int:
    result = run_signal_evidence_pack(opportunity_id=args.opportunity_id or None)
    print(f"signal-evidence-pack count={result['count']}")
    return 0


def cmd_source_truth(args: argparse.Namespace) -> int:
    result = run_source_truth_engine()
    sel = result["selected"]
    print(f"source-truth selected={sel['selected_count']} today={sel.get('today_day')}")
    for row in sel["selected"]:
        print(f"  {row['logical']:20} {row['method']:14} {row['path']}")
    if sel.get("missing_required"):
        print("missing:", sel["missing_required"])
    return 0


def cmd_moving_commodity(args: argparse.Namespace) -> int:
    receipt = run_moving_commodity(faf_year=args.year)
    print(f"moving-commodity tied={receipt['count']} elapsed={receipt['elapsed_sec']}s")
    print(f"export → {receipt['export_csv']}")
    print("\nMoving a lot (FAF5 + CFS tied on SCTG):")
    for row in receipt["top_10"]:
        print(
            f"  #{row['rank']:2} {row['commodity'][:26]:26} "
            f"score={row['moving_a_lot_score']:5.1f} "
            f"faf5={row['faf5_pct_of_national']:4.1f}% "
            f"cfs={row['cfs_pct_of_shipments']:4.1f}% "
            f"{row['primary_mode'] or '—'}"
        )
        if row.get("top_corridor"):
            print(f"       → {row['top_corridor']}")
    return 0


def cmd_transport_economy(args: argparse.Namespace) -> int:
    receipt = run_transport_economy(faf_year=args.year)
    print(
        f"transport-economy nodes={len(receipt['nodes'])} "
        f"faf5={receipt['national_totals']['faf5_billion_tons']}B tons "
        f"elapsed={receipt['elapsed_sec']}s"
    )
    print(f"export → {receipt['export_csv']}")
    print("\nTop commodities (transport-wired):")
    for n in receipt["top_10"]:
        top = (n.get("top_shipper_carrier_ties") or [{}])[0]
        modes = (n.get("faf5") or {}).get("top_modes") or []
        mode = modes[0]["mode"] if modes else "—"
        print(
            f"  SCTG {n['sctg']} {n['commodity'][:24]:24} "
            f"score={n['transport_score']:5.1f} "
            f"carriers={n['fmcsa_carriers_certified']:,} "
            f"mode={mode}"
        )
        if top.get("shipper"):
            print(f"    {top['shipper']} → {top.get('carrier', '—')}")
    return 0


def cmd_commodity_economy(args: argparse.Namespace) -> int:
    receipt = run_commodity_economy(
        faf_year=args.year,
        refresh_faf_receipt=args.refresh_faf,
    )
    if args.sync:
        sync = sync_financial_dashboard()
        print(f"sync-financial copied={len(sync['copied'])}")
    print(
        f"commodity-economy slate={len(receipt['unified_commodity_slate'])} "
        f"elapsed={receipt['elapsed_sec']}s gaps={len(receipt['gaps'])}"
    )
    print("Physical economy:")
    pe = receipt["physical_economy_totals"]
    print(f"  FAF5 {pe.get('faf5_billion_tons')}B tons  CFS {pe.get('cfs_million_tons'):,.0f}M tons")
    print(f"  Crude imports {pe.get('crude_imports_kbbl_latest'):,} kbbl latest")
    print("Top unified:")
    for row in receipt["unified_commodity_slate"][:8]:
        print(
            f"  {row['commodity'][:28]:28} score={row['economy_score']:5.1f} "
            f"mode={row.get('primary_mode') or '—'}"
        )
    if receipt["gaps"]:
        print("Gaps:", ", ".join(receipt["gaps"]))
    return 0


def cmd_freight_movement(args: argparse.Namespace) -> int:
    receipt = run_freight_movement(year=args.year)
    print(
        f"freight-movement year={receipt['year']} "
        f"kt={receipt['totals']['thousand_tons']:,.0f} "
        f"elapsed={receipt['elapsed_sec']}s"
    )
    print("Top modes:")
    for m in receipt["by_mode"][:4]:
        print(f"  {m['mode']:16} {m['pct_of_tons']:5.1f}%  {m['thousand_tons']:,.0f} kt")
    print("Top corridor:", receipt["top_corridors"][0]["corridor"])
    return 0


def cmd_forward_screen(args: argparse.Namespace) -> int:
    cfg = ScreenConfig(
        max_price=args.max_price,
        batch_size=args.batch_size,
        enrich_top_n=args.enrich_top_n,
        top_k=args.top_k,
    )
    receipt = run_forward_screen(cfg)
    append_log(REPORTS / "build_status.log", f"{utc_now()} penny_forward_screen_v1.json status=ok")
    if args.sync:
        aggregate_moneyball()
        sync = sync_financial_dashboard()
        print(f"sync-financial copied={len(sync['copied'])}")
    print(
        f"forward-screen survivors={receipt['survivor_count']} "
        f"top={receipt['top_k']} elapsed={receipt['elapsed_sec']}s"
    )
    for row in receipt["top"][:10]:
        print(
            f"  {row['ticker']:6} ${row['px']:.2f} score={row['score']:.0f} "
            f"1y={row['ret_1y']:+.0f}% upside={row.get('upside_pct')} "
            f"{row['name'][:40]}"
        )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path("/Users/kyle/Documents/mabeline")
    run_id = args.run_id
    pq_dir = root / "warehouse" / "catalog_parquet_v1" / f"run_id={run_id}"
    manifest_receipt = BUILD_REPORTS / "catalog_manifest_receipt_v1.json"
    parquet_receipt = BUILD_REPORTS / "catalog_parquet_receipt_v1.json"
    log = REPORTS / "catalog_run.log"

    print(f"run_id={run_id}")
    if manifest_receipt.exists():
        import json

        m = json.loads(manifest_receipt.read_text(encoding="utf-8"))
        print(f"manifest: {m.get('family_count')} families {m.get('status_counts')}")
    if parquet_receipt.exists():
        import json

        p = json.loads(parquet_receipt.read_text(encoding="utf-8"))
        print(
            f"parquet: converted={p.get('converted_count')} "
            f"skipped={p.get('skipped_count')} errors={p.get('error_count')}"
        )
        bad = [f for f in p.get("families", []) if f.get("errors")]
        if bad:
            print("families with errors:")
            for f in sorted(bad, key=lambda x: -x["errors"])[:10]:
                print(f"  {f['family']}: {f['errors']} errors, {f['converted']} converted")
    if pq_dir.exists():
        n = len(list(pq_dir.rglob("*.parquet")))
        print(f"parquet files on disk: {n} under {pq_dir}")
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()
        print(f"log: {len(lines)} lines — tail: {lines[-1] if lines else '(empty)'}")
    print("\nfinancial receipts:")
    for name in (
        "penny_forward_screen_v1.json",
        "moneyball_aggregate_v1.json",
        "moneyball_supplements_v1.json",
        "dollar_to_million_playbook_v1.json",
        "freight_movement_receipt_v1.json",
        "financial_sync_receipt_v1.json",
    ):
        p = BUILD_REPORTS / name
        print(f"  {name}: {'yes' if p.exists() else 'missing'}")
    print("\ncommands:")
    print("  bin/mabel-catalog financial")
    print("  bin/mabel-catalog moneyball --sync")
    print("  bin/mabel-catalog million-playbook --sync")
    print("  bin/mabel-catalog forward-screen --sync")
    print("  bin/mabel-catalog open --phase forward-screen")
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    root = Path("/Users/kyle/Documents/mabeline")
    log = root / "reports" / "catalog_run.log"
    venv_py = root / ".venv" / "bin" / "python"
    py = str(venv_py) if venv_py.exists() else "python3"
    phase = getattr(args, "phase", "run-all")
    families = getattr(args, "families", "") or ""
    fam_flag = f" --families {families}" if families else ""
    extra = ""
    run_id_flag = f" --run-id {args.run_id}"
    if phase == "forward-screen":
        extra = " --batch-size 120 --enrich-top-n 200 --sync"
        run_id_flag = ""
    elif phase == "financial":
        run_id_flag = ""
        extra = ""
    elif phase == "commodity-economy":
        run_id_flag = ""
        extra = " --sync"
    elif phase == "market-scan":
        run_id_flag = ""
        extra = ""
    elif phase == "today":
        run_id_flag = ""
        extra = ""
    cmd = (
        f"cd {root} && "
        f"mkdir -p reports build_reports && "
        f"test -x .venv/bin/python || python3 -m venv .venv && "
        f".venv/bin/pip install -q -r requirements-catalog.txt && "
        f"caffeinate -dims {py} -m catalog {phase}{run_id_flag}{fam_flag}{extra} "
        f">> {log} 2>&1"
    )
    script = f'tell application "Terminal" to do script "{cmd}"'
    subprocess.run(["osascript", "-e", script], check=True)
    print(f"Launched Terminal.app job run_id={args.run_id}")
    print(f"Tail log: tail -f {log}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mabel-catalog")
    sub = parser.add_subparsers(dest="command", required=True)

    p_today = sub.add_parser(
        "today",
        help="Newest-first ingest → _unwrapped/today/YYYY-MM-DD/ (gaps + unwrap + absorb)",
    )
    p_today.add_argument("--absorb-only", action="store_true", help="Only absorb release={day} into today/")
    p_today.add_argument("--day", default="", help="UTC date YYYY-MM-DD (default: today UTC)")
    p_today.set_defaults(func=cmd_today)

    p_open = sub.add_parser("open", help="Launch a catalog phase in Terminal.app (long-running)")
    p_open.add_argument("--run-id", default=utc_now()[:10])
    p_open.add_argument(
        "--phase",
        default="run-all",
        choices=["run-all", "unwrap", "gaps", "today", "manifest", "parquet", "forward-screen", "financial", "commodity-economy", "market-scan"],
    )
    p_open.add_argument("--families", default="", help="Comma-separated families (parquet phase)")
    p_open.set_defaults(func=cmd_open)

    p_status = sub.add_parser("status", help="Show manifest/parquet receipts and usage hints")
    p_status.add_argument("--run-id", default=utc_now()[:10])
    p_status.set_defaults(func=cmd_status)

    p_mb = sub.add_parser("moneyball", help="Aggregate penny screen into moneyball 1¢→$100 slate")
    p_mb.add_argument("--stake", type=float, default=1.0, help="USD stake per name for projection")
    p_mb.add_argument("--goal", type=float, default=100.0, help="Target portfolio value goal")
    p_mb.add_argument("--million-goal", type=float, default=1_000_000.0, help="Playbook $1→$N goal")
    p_mb.add_argument("--top-k", type=int, default=25)
    p_mb.add_argument("--sync", action="store_true", help="Push receipts to financial/ dashboard data")
    p_mb.set_defaults(func=cmd_moneyball)

    p_pb = sub.add_parser("million-playbook", help="Write $1→$1M playbook from moneyball + web paths")
    p_pb.add_argument("--million-goal", type=float, default=1_000_000.0)
    p_pb.add_argument("--sync", action="store_true")
    p_pb.set_defaults(func=cmd_million_playbook)

    p_scan = sub.add_parser(
        "market-scan",
        help="Price SEC + JPX/Xetra/KRX tickers for 1y returns (throttled, checkpointed)",
    )
    p_scan.add_argument("--batch-size", type=int, default=30)
    p_scan.add_argument("--sleep", type=float, default=1.6, help="Seconds between batches")
    p_scan.add_argument("--no-resume", action="store_true", help="Ignore checkpoint, rescan all")
    p_scan.set_defaults(func=cmd_market_scan)

    p_fc = sub.add_parser(
        "find-cargo",
        help="Inspection-level shipper→carrier→commodity lane ties (FMCSA MCMIS)",
    )
    p_fc.add_argument("--state", default="", help="Filter COUNTY_CODE_STATE e.g. TX")
    p_fc.add_argument("--min-count", type=int, default=5, help="Min inspections per tie")
    p_fc.add_argument("--limit", type=int, default=500)
    p_fc.set_defaults(func=cmd_find_cargo)

    p_sc = sub.add_parser(
        "shipper-carriers",
        help="Export shipper→carrier roll-up from FMCSA inspections (reusable filter)",
    )
    p_sc.add_argument("--shipper", required=True, help="Shipper name substring e.g. 'DOLLAR GENERAL'")
    p_sc.add_argument("--min-stops", type=int, default=1, dest="min_stops")
    p_sc.add_argument("--export", default="", help="Optional export CSV filename")
    p_sc.set_defaults(func=cmd_shipper_carriers)

    p_cp = sub.add_parser(
        "compiler-pass",
        help="Mabeline Compiler Pass V1: source truth + spine refresh + proofs + cards",
    )
    p_cp.add_argument("--skip-sync", action="store_true", help="Skip sync-financial step")
    p_cp.set_defaults(func=cmd_compiler_pass)

    p_st = sub.add_parser("source-truth", help="Resolve newest valid sources; emit selected/rejected manifests")
    p_st.set_defaults(func=cmd_source_truth)

    p_tb = sub.add_parser("thg-build", help="Build temporal_edge_events from FMCSA + FAF5 + CFS + STB")
    p_tb.add_argument("--from-month", default="202401", dest="from_month")
    p_tb.add_argument("--min-stops", type=int, default=2, dest="min_stops")
    p_tb.set_defaults(func=cmd_thg_build)

    p_tbl = sub.add_parser("thg-baseline", help="Month-over-month change scores on THG events")
    p_tbl.set_defaults(func=cmd_thg_baseline)

    p_tl = sub.add_parser("thg-linear", help="Linear wire: thg-build → baseline → radar → dollar-to-million")
    p_tl.add_argument("--from-month", default="202401", dest="from_month")
    p_tl.add_argument("--min-stops", type=int, default=2, dest="min_stops")
    p_tl.add_argument("--top-n", type=int, default=50, dest="top_n")
    p_tl.set_defaults(func=cmd_thg_linear)

    p_tq = sub.add_parser("thg-query", help="Query THG truck delta vs FAF residual for SCTG/month")
    p_tq.add_argument("--sctg2", required=True)
    p_tq.add_argument("--month", default=None)
    p_tq.set_defaults(func=cmd_thg_query)

    p_ht = sub.add_parser("htgnn-train", help="Train HT-GNN embeddings on subsampled THG edges")
    p_ht.add_argument("--epochs", type=int, default=20)
    p_ht.add_argument("--snapshot-month", default=None)
    p_ht.add_argument("--limit", type=int, default=250_000)
    p_ht.set_defaults(func=cmd_htgnn_train)

    p_hs = sub.add_parser("htgnn-score", help="Score / verify node embeddings parquet")
    p_hs.set_defaults(func=cmd_htgnn_score)

    p_cts = sub.add_parser("commodity-truck-signal", help="Extract commodity-on-truck market signals from FMCSA")
    p_cts.add_argument("--min-inspections", type=int, default=3, dest="min_inspections")
    p_cts.add_argument("--limit", type=int, default=25000)
    p_cts.set_defaults(func=cmd_commodity_truck_signal)

    p_mtr = sub.add_parser("market-trend-radar", help="Commodity trend radar from truck signals + FAF5/CFS/EIA/STB")
    p_mtr.set_defaults(func=cmd_market_trend_radar)

    p_dtm = sub.add_parser("dollar-to-million", help="Rank asymmetric opportunity research leads (not stock picks)")
    p_dtm.add_argument("--top-n", type=int, default=50, dest="top_n")
    p_dtm.add_argument("--full-pipeline", action="store_true", help="Run missing-data + truck-signal + radar first")
    p_dtm.add_argument("--validate", action="store_true", help="Run output validation after build")
    p_dtm.set_defaults(func=cmd_dollar_to_million)

    p_mdp = sub.add_parser("missing-data-plan", help="Machine-readable missing/stale/broken data plan")
    p_mdp.set_defaults(func=cmd_missing_data_plan)

    p_sep = sub.add_parser("signal-evidence-pack", help="Write evidence packs for top opportunities")
    p_sep.add_argument("--opportunity-id", default="", dest="opportunity_id")
    p_sep.set_defaults(func=cmd_signal_evidence_pack)

    p_ms = sub.add_parser("money-spider", help="Connect commodity+FMCSA+moneyball into invoiceable threads")
    p_ms.add_argument("--refresh", action="store_true", help="Rebuild commodity and moneyball layers first")
    p_ms.set_defaults(func=cmd_money_spider)

    p_mc = sub.add_parser(
        "moving-commodity",
        help="Tie what's moving a lot: SCTG + FAF5 tons + CFS tons + mode + corridor",
    )
    p_mc.add_argument("--year", default="2024")
    p_mc.set_defaults(func=cmd_moving_commodity)

    p_te = sub.add_parser(
        "transport-economy",
        help="Wire entire physical economy on SCTG: FAF5 + CFS + FMCSA + inspections",
    )
    p_te.add_argument("--year", default="2024", help="FAF year column")
    p_te.set_defaults(func=cmd_transport_economy)

    p_ce = sub.add_parser(
        "commodity-economy",
        help="Full physical commodity economy: FAF5 + CFS + PET imports + USGS",
    )
    p_ce.add_argument("--year", default="2024", help="FAF year column")
    p_ce.add_argument("--refresh-faf", action="store_true", help="Also rewrite freight_movement receipt")
    p_ce.add_argument("--sync", action="store_true", help="Push receipts to financial/ dashboard")
    p_ce.set_defaults(func=cmd_commodity_economy)

    p_fm = sub.add_parser("freight-movement", help="FAF5 tonnage/ton-mile analysis from on-disk data")
    p_fm.add_argument("--year", default="2024", help="FAF year column suffix (e.g. 2024)")
    p_fm.set_defaults(func=cmd_freight_movement)

    p_fs = sub.add_parser(
        "forward-screen",
        help="3-phase penny-forward screen (batch prices, enrich top survivors)",
    )
    p_fs.add_argument("--max-price", type=float, default=5.0)
    p_fs.add_argument("--batch-size", type=int, default=120)
    p_fs.add_argument("--enrich-top-n", type=int, default=200)
    p_fs.add_argument("--top-k", type=int, default=25)
    p_fs.add_argument("--sync", action="store_true", help="Run moneyball + sync to financial/ after screen")
    p_fs.set_defaults(func=cmd_forward_screen)

    p_sf = sub.add_parser("sync-financial", help="Copy build_reports JSON into financial/src/data")
    p_sf.set_defaults(func=cmd_sync_financial)

    p_fin = sub.add_parser(
        "financial",
        help="Moneyball aggregate + sync dashboard (add --screen for full Yahoo forward-screen in Terminal)",
    )
    p_fin.add_argument("--screen", action="store_true", help="Run forward-screen first (use Terminal for long job)")
    p_fin.add_argument("--stake", type=float, default=1.0)
    p_fin.add_argument("--goal", type=float, default=100.0)
    p_fin.add_argument("--top-k", type=int, default=25)
    p_fin.set_defaults(func=cmd_financial)

    for name, help_text in [
        ("unwrap", "Unzip any pending .zip under _unwrapped"),
        ("gaps", "Retry known gap downloads + write gap register"),
        ("manifest", "Rescan _unwrapped and rewrite manifests"),
        ("parquet", "Convert tabular/json/geojson sources to parquet"),
        ("run-all", "unwrap → gaps → manifest → parquet"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--run-id", default=utc_now()[:10])
        p.add_argument("--force", action="store_true", help="Reconvert parquet even if source_sig matches")
        p.add_argument("--families", default="", help="Comma-separated family list for parquet")
        p.set_defaults(func=globals()[f"cmd_{name.replace('-', '_')}"])

    args = parser.parse_args(argv)
    BUILD_REPORTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
