"use client";

interface KpiCardProps {
  title: string;
  value: number | string;
  trend?: { delta: number; direction: "up" | "down" | "steady" };
  accent?: "primary" | "success" | "warning" | "danger";
}

const accentColors = {
  primary: "var(--primary)",
  success: "var(--success)",
  warning: "var(--warning)",
  danger: "var(--danger)",
};

export function KpiCard({ title, value, trend, accent = "primary" }: KpiCardProps) {
  const trendColor = trend?.direction === "up" ? "var(--danger)" : trend?.direction === "down" ? "var(--success)" : "var(--text-tertiary)";
  const trendArrow = trend?.direction === "up" ? "↑" : trend?.direction === "down" ? "↓" : "→";
  return (
    <div className="relative bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-[var(--radius-xl)] p-4 overflow-hidden transition-shadow hover:shadow-[var(--shadow-sm)]">
      <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-[3px]" style={{ background: accentColors[accent] }} />
      <h4 className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide mb-1">{title}</h4>
      <div className="text-2xl font-bold">{value}</div>
      {trend && (
        <div className="text-xs mt-1" style={{ color: trendColor }}>
          {trendArrow} {trend.delta >= 0 ? "+" : ""}{trend.delta}
        </div>
      )}
    </div>
  );
}
