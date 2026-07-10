"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import routeDemo from "@/data/thg_pet_route_demo_v1.json";
import thgDemo from "@/data/thg_demo_payload_v1.json";

type StateRow = {
  state: string;
  prior: number;
  current: number;
  delta_abs: number;
  delta_pct: number;
  lon: number;
  lat: number;
};

type Commodity = {
  sctg2: string;
  name: string;
  prior: number;
  weight: number;
  delta: number;
  score: number;
};

const LON0 = -125;
const LON1 = -66;
const LAT0 = 24;
const LAT1 = 50;

function project(lon: number, lat: number, w: number, h: number) {
  const x = ((lon - LON0) / (LON1 - LON0)) * w;
  const y = ((LAT1 - lat) / (LAT1 - LAT0)) * h;
  return { x, y };
}

function fmtPct(n: number) {
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

export default function ThgPage() {
  const states = routeDemo.states as StateRow[];
  const commodities = thgDemo.commodities as Commodity[];
  const [sctg, setSctg] = useState("17");
  const [hover, setHover] = useState<string | null>(null);

  const selected = useMemo(
    () => commodities.find((c) => c.sctg2 === sctg) ?? commodities[0],
    [commodities, sctg],
  );

  const topStates = useMemo(
    () => [...states].sort((a, b) => b.delta_abs - a.delta_abs).slice(0, 12),
    [states],
  );

  const w = 920;
  const h = 520;
  const maxAbs = Math.max(...states.map((s) => Math.abs(s.delta_abs)), 1);

  const pathD = useMemo(() => {
    const ordered = [...topStates].sort((a, b) => a.lon - b.lon);
    return ordered
      .map((s, i) => {
        const { x, y } = project(s.lon, s.lat, w, h);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  }, [topStates]);

  const corridors =
    (thgDemo.corridors as Record<
      string,
      { state: string; weight: number; delta: number; score: number }[]
    >)[sctg] ?? [];
  const shippers =
    (thgDemo.shippers as Record<
      string,
      { name: string; weight: number; carriers?: number }[]
    >)[sctg] ?? [];

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
            Mabeline · Temporal haul graph
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
            Where the +55% comes from
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--muted)]">
            Petroleum (SCTG 17) inspection haul weight rose from{" "}
            <span className="text-foreground">{routeDemo.national_prior}</span> to{" "}
            <span className="text-foreground">{routeDemo.national_current}</span>{" "}
            between {routeDemo.month_prior} and {routeDemo.month_current}. Line
            connects top absolute state contributors — no map API key required.
          </p>
        </div>
        <Link
          href="/"
          className="text-sm text-[var(--muted)] underline-offset-4 hover:text-foreground hover:underline"
        >
          ← Financial board
        </Link>
      </div>

      <section className="mb-10 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
          <p className="text-xs text-[var(--muted)]">National delta</p>
          <p className="mt-1 text-2xl font-semibold text-[var(--up)]">
            {fmtPct(routeDemo.national_delta_pct)}
          </p>
          <p className="mt-1 font-mono text-xs text-[var(--muted)]">
            {routeDemo.math}
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
          <p className="text-xs text-[var(--muted)]">Top contributor</p>
          <p className="mt-1 text-2xl font-semibold">
            {topStates[0]?.state}{" "}
            <span className="text-[var(--up)]">
              +{topStates[0]?.delta_abs.toFixed(0)}
            </span>
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            Absolute haul-weight change
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
          <p className="text-xs text-[var(--muted)]">Vintage</p>
          <p className="mt-1 text-2xl font-semibold">
            {routeDemo.month_prior} → {routeDemo.month_current}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            FMCSA observed_haul edges · THG
          </p>
        </div>
      </section>

      <section className="mb-12 overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)]">
        <div className="border-b border-[var(--border)] px-4 py-3 text-sm text-[var(--muted)]">
          Corridor sketch · state centroids · hover a node
          {hover ? (
            <span className="ml-2 text-foreground">· {hover}</span>
          ) : null}
        </div>
        <div className="overflow-x-auto p-4">
          <svg
            viewBox={`0 0 ${w} ${h}`}
            className="mx-auto h-auto w-full max-w-4xl"
            role="img"
            aria-label="Petroleum haul weight change by state"
          >
            <rect width={w} height={h} fill="#0c0c0e" rx="8" />
            <path
              d={pathD}
              fill="none"
              stroke="#fbbf24"
              strokeWidth="2.5"
              strokeOpacity="0.85"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {states.map((s) => {
              const { x, y } = project(s.lon, s.lat, w, h);
              const r = 4 + (Math.abs(s.delta_abs) / maxAbs) * 14;
              const up = s.delta_abs >= 0;
              return (
                <g
                  key={s.state}
                  onMouseEnter={() =>
                    setHover(
                      `${s.state}: ${s.prior} → ${s.current} (${fmtPct(s.delta_pct)}, Δ${s.delta_abs >= 0 ? "+" : ""}${s.delta_abs.toFixed(0)})`,
                    )
                  }
                  onMouseLeave={() => setHover(null)}
                  className="cursor-pointer"
                >
                  <circle
                    cx={x}
                    cy={y}
                    r={r}
                    fill={up ? "#34d399" : "#fb7185"}
                    fillOpacity={0.85}
                    stroke="#fafafa"
                    strokeWidth={hover?.startsWith(s.state) ? 2 : 0.5}
                  />
                  <text
                    x={x}
                    y={y - r - 4}
                    textAnchor="middle"
                    fill="#a1a1aa"
                    fontSize="10"
                    fontFamily="ui-monospace, monospace"
                  >
                    {s.state}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
        <div className="grid gap-2 border-t border-[var(--border)] p-4 sm:grid-cols-2 lg:grid-cols-3">
          {topStates.map((s) => (
            <div
              key={s.state}
              className="flex items-center justify-between rounded-lg bg-black/30 px-3 py-2 text-sm"
            >
              <span className="font-mono">{s.state}</span>
              <span className="text-[var(--muted)]">
                {s.prior.toFixed(0)} → {s.current.toFixed(0)}
              </span>
              <span className={s.delta_abs >= 0 ? "text-[var(--up)]" : "text-[var(--down)]"}>
                {s.delta_abs >= 0 ? "+" : ""}
                {s.delta_abs.toFixed(0)}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold">Commodity explorer</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Same month pair · pick an SCTG to see corridors and shippers from the
          demo payload.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {commodities.slice(0, 16).map((c) => (
            <button
              key={c.sctg2}
              type="button"
              onClick={() => setSctg(c.sctg2)}
              className={`rounded-lg border px-3 py-1.5 text-xs transition ${
                sctg === c.sctg2
                  ? "border-[var(--accent)] bg-[var(--accent)]/10 text-foreground"
                  : "border-[var(--border)] text-[var(--muted)] hover:border-[var(--muted)]"
              }`}
            >
              {c.sctg2} {c.name.split(" ")[0]}{" "}
              <span
                className={
                  c.delta >= 0 ? "text-[var(--up)]" : "text-[var(--down)]"
                }
              >
                {fmtPct(c.delta)}
              </span>
            </button>
          ))}
        </div>
        {selected ? (
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <p className="text-sm font-medium">
                {selected.sctg2} · {selected.name}
              </p>
              <p className="mt-2 text-2xl font-semibold">
                <span
                  className={
                    selected.delta >= 0
                      ? "text-[var(--up)]"
                      : "text-[var(--down)]"
                  }
                >
                  {fmtPct(selected.delta)}
                </span>
              </p>
              <p className="mt-1 text-xs text-[var(--muted)]">
                {selected.prior.toFixed(0)} → {selected.weight.toFixed(0)} haul
                weight
              </p>
              <ul className="mt-4 space-y-2 text-sm">
                {corridors.map((row) => (
                  <li
                    key={row.state}
                    className="flex justify-between border-b border-[var(--border)]/60 py-1"
                  >
                    <span className="font-mono text-[var(--muted)]">
                      {row.state}
                    </span>
                    <span className="text-[var(--muted)]">
                      {fmtPct(row.delta)}
                    </span>
                    <span>{row.weight.toFixed(0)}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <p className="text-sm font-medium">Top shippers (inspection names)</p>
              <ul className="mt-4 space-y-2 text-sm">
                {shippers.map((row) => (
                  <li
                    key={row.name}
                    className="flex justify-between gap-4 border-b border-[var(--border)]/60 py-1"
                  >
                    <span className="truncate text-[var(--muted)]">
                      {row.name}
                    </span>
                    <span className="shrink-0">{row.weight.toFixed(0)}</span>
                  </li>
                ))}
                {shippers.length === 0 ? (
                  <li className="text-[var(--muted)]">No shippers in demo slice</li>
                ) : null}
              </ul>
            </div>
          </div>
        ) : null}
      </section>

      <p className="text-xs text-[var(--muted)]">
        Demo JSON only — full THG lives in{" "}
        <code className="font-mono">warehouse/th_graph_v1/</code> (not deployed).
        Truck = sensor, commodity = signal.
      </p>
    </main>
  );
}
