import Link from "next/link";
import { Section } from "@/components/Section";
import { StatCard } from "@/components/StatCard";
import { fmtNum, getCommodityEconomy } from "@/lib/data";

export default function CommodityPage() {
  const ce = getCommodityEconomy();
  const pe = ce.physical_economy_totals;
  const cfsSectors = ce.layers.cfs_2022?.by_sector ?? [];
  const minerals = ce.layers.usgs_minerals?.top_commodities ?? [];

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <header className="mb-10 border-b border-zinc-800 pb-8">
        <Link href="/" className="text-xs text-zinc-500 hover:text-emerald-400">
          ← Dashboard
        </Link>
        <p className="mt-4 text-xs font-semibold uppercase tracking-[0.2em] text-amber-500">
          Physical economy
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Commodity Economy
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-zinc-400">
          {ce.what_this_is} As of {ce.as_of}. Not futures prices or investment advice.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="FAF5 freight"
          value={`${pe.faf5_billion_tons ?? "—"}B t`}
          sub="Modeled national flows 2024"
          tone="accent"
        />
        <StatCard
          label="CFS shipments"
          value={`${fmtNum(pe.cfs_million_tons, 0)}M t`}
          sub={`$${fmtNum(pe.cfs_billion_usd_shipment_value, 0)}B value`}
          tone="neutral"
        />
        <StatCard
          label="Crude imports"
          value={pe.crude_imports_kbbl_latest != null ? `${fmtNum(pe.crude_imports_kbbl_latest, 0)}` : "—"}
          sub="thousand barrels latest month"
          tone="up"
        />
        <StatCard
          label="USGS deposits"
          value={fmtNum(pe.usgs_deposit_sites, 0)}
          sub="Distinct mineral sites"
          tone="neutral"
        />
      </div>

      <div className="mt-10 space-y-10">
        <Section
          title="Unified commodity slate"
          description="Combined FAF5 tonnage share (55%) + Census CFS weight share (45%) by SCTG."
        >
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900 text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Commodity</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">FAF5 %</th>
                  <th className="px-4 py-3">CFS %</th>
                  <th className="px-4 py-3">CFS $B</th>
                  <th className="px-4 py-3">Mode</th>
                </tr>
              </thead>
              <tbody>
                {ce.unified_commodity_slate.map((row, i) => (
                  <tr
                    key={row.sctg}
                    className="border-b border-zinc-800/80 last:border-0"
                  >
                    <td className="px-4 py-3 text-zinc-500">{i + 1}</td>
                    <td className="px-4 py-3 font-medium text-white">{row.commodity}</td>
                    <td className="px-4 py-3 font-mono text-amber-300">
                      {row.economy_score.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 font-mono text-zinc-400">
                      {row.faf5_pct != null ? `${row.faf5_pct}%` : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono text-zinc-400">
                      {row.cfs_pct != null ? `${row.cfs_pct}%` : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono text-emerald-400">
                      {row.cfs_billion_usd != null ? row.cfs_billion_usd.toFixed(1) : "—"}
                    </td>
                    <td className="px-4 py-3 text-zinc-500">{row.primary_mode ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        <Section title="Crude import origins" description="EIA PET_IMPORTS monthly flows to Total U.S.">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {ce.energy_snapshot.crude_imports_by_origin.map((o) => (
              <div
                key={o.region}
                className="rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3"
              >
                <p className="text-sm text-zinc-300">{o.region}</p>
                <p className="font-mono text-lg text-white">
                  {o.thousand_barrels.toLocaleString()} kbbl
                </p>
              </div>
            ))}
          </div>
        </Section>

        <div className="grid gap-10 lg:grid-cols-2">
          <Section title="CFS by sector (2022)" description="Shipment value-weighted">
            <ul className="space-y-2 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4">
              {cfsSectors.slice(0, 8).map((s) => (
                <li key={s.sector} className="flex justify-between text-sm">
                  <span className="text-zinc-400">{s.label}</span>
                  <span className="font-mono text-emerald-400">${s.billion_usd.toFixed(0)}B</span>
                </li>
              ))}
            </ul>
          </Section>

          <Section title="USGS mineral inventory" description="Deposit sites by commodity">
            <ul className="space-y-2 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4">
              {minerals.slice(0, 8).map((m) => (
                <li key={m.commodity} className="flex justify-between text-sm">
                  <span className="text-zinc-400">{m.commodity}</span>
                  <span className="font-mono text-amber-300">
                    {m.deposit_sites.toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          </Section>
        </div>

        {ce.gaps.length > 0 && (
          <Section title="Data gaps" description="Honest missing-source register">
            <ul className="space-y-1 text-sm text-zinc-500">
              {ce.gaps.map((g) => (
                <li key={g} className="font-mono text-xs">
                  {g}
                </li>
              ))}
            </ul>
          </Section>
        )}
      </div>
    </main>
  );
}
