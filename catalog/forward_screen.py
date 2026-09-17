"""
Penny-forward screen: find sub-$5 stocks that have not already run up,
then score survivors for next-year upside potential.

Algorithm (3 phases)
--------------------
Phase 1 — Local universe (0 API calls)
  Load SEC tickers, drop warrants/units/delisted-pattern symbols.

Phase 2 — Batch price history (1 Yahoo call per batch)
  yf.download(batch, start=1y) once per batch; derive price, returns,
  and volume locally. No per-ticker .history() calls.

Phase 3 — Metadata enrichment (1 call per survivor, capped)
  Fetch .info only for top preliminary scorers (default 200), not every
  sub-$5 name. Re-rank with analyst targets, sector, liquidity.

Compared to the ad-hoc loop (~3 tickers/sec, ~45 min ETA for 9.6k names),
this design targets ~80–150 tickers/sec on phase 2 and finishes in
~5–15 minutes depending on Yahoo rate limits.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yfinance as yf

from catalog.config import BUILD_REPORTS, ROOT, utc_now

SEC_TICKERS = ROOT / "_unwrapped/sec_filings/company_tickers.json"
RECEIPT_PATH = BUILD_REPORTS / "penny_forward_screen_v1.json"

JUNK_MARKERS = ("-WT", "-WS", "/WS", "/WT", "-UN", "-RI", "-PA", "-PB", "-PC", "-PD", "-PE", "-PF", "-PG")
MAJOR_EXCHANGES = frozenset({"NMS", "NGM", "NCM", "NYQ", "ASE"})


@dataclass
class ScreenConfig:
    max_price: float = 5.0
    max_ret_1y_pct: float = 150.0
    max_ret_3m_pct: float = 80.0
    min_history_days: int = 60
    batch_size: int = 120
    batch_sleep_sec: float = 0.6
    enrich_top_n: int = 200
    enrich_sleep_sec: float = 0.4
    top_k: int = 25
    lookback_days: int = 365
    lookback_3m_days: int = 63


@dataclass
class Candidate:
    ticker: str
    name: str
    px: float
    ret_1y: float
    ret_3m: float
    avg_volume: float | None = None
    preliminary_score: float = 0.0
    mcap_m: float | None = None
    target: float | None = None
    upside_pct: float | None = None
    sector: str = ""
    industry: str = ""
    exchange: str = ""
    rec: str = ""
    score: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)


def is_junk_ticker(ticker: str) -> bool:
    t = ticker.upper()
    if any(m in t for m in JUNK_MARKERS):
        return True
    if "WARRANT" in t:
        return True
    if t.endswith("W") and len(t) > 4:
        return True
    return False


def load_sec_universe(path: Path = SEC_TICKERS) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    meta: dict[str, str] = {}
    for row in data.values():
        ticker = (row.get("ticker") or "").strip().upper()
        if not ticker or is_junk_ticker(ticker):
            continue
        meta[ticker] = (row.get("title") or "")[:80]
    return meta


def preliminary_score(
    *,
    px: float,
    ret_1y: float,
    ret_3m: float,
    avg_volume: float | None,
) -> float:
    """Price-action score before analyst metadata. Higher = better candidate."""
    score = 0.0
    # Prefer names still cheap and not already running
    if 1.0 <= px <= 4.0:
        score += 30
    elif px <= 5.0:
        score += 15
    score += max(0.0, 50 - ret_1y * 0.25)
    score += max(0.0, 30 - ret_3m * 0.4)
    if avg_volume and avg_volume >= 200_000:
        score += 20
    elif avg_volume and avg_volume >= 50_000:
        score += 10
    return round(score, 2)


def final_score(
    *,
    preliminary: float,
    upside_pct: float | None,
    sector: str,
    industry: str,
    rec: str,
    mcap: float | None,
    avg_volume: float | None,
    exchange: str,
    ret_3m: float,
) -> float:
    score = preliminary * 0.35
    if upside_pct is not None:
        score += min(upside_pct, 800) * 0.45
    ind = industry.lower()
    if "biotech" in ind or "biotechnology" in ind or sector == "Healthcare":
        score += 40
    if rec in ("buy", "strong_buy"):
        score += 25
    if mcap and 50_000_000 <= mcap <= 2_000_000_000:
        score += 20
    if avg_volume and avg_volume >= 200_000:
        score += 15
    if exchange in MAJOR_EXCHANGES:
        score += 10
    score -= max(0.0, ret_3m) * 0.3
    return round(score, 2)


def _batch_download(
    batch: list[str],
    start: date,
    end: date,
) -> Any:
    return yf.download(
        batch,
        start=start.isoformat(),
        end=end.isoformat(),
        group_by="ticker",
        threads=True,
        progress=False,
        auto_adjust=True,
    )


def _extract_close(data: Any, ticker: str, batch_len: int):
    if batch_len == 1:
        if data is None or data.empty:
            return None
        return data["Close"]
    if ticker not in data.columns.get_level_values(0):
        return None
    sub = data[ticker]
    if sub is None or sub.empty:
        return None
    return sub["Close"]


def _extract_volume(data: Any, ticker: str, batch_len: int):
    if batch_len == 1:
        if data is None or data.empty or "Volume" not in data.columns:
            return None
        return data["Volume"]
    if ticker not in data.columns.get_level_values(0):
        return None
    sub = data[ticker]
    if sub is None or sub.empty or "Volume" not in sub.columns:
        return None
    return sub["Volume"]


def phase2_price_screen(
    universe: dict[str, str],
    cfg: ScreenConfig,
    *,
    log_fn=None,
) -> tuple[list[Candidate], dict[str, Any]]:
    end = date.today()
    start = end - timedelta(days=cfg.lookback_days)
    tickers = sorted(universe)
    survivors: list[Candidate] = []
    stats = {
        "tickers_total": len(tickers),
        "batches": 0,
        "priced": 0,
        "passed_price_filter": 0,
        "errors": 0,
        "elapsed_sec": 0.0,
    }
    t0 = time.monotonic()

    for i in range(0, len(tickers), cfg.batch_size):
        batch = tickers[i : i + cfg.batch_size]
        stats["batches"] += 1
        try:
            data = _batch_download(batch, start, end)
        except Exception:
            stats["errors"] += 1
            time.sleep(cfg.batch_sleep_sec * 3)
            continue

        for t in batch:
            try:
                close = _extract_close(data, t, len(batch))
                if close is None:
                    continue
                close = close.dropna()
                if len(close) < cfg.min_history_days:
                    continue
                stats["priced"] += 1

                px = float(close.iloc[-1])
                if px <= 0 or px > cfg.max_price:
                    continue

                px_1y = float(close.iloc[0])
                px_3m = float(close.iloc[max(0, len(close) - cfg.lookback_3m_days)])
                ret_1y = (px / px_1y - 1) * 100 if px_1y > 0 else 0.0
                ret_3m = (px / px_3m - 1) * 100 if px_3m > 0 else 0.0

                if ret_1y > cfg.max_ret_1y_pct or ret_3m > cfg.max_ret_3m_pct:
                    continue

                vol_s = _extract_volume(data, t, len(batch))
                avg_vol = float(vol_s.dropna().tail(20).mean()) if vol_s is not None and not vol_s.dropna().empty else None

                pre = preliminary_score(px=px, ret_1y=ret_1y, ret_3m=ret_3m, avg_volume=avg_vol)
                survivors.append(
                    Candidate(
                        ticker=t,
                        name=universe[t],
                        px=round(px, 3),
                        ret_1y=round(ret_1y, 1),
                        ret_3m=round(ret_3m, 1),
                        avg_volume=round(avg_vol, 0) if avg_vol else None,
                        preliminary_score=pre,
                        evidence={"phase": "price_batch", "px_1y": round(px_1y, 4), "px_3m": round(px_3m, 4)},
                    )
                )
                stats["passed_price_filter"] += 1
            except Exception:
                continue

        if log_fn and i and i % (cfg.batch_size * 10) == 0:
            log_fn(f"phase2 progress {i}/{len(tickers)} survivors={len(survivors)}")
        time.sleep(cfg.batch_sleep_sec)

    stats["elapsed_sec"] = round(time.monotonic() - t0, 2)
    survivors.sort(key=lambda c: c.preliminary_score, reverse=True)
    return survivors, stats


def phase3_enrich(
    candidates: list[Candidate],
    cfg: ScreenConfig,
    *,
    log_fn=None,
) -> tuple[list[Candidate], dict[str, Any]]:
    pool = candidates[: cfg.enrich_top_n]
    stats = {"enriched": 0, "errors": 0, "elapsed_sec": 0.0}
    t0 = time.monotonic()

    for c in pool:
        try:
            info = yf.Ticker(c.ticker).info or {}
            mcap = info.get("marketCap") or 0
            sector = info.get("sector") or ""
            industry = (info.get("industry") or "")[:40]
            exchange = info.get("exchange") or info.get("quoteType") or ""
            target = info.get("targetMeanPrice") or info.get("targetMedianPrice")
            rec = info.get("recommendationKey") or ""
            vol = info.get("averageVolume") or info.get("averageVolume10days") or c.avg_volume
            upside = ((target / c.px) - 1) * 100 if target and target > 0 else None

            c.mcap_m = round(mcap / 1e6, 1) if mcap else None
            c.sector = sector
            c.industry = industry
            c.exchange = exchange
            c.target = round(float(target), 2) if target else None
            c.upside_pct = round(upside, 1) if upside is not None else None
            c.rec = rec
            if vol:
                c.avg_volume = float(vol)
            c.score = final_score(
                preliminary=c.preliminary_score,
                upside_pct=c.upside_pct,
                sector=sector,
                industry=industry,
                rec=rec,
                mcap=mcap,
                avg_volume=c.avg_volume,
                exchange=exchange,
                ret_3m=c.ret_3m,
            )
            c.evidence["phase"] = "enriched"
            stats["enriched"] += 1
        except Exception:
            stats["errors"] += 1
            c.score = c.preliminary_score
        time.sleep(cfg.enrich_sleep_sec)

    stats["elapsed_sec"] = round(time.monotonic() - t0, 2)
    pool.sort(key=lambda c: c.score, reverse=True)
    if log_fn:
        log_fn(f"phase3 enriched={stats['enriched']} errors={stats['errors']}")
    return pool, stats


def run_forward_screen(cfg: ScreenConfig | None = None) -> dict[str, Any]:
    cfg = cfg or ScreenConfig()
    t0 = time.monotonic()

    universe = load_sec_universe()
    survivors, p2_stats = phase2_price_screen(universe, cfg, log_fn=print)
    enriched, p3_stats = phase3_enrich(survivors, cfg, log_fn=print)

    top = enriched[: cfg.top_k]
    receipt = {
        "scan_type": "penny_forward_screen_v1",
        "algorithm": "3_phase_batch_price_then_enrich",
        "as_of": date.today().isoformat(),
        "config": asdict(cfg),
        "universe": {
            "source": str(SEC_TICKERS.relative_to(ROOT)),
            "tickers_after_junk_filter": len(universe),
        },
        "phase2": p2_stats,
        "phase3": p3_stats,
        "survivor_count": len(survivors),
        "enriched_count": len(enriched),
        "top_k": cfg.top_k,
        "top": [asdict(c) for c in top],
        "method": (
            "SEC tickers; price<=${max_price}; not matured (1y<={max_ret_1y_pct}%, "
            "3m<={max_ret_3m_pct}%); batch history screen; analyst-upside enrich"
        ).format(
            max_price=cfg.max_price,
            max_ret_1y_pct=cfg.max_ret_1y_pct,
            max_ret_3m_pct=cfg.max_ret_3m_pct,
        ),
        "dedupe_method": "ticker_unique_per_run",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "created_at": utc_now(),
        "notes": [
            "Not a prediction model; heuristic screen from SEC identifiers + Yahoo prices.",
            "Phase 2 uses 1 batch download per {} tickers vs per-ticker history calls.".format(cfg.batch_size),
            "Compare to ad-hoc loop: ~3 tickers/sec -> this targets ~80-150 tickers/sec on phase 2.",
        ],
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt
