"""
Full market scan: price every ticker we can derive from on-disk identifiers
(SEC company_tickers + JPX/Xetra/KRX listings) and compute 1-year returns.

Emits, with sanity filters and partial-progress checkpoints:
  - build_reports/market_scan_returns_v1.json   (top-50 sane + raw max + per-market)
  - build_reports/penny_forward_full_v1.json     (all priced <= $5, not matured)
  - build_reports/moneyball_price_refresh_v1.json (current prices for the slate)

Yahoo is rate-limited; this throttles hard and checkpoints so a kill/restart
keeps prior progress. NOT investment advice.
"""

from __future__ import annotations

import csv
import datetime
import json
import time
from pathlib import Path
from typing import Any

from catalog.config import BUILD_REPORTS, ROOT, utc_now
from catalog.util import append_log, write_json

SEC_TICKERS = ROOT / "_unwrapped/sec_filings/company_tickers.json"
EXCHANGES = ROOT / "_unwrapped/exchanges"
CHECKPOINT = BUILD_REPORTS / "market_scan_checkpoint_v1.json"
RETURNS_RECEIPT = BUILD_REPORTS / "market_scan_returns_v1.json"
PENNY_FULL_RECEIPT = BUILD_REPORTS / "penny_forward_full_v1.json"
PRICE_REFRESH_RECEIPT = BUILD_REPORTS / "moneyball_price_refresh_v1.json"
MONEYBALL_RECEIPT = BUILD_REPORTS / "moneyball_aggregate_v1.json"

MONEYBALL_SLATE = [
    "HOWL", "JSPR", "MDCX", "AIM", "ENSC", "TPST", "IGC", "SLXN",
    "GTBP", "MDNAF", "ESLA", "SNTI", "REVB", "RVPH", "CELZ",
]


def _sec_tickers() -> dict[str, dict]:
    if not SEC_TICKERS.exists():
        return {}
    raw = json.loads(SEC_TICKERS.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for v in raw.values():
        t = (v.get("ticker") or "").upper().strip()
        if t and "-" not in t and not t.endswith("W"):
            out[t] = {"market": "SEC", "name": v.get("title", "")}
    return out


def _read_csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh))


def _exchange_tickers() -> dict[str, dict]:
    out: dict[str, dict] = {}
    # JPX: full TSE listed issues (Local Code -> .T)
    for path in ("jpx/tse_listed_issues.csv", "jpx/jpx_auto_companies.csv"):
        for row in _read_csv_rows(EXCHANGES / path):
            code = (row.get("Local Code") or "").strip()
            if code:
                out[f"{code}.T"] = {"market": "JPX", "name": row.get("Name (English)", "")}
    # Xetra: curated mnemonics (-> .DE)
    for row in _read_csv_rows(EXCHANGES / "deutsche_boerse/xetra_auto_companies.csv"):
        mnem = (row.get("Mnemonic") or "").strip()
        if mnem:
            out[f"{mnem}.DE"] = {"market": "XETRA", "name": row.get("Instrument", "")}
    # KRX: full listed companies (종목코드 -> .KS/.KQ); codes may be alphanumeric
    for path in ("krx/krx_listed_companies.csv", "krx/krx_auto_companies.csv"):
        for row in _read_csv_rows(EXCHANGES / path):
            code = (row.get("종목코드") or "").strip()
            market = row.get("시장구분") or ""
            if code and len(code) == 6:
                suffix = ".KQ" if "코스닥" in market else ".KS"
                out[f"{code}{suffix}"] = {"market": "KRX", "name": row.get("회사명", "")}
    return out


def _load_checkpoint() -> dict[str, Any]:
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"priced": {}}


def run_market_scan(
    *,
    batch_size: int = 30,
    sleep_between: float = 1.6,
    max_return_cap: float = 500.0,
    min_start_price: float = 1.0,
    penny_max: float = 5.0,
    resume: bool = True,
) -> dict[str, Any]:
    import yfinance as yf

    universe = {**_sec_tickers(), **_exchange_tickers()}
    end = datetime.date.today()
    start = end - datetime.timedelta(days=365)

    ckpt = _load_checkpoint() if resume else {"priced": {}}
    priced: dict[str, dict] = ckpt.get("priced", {})

    tickers = [t for t in sorted(universe) if t not in priced]
    log = ROOT / "reports" / "catalog_run.log"
    append_log(log, f"{utc_now()} market-scan start universe={len(universe)} todo={len(tickers)}")

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i : i + batch_size]
        for attempt in range(3):
            try:
                data = yf.download(
                    batch, start=start.isoformat(), end=end.isoformat(),
                    group_by="ticker", threads=True, progress=False, auto_adjust=True,
                )
                break
            except Exception:
                time.sleep(4 * (attempt + 1))
                data = None
        if data is None:
            continue
        for t in batch:
            rec: dict[str, Any] = {"market": universe[t]["market"], "name": universe[t]["name"][:60]}
            try:
                close = (data["Close"] if len(batch) == 1 else data[t]["Close"]).dropna()
                if len(close) >= 20:
                    s, e = float(close.iloc[0]), float(close.iloc[-1])
                    if s > 0:
                        rec.update({"start": round(s, 4), "end": round(e, 4), "ret_1y": round((e / s - 1) * 100, 2)})
            except Exception:
                pass
            priced[t] = rec
        if i % (batch_size * 20) == 0:
            write_json(CHECKPOINT, {"priced": priced, "updated_at": utc_now(), "done": len(priced), "total": len(universe)})
            append_log(log, f"{utc_now()} market-scan progress {len(priced)}/{len(universe)}")
        time.sleep(sleep_between)

    write_json(CHECKPOINT, {"priced": priced, "updated_at": utc_now(), "done": len(priced), "total": len(universe)})

    valid = {t: r for t, r in priced.items() if "ret_1y" in r}
    sane = [
        {"ticker": t, **r}
        for t, r in valid.items()
        if r.get("start", 0) >= min_start_price and r["ret_1y"] <= max_return_cap
    ]
    sane.sort(key=lambda r: r["ret_1y"], reverse=True)
    raw = [{"ticker": t, **r} for t, r in valid.items()]
    raw.sort(key=lambda r: r["ret_1y"], reverse=True)

    per_market: dict[str, dict] = {}
    for t, r in valid.items():
        m = r["market"]
        if r.get("start", 0) >= min_start_price and r["ret_1y"] <= max_return_cap:
            cur = per_market.get(m)
            if not cur or r["ret_1y"] > cur["ret_1y"]:
                per_market[m] = {"ticker": t, **r}

    returns_receipt = {
        "scan_type": "market_scan_returns_v1",
        "period": f"{start.isoformat()} to {end.isoformat()}",
        "universe_size": len(universe),
        "priced": len(valid),
        "filters": {"min_start_price": min_start_price, "max_return_cap": max_return_cap},
        "top_50_sane": sane[:50],
        "raw_max": raw[0] if raw else None,
        "best_per_market": per_market,
        "created_at": utc_now(),
    }
    write_json(RETURNS_RECEIPT, returns_receipt)

    penny = [
        {"ticker": t, **r}
        for t, r in valid.items()
        if 0 < r.get("end", 0) <= penny_max and r["ret_1y"] < 120
    ]
    penny.sort(key=lambda r: r["ret_1y"])
    write_json(
        PENNY_FULL_RECEIPT,
        {
            "scan_type": "penny_forward_full_v1",
            "as_of": end.isoformat(),
            "method": "all priced tickers <= $5 not matured (ret_1y<120%); price-only, no analyst enrich",
            "count": len(penny),
            "candidates": penny[:200],
            "created_at": utc_now(),
        },
    )

    refresh = {t: priced.get(t, {}) for t in MONEYBALL_SLATE}
    write_json(
        PRICE_REFRESH_RECEIPT,
        {
            "scan_type": "moneyball_price_refresh_v1",
            "as_of": end.isoformat(),
            "slate_prices": refresh,
            "created_at": utc_now(),
        },
    )

    append_log(log, f"{utc_now()} market-scan done priced={len(valid)} sane={len(sane)} penny={len(penny)}")
    return {
        "universe": len(universe),
        "priced": len(valid),
        "top_sane": sane[:10],
        "raw_max": raw[0] if raw else None,
        "penny_count": len(penny),
        "receipts": [
            str(RETURNS_RECEIPT.relative_to(ROOT)),
            str(PENNY_FULL_RECEIPT.relative_to(ROOT)),
            str(PRICE_REFRESH_RECEIPT.relative_to(ROOT)),
        ],
    }
