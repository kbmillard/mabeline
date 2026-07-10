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

  return (
    <main className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.28em] text-zinc-500">
        Mabeline · proof
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-zinc-50 sm:text-5xl">
        Iran · oil · truck
      </h1>
      <p className="mt-4 max-w-2xl text-sm leading-relaxed text-zinc-400">
        Three sensors on one page. Numbers from on-disk EIA, Census IMDB, and
        FMCSA haul edges — not a news take.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
          <p className="text-xs uppercase tracking-wider text-zinc-500">
            EIA Iran → US crude
          </p>
          <p className="mt-2 text-3xl font-semibold text-zinc-50">
            {eia.last_kbbl?.toLocaleString() ?? "—"}
            <span className="ml-2 text-sm font-normal text-zinc-500">kbbl</span>
          </p>
          <p className="mt-1 font-mono text-sm text-zinc-400">
            {eia.last_month ?? "—"} · {eia.series}
          </p>
        </div>
        <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
          <p className="text-xs uppercase tracking-wider text-zinc-500">
            Census Iran (5070)
          </p>
          <p className="mt-2 text-3xl font-semibold text-zinc-50">
            {fmtUsd(census.con_val_mo)}
          </p>
          <p className="mt-1 font-mono text-sm text-zinc-400">
            {census.month ?? "—"} · vessel_wgt {census.ves_wgt_mo ?? 0}
          </p>
        </div>
        <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
          <p className="text-xs uppercase tracking-wider text-zinc-500">
            Truck petroleum SCTG 17
          </p>
          <p className="mt-2 text-3xl font-semibold text-emerald-400">
            {fmtPct(truck.truck_observation_delta_pct)}
          </p>
          <p className="mt-1 font-mono text-sm text-zinc-400">
            {truck.snapshot_month ?? "—"} · {truck.prior_weight} →{" "}
            {truck.truck_weight}
          </p>
        </div>
      </div>

      <section className="mt-8 rounded-2xl border border-zinc-700 bg-zinc-900/60 p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Join</p>
        <p className="mt-2 font-mono text-xl text-amber-400">
          {iranOil.join}
        </p>
        <p className="mt-3 text-sm text-zinc-300">{iranOil.join_note}</p>
        <p className="mt-4 font-mono text-xs text-zinc-600">
          as_of {iranOil.as_of}
        </p>
      </section>

      <section className="mt-12 grid gap-10 lg:grid-cols-2">
        <div>
          <h2 className="text-sm font-medium uppercase tracking-wider text-zinc-400">
            EIA Iran monthly (kbbl)
          </h2>
          <ul className="mt-4 space-y-2">
            {[...eia.monthly].reverse().map((row) => (
              <li
                key={row.period}
                className="flex justify-between border-b border-zinc-800 py-2 font-mono text-sm"
              >
                <span className="text-zinc-500">{row.period}</span>
                <span className="text-zinc-100">{row.kbbl.toLocaleString()}</span>
              </li>
            ))}
          </ul>
          <p className="mt-3 break-all font-mono text-[11px] text-zinc-600">
            {eia.source_path}
          </p>
        </div>
        <div>
          <h2 className="text-sm font-medium uppercase tracking-wider text-zinc-400">
            Census Iran HS
          </h2>
          <ul className="mt-4 space-y-2">
            {(census.top_hs ?? []).map((row) => (
              <li
                key={`${row.hs}-${row.month}`}
                className="flex justify-between gap-4 border-b border-zinc-800 py-2 font-mono text-sm"
              >
                <span className="text-zinc-500">{row.hs}</span>
                <span className="text-zinc-100">{fmtUsd(row.con_val)}</span>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-zinc-500">{census.note}</p>
          <p className="mt-2 break-all font-mono text-[11px] text-zinc-600">
            {census.source_path}
          </p>
        </div>
      </section>

      <div className="mt-12 flex flex-wrap gap-6 text-sm">
        <Link href="/thg" className="text-zinc-300 underline-offset-4 hover:underline">
          Corridor map
        </Link>
        <Link href="/" className="text-zinc-500 underline-offset-4 hover:underline">
          Home
        </Link>
      </div>
    </main>
  );
}
