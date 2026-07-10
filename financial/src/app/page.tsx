import Link from "next/link";
import { Section } from "@/components/Section";
import { StatCard } from "@/components/StatCard";
import { TopFiveBoard } from "@/components/TopFiveBoard";
import {
  fmtNum,
  fmtPct,
  fmtUsd,
  getCommodityEconomy,
  getFreightMovement,
  getMarketScan,
  getMillionPlaybook,
  getMoneyball,
  getPennyForward,
  getReturnScan,
} from "@/lib/data";

export default function Home() {
  const scan = getReturnScan();
  const market = getMarketScan();
  const penny = getPennyForward();
  const moneyball = getMoneyball();
  const million = getMillionPlaybook();
  const freightMv = getFreightMovement();
  const commodity = getCommodityEconomy();
  const raw = scan.runs.raw_sec_scan;
  const sanity = scan.runs.sanity_sec_scan_full;
  const freightBasket = scan.prior_validated_basket?.highest;
  const bestMb = moneyball.summary.best_cent_zone;

  const leaders = [
    {
      label: "Filtered winner",
      ticker: sanity?.highest.ticker ?? "—",
      return_pct: sanity?.highest.return_pct,
      start: sanity?.highest.start_usd,
      end: sanity?.highest.end_usd,
      note: "Artiva Biotherapeutics — real biotech run",
      legit: true,
    },
    {
      label: "Freight basket",
      ticker: freightBasket?.ticker ?? "—",
      return_pct: freightBasket?.return_pct,
      note: "Best verified name from FMCSA-linked public basket",
      legit: true,
    },
    {
      label: "Raw max (artifact)",
      ticker: raw?.raw_highest.ticker ?? "—",
      return_pct: raw?.raw_highest.return_pct,
      start: raw?.raw_highest.start_usd,
      end: raw?.raw_highest.end_usd,
      note: raw?.raw_highest.note,
      legit: false,
    },
    {
      label: "Exchange sample",
      ticker: scan.runs.exchange_sample?.highest.ticker ?? "—",
      return_pct: scan.runs.exchange_sample?.highest.return_pct,
      start: scan.runs.exchange_sample?.highest.start_usd,
      end: scan.runs.exchange_sample?.highest.end_usd,
      note: "Toyota (7203.T) from JPX sample",
      legit: true,
    },
  ];

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <Link
        href="/iran"
        className="mb-4 inline-flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 transition hover:border-zinc-500"
      >
        <span className="font-semibold">Iran · oil · truck</span>
        <span className="text-zinc-500">EIA · Census · haul proof</span>
        <span aria-hidden>→</span>
      </Link>
      <Link
        href="/thg"
        className="mb-8 ml-0 inline-flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-900/40 px-4 py-3 text-sm text-zinc-100 transition hover:border-zinc-500 sm:ml-3"
      >
        <span className="font-semibold text-zinc-200">THG map</span>
        <span className="text-zinc-500">Petroleum +55% corridors</span>
        <span aria-hidden>→</span>
      </Link>
      <header className="mb-10 border-b border-zinc-800 pb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-500">
          Mabeline
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Truck as sensor · commodity as signal
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-zinc-400">
          Public transport evidence graph. Financial screens below are secondary.{" "}
          <Link href="/commodity" className="text-amber-400 hover:underline">
            Commodity economy
          </Link>
          . Not investment advice.
        </p>
      </header>

      <TopFiveBoard
        asOf={market.created_at.slice(0, 10)}
        returns={market.top_50_sane}
        moneyball={moneyball.top}
        penny={penny.top}
      />

      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="SEC tickers priced"
          value={String(sanity?.tickers_priced ?? raw?.tickers_priced ?? "—")}
          sub="Sanity-filtered full pass"
          tone="accent"
        />
        <StatCard
          label="Moneyball #1"
          value={bestMb?.ticker ?? "—"}
          sub={
            bestMb
              ? `mb=${bestMb.moneyball_score.toFixed(0)} · ${fmtUsd(bestMb.price_now)}`
              : "—"
          }
          tone="up"
        />
        <StatCard
          label="Cent zone"
          value={String(moneyball.summary.cent_zone_count)}
          sub={`${moneyball.summary.scored} scored`}
          tone="neutral"
        />
        <StatCard
          label="$1 → $1M"
          value={million.paths.memecoin_launch.feasible_for_1_to_1m ? "Memecoin" : "—"}
          sub={
            million.paths.sec_penny_stocks.stock_paths_from_moneyball[0]
              ? `${million.paths.sec_penny_stocks.stock_paths_from_moneyball[0].ticker} needs $${fmtNum(million.paths.sec_penny_stocks.stock_paths_from_moneyball[0].stake_needed_for_1m_usd, 0)} for stock path`
              : "playbook wired"
          }
          tone="up"
        />
        <StatCard
          label={`FAF5 ${freightMv.year}`}
          value={`${fmtNum(freightMv.totals.billion_tons_equiv, 1)}B t`}
          sub={`Top: ${commodity.unified_commodity_slate[0]?.commodity ?? "—"} → /commodity`}
          tone="accent"
        />
      </div>

      <div className="mt-10 space-y-10">
        <Section
          title="Moneyball aggregate (1¢ → $100)"
          description={moneyball.moneyball_thesis}
        >
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900 text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Ticker</th>
                  <th className="px-4 py-3">Price</th>
                  <th className="px-4 py-3">MB</th>
                  <th className="px-4 py-3">Path to $100</th>
                  <th className="px-4 py-3">Multiple</th>
                  <th className="px-4 py-3">Zone</th>
                  <th className="px-4 py-3">Name</th>
                </tr>
              </thead>
              <tbody>
                {moneyball.top.map((row, i) => {
                  const path = row.x100_feasible
                    ? `$${row.stake_usd}→$${row.value_at_target_usd ?? 0}`
                    : row.stake_needed_for_goal_usd
                      ? `$${row.stake_needed_for_goal_usd.toFixed(2)}→$100`
                      : "—";
                  return (
                    <tr
                      key={row.ticker}
                      className="border-b border-zinc-800/80 last:border-0"
                    >
                      <td className="px-4 py-3 text-zinc-500">{i + 1}</td>
                      <td className="px-4 py-3 font-mono font-semibold text-white">
                        {row.ticker}
                      </td>
                      <td className="px-4 py-3 font-mono">{fmtUsd(row.price_now)}</td>
                      <td className="px-4 py-3 font-mono text-amber-300">
                        {row.moneyball_score.toFixed(0)}
                      </td>
                      <td className="px-4 py-3 font-mono text-emerald-400">{path}</td>
                      <td className="px-4 py-3 font-mono text-zinc-400">
                        {row.upside_multiple != null ? `${row.upside_multiple}x` : "—"}
                      </td>
                      <td className="px-4 py-3 text-xs">
                        {row.cent_zone ? (
                          <span className="rounded bg-emerald-950 px-2 py-0.5 text-emerald-400">
                            CENT
                          </span>
                        ) : (
                          <span className="text-zinc-600">—</span>
                        )}
                        {row.x100_feasible && (
                          <span className="ml-1 rounded bg-amber-950 px-2 py-0.5 text-amber-400">
                            100x+
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-zinc-400">{row.name}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-zinc-600">{moneyball.method}</p>
        </Section>

        <Section
          title="$1 → $1,000,000 playbook"
          description={million.verdict}
        >
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4">
              <h3 className="text-sm font-semibold text-emerald-400">
                Memecoin launch (only $1→$1M path)
              </h3>
              <ul className="mt-3 space-y-2 text-xs text-zinc-400">
                {million.paths.memecoin_launch.monitor_checklist.map((line) => (
                  <li key={line}>• {line}</li>
                ))}
              </ul>
              <div className="mt-4 overflow-hidden rounded-xl border border-zinc-800">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-900 text-zinc-500">
                      <th className="px-3 py-2 text-left">Example</th>
                      <th className="px-3 py-2 text-right">In</th>
                      <th className="px-3 py-2 text-right">Out</th>
                    </tr>
                  </thead>
                  <tbody>
                    {million.paths.memecoin_launch.documented_examples.map((ex) => (
                      <tr key={ex.name} className="border-b border-zinc-800/80">
                        <td className="px-3 py-2 text-zinc-300">{ex.name}</td>
                        <td className="px-3 py-2 text-right font-mono">
                          {fmtUsd(ex.in_usd)}
                        </td>
                        <td className="px-3 py-2 text-right font-mono text-emerald-400">
                          {fmtUsd(ex.out_usd)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4">
              <h3 className="text-sm font-semibold text-amber-400">
                SEC penny path (stake needed for $1M)
              </h3>
              <p className="mt-2 text-xs text-zinc-500">
                {million.paths.sec_penny_stocks.note}
              </p>
              <div className="mt-4 overflow-hidden rounded-xl border border-zinc-800">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-900 text-zinc-500">
                      <th className="px-3 py-2 text-left">Ticker</th>
                      <th className="px-3 py-2 text-right">Price</th>
                      <th className="px-3 py-2 text-right">Stake→$1M</th>
                      <th className="px-3 py-2 text-right">Mult</th>
                    </tr>
                  </thead>
                  <tbody>
                    {million.paths.sec_penny_stocks.stock_paths_from_moneyball
                      .slice(0, 8)
                      .map((row) => (
                        <tr key={row.ticker} className="border-b border-zinc-800/80">
                          <td className="px-3 py-2 font-mono text-white">{row.ticker}</td>
                          <td className="px-3 py-2 text-right font-mono">
                            {fmtUsd(row.price_now)}
                          </td>
                          <td className="px-3 py-2 text-right font-mono text-amber-300">
                            {row.stake_needed_for_1m_usd != null
                              ? fmtUsd(row.stake_needed_for_1m_usd)
                              : "—"}
                          </td>
                          <td className="px-3 py-2 text-right font-mono text-zinc-400">
                            {row.upside_multiple}x
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Section>

        <Section
          title="1-year return leaders"
          description="Sanity filters: start price ≥ $1, return capped at +500% for filtered scan."
        >
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900 text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Ticker</th>
                  <th className="px-4 py-3">Return</th>
                  <th className="px-4 py-3">Start → End</th>
                  <th className="px-4 py-3">Note</th>
                </tr>
              </thead>
              <tbody>
                {leaders.map((row) => (
                  <tr
                    key={row.label}
                    className="border-b border-zinc-800/80 last:border-0"
                  >
                    <td className="px-4 py-3 text-zinc-300">{row.label}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-white">
                      {row.ticker}
                    </td>
                    <td
                      className={`px-4 py-3 font-mono ${
                        row.legit ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {row.return_pct != null && row.return_pct > 1000
                        ? "artifact"
                        : fmtPct(row.return_pct)}
                    </td>
                    <td className="px-4 py-3 font-mono text-zinc-400">
                      {row.start != null
                        ? `${fmtUsd(row.start)} → ${fmtUsd(row.end)}`
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-zinc-500">{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        <Section title="Penny-forward candidates" description={penny.method}>
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900 text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Ticker</th>
                  <th className="px-4 py-3">Price</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">1Y</th>
                  <th className="px-4 py-3">Upside</th>
                  <th className="px-4 py-3">Name</th>
                </tr>
              </thead>
              <tbody>
                {penny.top.map((c, i) => (
                  <tr
                    key={c.ticker}
                    className="border-b border-zinc-800/80 last:border-0"
                  >
                    <td className="px-4 py-3 text-zinc-500">{i + 1}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-white">
                      {c.ticker}
                    </td>
                    <td className="px-4 py-3 font-mono">{fmtUsd(c.px)}</td>
                    <td className="px-4 py-3 font-mono text-amber-300">
                      {c.score.toFixed(0)}
                    </td>
                    <td className="px-4 py-3 font-mono text-zinc-400">
                      {fmtPct(c.ret_1y, 0)}
                    </td>
                    <td className="px-4 py-3 font-mono text-emerald-400">
                      {fmtPct(c.upside_pct, 0)}
                    </td>
                    <td className="px-4 py-3 text-zinc-400">{c.name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-zinc-600">
            {penny.survivor_count} survivors · as of {penny.as_of}
            {penny.artv_reference
              ? ` · ${penny.artv_reference.ticker} excluded (${penny.artv_reference.note})`
              : ""}
          </p>
        </Section>

        <Section
          title="Commodity economy"
          description={
            <>
              Unified physical slate from FAF5 + CFS + crude imports + USGS.{" "}
              <Link href="/commodity" className="text-amber-400 hover:underline">
                Full view →
              </Link>
            </>
          }
        >
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900 text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-4 py-3">Commodity</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">FAF5</th>
                  <th className="px-4 py-3">CFS</th>
                  <th className="px-4 py-3">Mode</th>
                </tr>
              </thead>
              <tbody>
                {commodity.unified_commodity_slate.slice(0, 8).map((row) => (
                  <tr
                    key={row.sctg}
                    className="border-b border-zinc-800/80 last:border-0"
                  >
                    <td className="px-4 py-3 text-white">{row.commodity}</td>
                    <td className="px-4 py-3 font-mono text-amber-300">
                      {row.economy_score.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 font-mono text-zinc-400">
                      {row.faf5_pct != null ? `${row.faf5_pct}%` : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono text-zinc-400">
                      {row.cfs_pct != null ? `${row.cfs_pct}%` : "—"}
                    </td>
                    <td className="px-4 py-3 text-zinc-500">{row.primary_mode ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        <Section
          title={`National freight movement (FAF5 ${freightMv.year})`}
          description={freightMv.what_this_is}
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                By mode
              </h3>
              <ul className="mt-3 space-y-2">
                {freightMv.by_mode.slice(0, 5).map((m) => (
                  <li
                    key={m.mode}
                    className="flex justify-between font-mono text-sm text-zinc-300"
                  >
                    <span>{m.mode}</span>
                    <span className="text-emerald-400">{m.pct_of_tons.toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Top corridor
              </h3>
              <p className="mt-3 font-mono text-sm text-white">
                {freightMv.top_corridors[0]?.corridor ?? "—"}
              </p>
              <p className="mt-1 font-mono text-xs text-zinc-500">
                {fmtNum(freightMv.top_corridors[0]?.thousand_tons, 0)} kt
              </p>
              <ul className="mt-4 space-y-1 text-xs text-zinc-600">
                {freightMv.what_this_is_not.map((n) => (
                  <li key={n}>· Not: {n}</li>
                ))}
              </ul>
            </div>
          </div>
        </Section>

        <Section title="Data sources">
          <ul className="grid gap-2 sm:grid-cols-2">
            {scan.sources.map((s) => (
              <li
                key={s}
                className="rounded-xl border border-zinc-800 bg-zinc-900/40 px-4 py-3 font-mono text-xs text-zinc-400"
              >
                {s}
              </li>
            ))}
            <li className="rounded-xl border border-zinc-800 bg-zinc-900/40 px-4 py-3 font-mono text-xs text-zinc-400">
              build_reports/moneyball_aggregate_v1.json
            </li>
            <li className="rounded-xl border border-zinc-800 bg-zinc-900/40 px-4 py-3 font-mono text-xs text-zinc-400">
              build_reports/commodity_economy_v1.json
            </li>
          </ul>
          <p className="text-xs text-zinc-600">
            Refresh:{" "}
            <span className="font-mono">bin/mabel-catalog financial</span> or{" "}
            <span className="font-mono">bin/mabel-catalog commodity-economy --sync</span>
          </p>
        </Section>
      </div>
    </main>
  );
}
