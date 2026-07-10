"""
Moneyball aggregate: combine on-disk signals into a single ranked slate.

Goal: find beaten-down penny names with a plausible path from ~$0.01–$1.00
toward $100 (100x–10,000x on price, depending on entry).

Moneyball idea (sabermetrics, not one metric):
  - Aggregate analyst gap, liquidity, exchange quality, maturity filter,
    biotech catalyst density, and feasibility of 100x move.
  - Penalize OTC junk, illiquid microcaps, and already-matured runners.

Inputs (local, no API required if receipts exist):
  - build_reports/penny_forward_screen_v1.json
  - build_reports/return_scan_receipt_v1.json (matured reference: ARTV)
  - _unwrapped/sec_filings/company_tickers.json
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.util import append_log, write_json

PENNY_RECEIPT = BUILD_REPORTS / "penny_forward_screen_v1.json"
SUPPLEMENT_RECEIPT = BUILD_REPORTS / "moneyball_supplements_v1.json"
RETURN_RECEIPT = BUILD_REPORTS / "return_scan_receipt_v1.json"
SEC_TICKERS = ROOT / "_unwrapped/sec_filings/company_tickers.json"
RECEIPT_PATH = BUILD_REPORTS / "moneyball_aggregate_v1.json"
PLAYBOOK_RECEIPT = BUILD_REPORTS / "dollar_to_million_playbook_v1.json"

MAJOR_EXCHANGES = frozenset({"NMS", "NGM", "NCM", "NYQ", "ASE"})
OTC_EXCHANGES = frozenset({"OQB", "OQX", "PNK", "OTC", "GREY", "OTCM"})


@dataclass
class MoneyballConfig:
    max_entry_price: float = 5.0
    cent_zone_max: float = 1.0
    target_100x: float = 100.0
    target_dollar_goal: float = 100.0
    stake_usd: float = 1.0
    top_k: int = 25
    min_volume: float = 50_000
    max_mcap_m: float = 500.0


@dataclass
class MoneyballPick:
    ticker: str
    name: str
    price_now: float
    proj_target: float | None
    moneyball_score: float
    upside_multiple: float | None
    x100_feasible: bool
    cent_zone: bool
    stake_usd: float
    value_at_target_usd: float | None
    stake_needed_for_goal_usd: float | None
    ret_1y: float | None
    ret_3m: float | None
    mcap_m: float | None
    exchange: str
    rec: str
    vol: float | None
    components: dict[str, float] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _rec_bonus(rec: str) -> float:
    return {"strong_buy": 25, "buy": 15}.get((rec or "").lower(), 0)


def _exchange_bonus(exchange: str) -> float:
    ex = (exchange or "").upper()
    if ex in MAJOR_EXCHANGES:
        return 20
    if ex in OTC_EXCHANGES:
        return -15
    return 0


def _maturity_bonus(ret_1y: float | None, ret_3m: float | None) -> float:
    """Reward beaten-down names; penalize recent runners."""
    score = 0.0
    if ret_1y is not None:
        if ret_1y < -50:
            score += 25
        elif ret_1y < 0:
            score += 15
        elif ret_1y > 100:
            score -= 40
    if ret_3m is not None:
        if ret_3m < -20:
            score += 10
        elif ret_3m > 50:
            score -= 25
    return score


def _liquidity_bonus(vol: float | None, mcap_m: float | None) -> float:
    score = 0.0
    if vol and vol >= 1_000_000:
        score += 20
    elif vol and vol >= 200_000:
        score += 12
    elif vol and vol >= 50_000:
        score += 5
    else:
        score -= 10
    if mcap_m and 10 <= mcap_m <= 200:
        score += 15
    elif mcap_m and mcap_m < 5:
        score -= 10
    return score


def _value_gap_bonus(price: float, target: float | None) -> tuple[float, float | None]:
    if not target or price <= 0:
        return 0.0, None
    mult = target / price
    if mult >= 10_000:
        gap = 80
    elif mult >= 1_000:
        gap = 60
    elif mult >= 100:
        gap = 45
    elif mult >= 20:
        gap = 25
    else:
        gap = min(20, mult)
    return gap, mult


def _matured_tickers(returns: dict | None, penny: dict | None) -> set[str]:
    out: set[str] = set()
    if returns:
        for run in (returns.get("runs") or {}).values():
            for key in ("highest", "raw_highest", "runner_up", "raw_runner_up"):
                h = run.get(key) if isinstance(run, dict) else None
                if not h:
                    continue
                ret = h.get("return_pct")
                if ret is not None and float(ret) > 100:
                    t = h.get("ticker")
                    if t:
                        out.add(str(t).upper())
    if penny:
        ref = penny.get("artv_reference") or {}
        if ref.get("ticker"):
            out.add(str(ref["ticker"]).upper())
    return out


def score_candidate(
    row: dict,
    cfg: MoneyballConfig,
    *,
    matured: set[str] | None = None,
) -> MoneyballPick | None:
    ticker = str(row.get("ticker", "")).upper()
    if matured and ticker in matured:
        return None

    price = float(row.get("price_now") or row.get("px") or 0)
    if price <= 0 or price > cfg.max_entry_price:
        return None

    target = row.get("proj_1y_target") or row.get("target")
    target_f = float(target) if target else None
    ret_1y = row.get("ret_1y")
    ret_3m = row.get("ret_3m")
    vol = row.get("vol") or row.get("avg_volume")
    mcap = row.get("mcap_m")
    exchange = row.get("exchange") or ""
    rec = row.get("rec") or ""

    gap_score, mult = _value_gap_bonus(price, target_f)
    cent_zone = price <= cfg.cent_zone_max

    value_at_target = None
    if target_f and price > 0:
        shares = cfg.stake_usd / price
        value_at_target = round(shares * target_f, 2)

    hits_goal = value_at_target is not None and value_at_target >= cfg.target_dollar_goal
    price_x100 = mult is not None and mult >= cfg.target_100x
    stake_for_goal = (
        round(cfg.target_dollar_goal / mult, 4) if mult and mult > 0 else None
    )

    components = {
        "value_gap": gap_score,
        "maturity": _maturity_bonus(
            float(ret_1y) if ret_1y is not None else None,
            float(ret_3m) if ret_3m is not None else None,
        ),
        "liquidity": _liquidity_bonus(
            float(vol) if vol is not None else None,
            float(mcap) if mcap is not None else None,
        ),
        "exchange": _exchange_bonus(exchange),
        "analyst_rec": _rec_bonus(rec),
        "cent_zone": 30 if cent_zone else (10 if price <= 2 else 0),
        "x100_feasible": 35 if (hits_goal or price_x100) else 0,
    }

    total = sum(components.values())

    return MoneyballPick(
        ticker=str(row.get("ticker", "")).upper(),
        name=str(row.get("name", ""))[:80],
        price_now=round(price, 4),
        proj_target=round(target_f, 2) if target_f else None,
        moneyball_score=round(total, 1),
        upside_multiple=round(mult, 1) if mult else None,
        x100_feasible=hits_goal or price_x100,
        cent_zone=cent_zone,
        stake_usd=cfg.stake_usd,
        value_at_target_usd=value_at_target,
        stake_needed_for_goal_usd=stake_for_goal,
        ret_1y=float(ret_1y) if ret_1y is not None else None,
        ret_3m=float(ret_3m) if ret_3m is not None else None,
        mcap_m=float(mcap) if mcap is not None else None,
        exchange=exchange,
        rec=rec,
        vol=float(vol) if vol is not None else None,
        components=components,
        evidence={"source_row": row.get("_source", "penny_forward_screen_v1")},
    )


def aggregate_moneyball(cfg: MoneyballConfig | None = None) -> dict[str, Any]:
    cfg = cfg or MoneyballConfig()

    penny = _load_json(PENNY_RECEIPT)
    returns = _load_json(RETURN_RECEIPT)
    sec_count = 0
    if SEC_TICKERS.exists():
        sec_count = len(json.loads(SEC_TICKERS.read_text(encoding="utf-8")))

    rows: list[dict] = []
    if penny:
        rows.extend(penny.get("candidates") or penny.get("top") or [])
    supplement = _load_json(SUPPLEMENT_RECEIPT)
    if supplement:
        for row in supplement.get("candidates") or []:
            tagged = dict(row)
            tagged["_source"] = "moneyball_supplements_v1"
            rows.append(tagged)

    picks: list[MoneyballPick] = []
    matured = _matured_tickers(returns, penny)
    for row in rows:
        pick = score_candidate(row, cfg, matured=matured)
        if pick:
            picks.append(pick)

    picks.sort(key=lambda p: p.moneyball_score, reverse=True)
    top = picks[: cfg.top_k]

    matured_ref = None
    if returns:
        sanity = returns.get("runs", {}).get("sanity_sec_scan_full", {})
        h = sanity.get("highest") or {}
        matured_ref = {
            "ticker": h.get("ticker"),
            "return_pct": h.get("return_pct"),
            "note": "matured winner excluded from penny screen; moneyball seeks pre-run names",
        }
    if penny and penny.get("artv_reference"):
        matured_ref = penny["artv_reference"]

    cent_picks = [p for p in picks if p.cent_zone]
    x100_picks = [p for p in picks if p.x100_feasible]

    receipt = {
        "scan_type": "moneyball_aggregate_v1",
        "algorithm": "aggregate_devise_moneyball",
        "as_of": penny.get("as_of") if penny else None,
        "config": asdict(cfg),
        "inputs": {
            "penny_forward_screen": str(PENNY_RECEIPT.relative_to(ROOT)) if penny else None,
            "moneyball_supplements": str(SUPPLEMENT_RECEIPT.relative_to(ROOT))
            if supplement
            else None,
            "return_scan": str(RETURN_RECEIPT.relative_to(ROOT)) if returns else None,
            "sec_tickers_count": sec_count,
            "candidate_pool": len(rows),
            "matured_excluded": sorted(matured),
        },
        "matured_reference": matured_ref,
        "summary": {
            "scored": len(picks),
            "cent_zone_count": len(cent_picks),
            "x100_feasible_count": len(x100_picks),
            "best_cent_zone": asdict(cent_picks[0]) if cent_picks else None,
            "best_x100": asdict(x100_picks[0]) if x100_picks else None,
        },
        "moneyball_thesis": (
            f"Put ${cfg.stake_usd} in a cent-zone name; if price reaches analyst target, "
            f"position value scales by target/price. 100x = ${cfg.stake_usd} → ${cfg.stake_usd * 100}. "
            f"Goal ${cfg.target_dollar_goal} requires higher multiple or larger stake."
        ),
        "top_k": cfg.top_k,
        "top": [asdict(p) for p in top],
        "method": (
            "Aggregate penny screen + moneyball composite: value_gap, maturity, liquidity, "
            "exchange, analyst rec, cent_zone, 100x feasibility. NOT investment advice."
        ),
        "dedupe_method": "ticker_unique_score_rank",
        "created_at": utc_now(),
    }

    write_json(RECEIPT_PATH, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} moneyball_aggregate_v1.json status=ok",
    )
    write_dollar_to_million_playbook(moneyball=receipt, cfg=cfg)
    return receipt


def write_dollar_to_million_playbook(
    *,
    moneyball: dict[str, Any] | None = None,
    cfg: MoneyballConfig | None = None,
    goal_usd: float = 1_000_000.0,
) -> dict[str, Any]:
    """Wire $1 → $1M paths: memecoin launch playbook + best SEC stock slate."""
    cfg = cfg or MoneyballConfig()
    mb = moneyball or _load_json(RECEIPT_PATH) or {}
    top = mb.get("top") or []
    supplement = _load_json(SUPPLEMENT_RECEIPT) or {}

    stock_paths: list[dict[str, Any]] = []
    for row in top[:15]:
        price = float(row.get("price_now") or 0)
        target = row.get("proj_target")
        mult = row.get("upside_multiple")
        if not price or not target or not mult:
            continue
        stake_for_million = round(goal_usd / float(mult), 2) if float(mult) > 0 else None
        stock_paths.append(
            {
                "ticker": row.get("ticker"),
                "name": row.get("name"),
                "price_now": price,
                "proj_target": target,
                "upside_multiple": mult,
                "stake_usd_1": cfg.stake_usd,
                "value_at_target_from_1_usd": row.get("value_at_target_usd"),
                "stake_needed_for_1m_usd": stake_for_million,
                "moneyball_score": row.get("moneyball_score"),
                "cent_zone": row.get("cent_zone"),
                "exchange": row.get("exchange"),
                "source": (row.get("evidence") or {}).get("source_row"),
            }
        )

    gtbp = next(
        (c for c in supplement.get("candidates") or [] if c.get("ticker") == "GTBP"),
        None,
    )

    receipt = {
        "scan_type": "dollar_to_million_playbook_v1",
        "as_of": mb.get("as_of") or utc_now()[:10],
        "goal_usd": goal_usd,
        "llm_first": True,
        "verdict": (
            "$1 → $1,000,000 requires ~1,000,000×. SEC equities in this repo cap at ~20–60× "
            "on analyst targets. Only documented $1-ish → $1M paths are zero-day memecoin "
            "launch snipes (KEYCAT, ASTEROID, early SHIB). NOT investment advice."
        ),
        "paths": {
            "memecoin_launch": {
                "feasible_for_1_to_1m": True,
                "expected_hit_rate": "well under 1%",
                "documented_examples": [
                    {
                        "name": "KEYCAT (Base)",
                        "in_usd": 100,
                        "out_usd": 8_300_000,
                        "multiple": 83_000,
                        "horizon": "~1 week",
                        "source": "https://coingape.com/trending/trader-turned-100-crypto-investment-into-8-3-million-in-a-week-heres-how-he-did-it/",
                    },
                    {
                        "name": "ASTEROID (Solana)",
                        "in_usd": 575,
                        "out_usd": 1_000_000,
                        "multiple": 1740,
                        "horizon": "~2 days",
                        "source": "https://finbold.com/trader-turns-575-into-1-million-in-2-days-trading-this-crypto/",
                    },
                    {
                        "name": "SHIB (early)",
                        "in_usd": 650,
                        "out_usd": 1_700_000,
                        "multiple": 2615,
                        "horizon": "bull cycle",
                        "source": "https://thecryptobasic.com/2024/01/12/shiba-inu-investor-flips-650-to-a-1-7m-fortune/",
                    },
                    {
                        "name": "PEPE (early)",
                        "in_usd": 3000,
                        "out_usd": 73_000_000,
                        "multiple": 24656,
                        "horizon": "~20 months",
                        "source": "https://dailyhodl.com/2024/12/10/trader-turns-3000-investment-into-73000000-with-frog-themed-memecoin-pepe-lookonchain/",
                    },
                ],
                "monitor_checklist": [
                    "Wallet: Phantom (Solana) or Base wallet; keep $5–10 gas + $1 buy size",
                    "Watch: Pump.fun new deploys, Bonk launchpad, Base new pairs (DexScreener / Birdeye)",
                    "Entry: first 5–30 minutes while mcap often $3K–$100K",
                    "Size: literal $1 per attempt; expect 99%+ total loss",
                    "Exit rules: take partial at 10×, 100×; never hold illiquid to zero",
                    "On-chain verify: liquidity locked, mint revoked, holder concentration",
                ],
            },
            "sec_penny_stocks": {
                "feasible_for_1_to_1m": False,
                "best_asymmetric_add": gtbp,
                "stock_paths_from_moneyball": stock_paths,
                "note": (
                    "For $1M from stocks use stake_needed_for_1m_usd column (~$17k–$50k at analyst targets). "
                    "GTBP added via moneyball_supplements (NK-cell asymmetry vs peer mcap)."
                ),
            },
        },
        "wired_inputs": {
            "moneyball_aggregate": str(RECEIPT_PATH.relative_to(ROOT)),
            "moneyball_supplements": str(SUPPLEMENT_RECEIPT.relative_to(ROOT)),
            "penny_forward_screen": str(PENNY_RECEIPT.relative_to(ROOT)),
            "return_scan": str(RETURN_RECEIPT.relative_to(ROOT)),
        },
        "commands": [
            "bin/mabel-catalog moneyball --sync --goal 1000000",
            "bin/mabel-catalog financial",
            "bin/mabel-catalog sync-financial",
        ],
        "method": "LLM-first synthesis + moneyball stake math for $1M goal. NOT investment advice.",
        "created_at": utc_now(),
    }

    write_json(PLAYBOOK_RECEIPT, receipt)
    append_log(
        ROOT / "reports" / "build_status.log",
        f"{utc_now()} dollar_to_million_playbook_v1.json status=ok",
    )
    return receipt


def dollars_from_cent_to_goal(price: float, target: float, stake: float = 1.0, goal: float = 100.0) -> dict:
    """If you stake $1 at price P, value at target T; what multiple hits $100?"""
    if price <= 0:
        return {}
    shares = stake / price
    at_target = shares * target
    mult = target / price
    stake_for_goal = goal / mult if mult > 0 else None
    return {
        "stake_usd": stake,
        "price": price,
        "target": target,
        "shares": shares,
        "value_at_target_usd": round(at_target, 2),
        "multiple": round(mult, 1),
        "stake_needed_for_goal_usd": round(stake_for_goal, 4) if stake_for_goal else None,
    }
