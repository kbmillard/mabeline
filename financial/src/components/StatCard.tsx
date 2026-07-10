type StatCardProps = {
  label: string;
  value: string;
  sub?: string;
  tone?: "neutral" | "up" | "down" | "accent";
};

const toneClass: Record<NonNullable<StatCardProps["tone"]>, string> = {
  neutral: "text-zinc-100",
  up: "text-emerald-400",
  down: "text-rose-400",
  accent: "text-amber-300",
};

export function StatCard({ label, value, sub, tone = "neutral" }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5 shadow-lg shadow-black/20">
      <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
        {label}
      </p>
      <p className={`mt-2 font-mono text-3xl font-semibold ${toneClass[tone]}`}>
        {value}
      </p>
      {sub ? <p className="mt-2 text-sm text-zinc-400">{sub}</p> : null}
    </div>
  );
}
