import Link from "next/link";
import iranOil from "@/data/thg_iran_oil_v1.json";

function fmtPct(n: number | null | undefined) {
  if (n == null || Number.isNaN(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

function fmtUsd(n: number | null | undefined) {
  if (n == null) return "—";
  return `$${n.toLocaleString()}`;
}

export default function IranPage() {
  const eia = iranOil.eia_iran;
  const census = iranOil.census_iran;
  const truck = iranOil.truck_petroleum;
  const join = iranOil.join;
  const joinTone =
    join === "aligned"
      ? "text-emerald-400"
      : join === "diverge" || join === "no_iran_eia_in_window"
        ? "text-amber-400"
        : "text-zinc-400";

  return (
    <main className="relative min-h-full overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_90%_60%_at_70%_-10%,#3f1d0f_0%,transparent_55%),radial-gradient(ellipse_50%_40%_at_10%_80%,#1e3a2f_0%,transparent_50%)]"
      />
      <div className="relative mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-amber-500/90">
          Mabeline
        </p>
        <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-zinc-50 sm:text-5xl sm:leading-[1.1]">
          Iran · oil · American roads
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-zinc-400">
          Truck is the sensor. Commodity is the signal. Origin pressure tags
          geopolitics onto the same spine — without pretending the headlines
          caused the haul.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
            <p className="text-xs uppercase tracking-wider text-zinc-500">
              EIA Iran → US crude
            </p>
            <p className="mt-2 text-3xl font-semibold text-zinc-50">
              {eia.last_kbbl?.toLocaleString() ?? "—"}
              <span className="ml-2 text-sm font-normal text-zinc-500">kbbl</span>
            </p>
            <p className="mt-1 text-sm text-zinc-400">
              Last print {eia.last_month ?? "—"} · Houston path
            </p>
          </div>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
            <p className="text-xs uppercase tracking-wider text-zinc-500">
              Census Iran goods
            </p>
            <p className="mt-2 text-3xl font-semibold text-zinc-50">
              {fmtUsd(census.con_val_mo)}
            </p>
            <p className="mt-1 text-sm text-zinc-400">
              {census.month ?? "—"} · vessel crude weight{" "}
              {census.ves_wgt_mo ?? 0}
            </p>
          </div>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
            <p className="text-xs uppercase tracking-wider text-zinc-500">
              US truck petroleum
            </p>
            <p className="mt-2 text-3xl font-semibold text-emerald-400">
              {fmtPct(truck.truck_observation_delta_pct)}
            </p>
            <p className="mt-1 text-sm text-zinc-400">
              Snapshot {truck.snapshot_month ?? "—"} · SCTG 17 hauls
            </p>
          </div>
        </div>

        <section className="mt-10 rounded-2xl border border-amber-500/30 bg-amber-500/5 p-6 sm:p-8">
          <p className="text-xs uppercase tracking-[0.2em] text-amber-500/80">
            Join verdict
          </p>
          <p className={`mt-3 text-2xl font-semibold sm:text-3xl ${joinTone}`}>
            {join.replaceAll("_", " ")}
          </p>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-zinc-300">
            {iranOil.join_note}
          </p>
          <p className="mt-4 font-mono text-xs text-zinc-500">
            as_of {iranOil.as_of} · {iranOil.thesis}
          </p>
        </section>

        <section className="mt-12 grid gap-8 lg:grid-cols-2">
          <div>
            <h2 className="text-lg font-medium text-zinc-100">
              EIA Iran crude months
            </h2>
            <ul className="mt-4 space-y-2">
              {[...eia.monthly].reverse().map((row) => (
                <li
                  key={row.period}
                  className="flex justify-between border-b border-zinc-800/80 py-2 text-sm"
                >
                  <span className="font-mono text-zinc-400">{row.period}</span>
                  <span className="text-zinc-100">
                    {row.kbbl.toLocaleString()} kbbl
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-lg font-medium text-zinc-100">
              Census Iran HS (top)
            </h2>
            <ul className="mt-4 space-y-2">
              {(census.top_hs ?? []).slice(0, 8).map((row) => (
                <li
                  key={`${row.hs}-${row.month}`}
                  className="flex justify-between gap-4 border-b border-zinc-800/80 py-2 text-sm"
                >
                  <span className="font-mono text-zinc-400">{row.hs}</span>
                  <span className="text-zinc-100">{fmtUsd(row.con_val)}</span>
                </li>
              ))}
              {(census.top_hs ?? []).length === 0 ? (
                <li className="text-sm text-zinc-500">No positive-value HS rows</li>
              ) : null}
            </ul>
            <p className="mt-4 text-xs text-zinc-500">{census.note}</p>
          </div>
        </section>

        <div className="mt-12 flex flex-wrap gap-4 text-sm">
          <Link
            href="/thg"
            className="text-amber-400 underline-offset-4 hover:underline"
          >
            Petroleum corridor map →
          </Link>
          <Link
            href="/"
            className="text-zinc-500 underline-offset-4 hover:underline"
          >
            Home
          </Link>
        </div>
      </div>
    </main>
  );
}
