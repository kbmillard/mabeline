type TopFiveBarProps = {
  rank: number;
  label: string;
  sub?: string;
  value: number;
  max: number;
  display: string;
  tone?: "amber" | "emerald" | "sky";
};

const fill: Record<NonNullable<TopFiveBarProps["tone"]>, string> = {
  amber: "bg-amber-400",
  emerald: "bg-emerald-400",
  sky: "bg-sky-400",
};

export function TopFiveBar({
  rank,
  label,
  sub,
  value,
  max,
  display,
  tone = "amber",
}: TopFiveBarProps) {
  const pct = max > 0 ? Math.max(4, (value / max) * 100) : 0;

  return (
    <div className="flex items-center gap-3">
      <span className="w-5 shrink-0 text-right font-mono text-xs text-zinc-600">
        {rank}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between gap-2">
          <span className="truncate font-mono text-sm font-semibold text-white">
            {label}
          </span>
          <span className="shrink-0 font-mono text-sm text-zinc-300">{display}</span>
        </div>
        {sub ? (
          <p className="truncate text-xs text-zinc-500">{sub}</p>
        ) : null}
        <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-zinc-800">
          <div
            className={`h-full rounded-full ${fill[tone]}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  );
}
