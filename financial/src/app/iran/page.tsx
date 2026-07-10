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

type LeverEvent = {
  when: string;
  label: string;
  wti_usd?: number;
  price_effect?: string;
  source?: string;
};

export default function IranPage() {
  const eia = iranOil.eia_iran;
  const census = iranOil.census_iran;
  const truck = iranOil.truck_petroleum;
  const lever = (
    iranOil as typeof iranOil & {
      hormuz_lever?: {
        pattern: string;
        unit: string;
        note: string;
        events: LeverEvent[];
        world_us_crude_kbbl_recent?: { period: string; kbbl: number }[];
      };
    }
  ).hormuz_lever;

  const wtiPoints = (lever?.events ?? []).filter((e) => e.wti_usd != null);
  const maxWti = Math.max(...wtiPoints.map((e) => e.wti_usd!), 1);

  return (
    <main className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.28em] text-zinc-500">
        Mabeline · proof
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-zinc-50 sm:text-5xl">
        Iran · oil · truck
      </h1>
      <p className="mt-4 max-w-2xl text-sm leading-relaxed text-zinc-400">
        Hormuz is the price lever. Truck hauls and Iran→US barrels are separate
        sensors. Same page so the dramatizing pattern can&apos;t hide.
      </p>

      {lever ? (
        <section className="mt-10 rounded-2xl border border-zinc-700 bg-zinc-950 p-6 sm:p-8">
          <p className="text-xs uppercase tracking-[0.2em] text-amber-500">
            Hormuz lever · {lever.unit}
          </p>
          <p className="mt-2 font-mono text-sm text-zinc-300">{lever.pattern}</p>
          <p className="mt-3 max-w-2xl text-sm text-zinc-400">{lever.note}</p>

          <div className="mt-8 flex items-end gap-3 sm:gap-6">
            {wtiPoints.map((e) => {
              const h = Math.max(12, ((e.wti_usd ?? 0) / maxWti) * 140);
              return (
                <div key={e.when} className="flex flex-1 flex-col items-center gap-2">
                  <span className="font-mono text-sm text-zinc-100">
                    ${e.wti_usd?.toFixed(0)}
                  </span>
                  <div
                    className="w-full max-w-[4.5rem] rounded-t bg-amber-500/80"
                    style={{ height: h }}
                  />
                  <span className="text-center font-mono text-[10px] text-zinc-500">
                    {e.when}
                  </span>
                </div>
              );
            })}
          </div>

          <ul className="mt-8 space-y-4">
            {lever.events.map((e) => (
              <li
                key={e.when}
                className="border-b border-zinc-800 pb-3 text-sm last:border-0"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-mono text-zinc-500">{e.when}</span>
                  {e.wti_usd != null ? (
                    <span className="font-mono text-zinc-100">
                      WTI ${e.wti_usd}
                    </span>
                  ) : null}
                </div>
                <p className="mt-1 text-zinc-200">{e.label}</p>
                {e.price_effect ? (
                  <p className="mt-1 text-zinc-500">{e.price_effect}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

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
            {eia.last_month ?? "—"} · last print
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
        <p className="mt-2 font-mono text-xl text-amber-400">{iranOil.join}</p>
        <p className="mt-3 text-sm text-zinc-300">{iranOil.join_note}</p>
        <p className="mt-4 font-mono text-xs text-zinc-600">
          as_of {iranOil.as_of}
        </p>
      </section>

      {lever?.world_us_crude_kbbl_recent?.length ? (
        <section className="mt-10">
          <h2 className="text-sm font-medium uppercase tracking-wider text-zinc-400">
            World → US crude (EIA kbbl) · not Iran
          </h2>
          <ul className="mt-4 grid gap-2 sm:grid-cols-2">
            {lever.world_us_crude_kbbl_recent.map((row) => (
              <li
                key={row.period}
                className="flex justify-between border-b border-zinc-800 py-2 font-mono text-sm"
              >
                <span className="text-zinc-500">{row.period}</span>
                <span className="text-zinc-100">
                  {Math.round(row.kbbl).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

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
        </div>
      </section>

      <div className="mt-12 flex flex-wrap gap-6 text-sm">
        <Link
          href="/thg"
          className="text-zinc-300 underline-offset-4 hover:underline"
        >
          Corridor map
        </Link>
        <Link href="/" className="text-zinc-500 underline-offset-4 hover:underline">
          Home
        </Link>
      </div>
    </main>
  );
}
