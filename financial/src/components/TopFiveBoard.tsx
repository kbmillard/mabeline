import { TopFiveBar } from "./TopFiveBar";
import type { MoneyballPick, MarketReturnRow, PennyCandidate } from "@/lib/types";

type TopFiveBoardProps = {
  asOf: string;
  returns: MarketReturnRow[];
  moneyball: MoneyballPick[];
  penny: PennyCandidate[];
};

function maxOf(rows: { value: number }[]): number {
  return rows.reduce((m, r) => Math.max(m, r.value), 0);
}

export function TopFiveBoard({ asOf, returns, moneyball, penny }: TopFiveBoardProps) {
  const returnRows = returns.slice(0, 5).map((r) => ({
    key: r.ticker,
    label: r.ticker,
    sub: `${r.market} · ${r.name}`,
    value: r.ret_1y,
    display: `+${r.ret_1y.toFixed(0)}%`,
  }));

  const mbRows = moneyball.slice(0, 5).map((r) => ({
    key: r.ticker,
    label: r.ticker,
    sub: r.cent_zone ? "CENT · " + r.name : r.name,
    value: r.moneyball_score,
    display: String(Math.round(r.moneyball_score)),
  }));

  const pennyRows = penny.slice(0, 5).map((r) => ({
    key: r.ticker,
    label: r.ticker,
    sub: r.name,
    value: r.score,
    display: r.upside_pct != null ? `+${r.upside_pct.toFixed(0)}%` : String(r.score),
  }));

  const columns = [
    {
      title: "1y returns",
      caption: "Sane filter · start ≥ $1",
      rows: returnRows,
      max: maxOf(returnRows),
      tone: "emerald" as const,
    },
    {
      title: "Moneyball",
      caption: "Score · 1¢→$100 slate",
      rows: mbRows,
      max: maxOf(mbRows),
      tone: "amber" as const,
    },
    {
      title: "Penny forward",
      caption: "Analyst upside",
      rows: pennyRows,
      max: maxOf(pennyRows),
      tone: "sky" as const,
    },
  ];

  return (
    <section className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-5">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500">
            Last run · top 5
          </p>
          <h2 className="mt-1 text-lg font-semibold text-white">
            Three lenses from synced receipts
          </h2>
        </div>
        <p className="font-mono text-xs text-zinc-500">as of {asOf}</p>
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        {columns.map((col) => (
          <div key={col.title}>
            <h3 className="text-sm font-semibold text-zinc-200">{col.title}</h3>
            <p className="text-xs text-zinc-500">{col.caption}</p>
            <div className="mt-4 space-y-4">
              {col.rows.map((row, i) => (
                <TopFiveBar
                  key={row.key}
                  rank={i + 1}
                  label={row.label}
                  sub={row.sub}
                  value={row.value}
                  max={col.max}
                  display={row.display}
                  tone={col.tone}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
