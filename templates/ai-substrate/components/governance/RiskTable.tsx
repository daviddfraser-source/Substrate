"use client";

interface RiskEntry {
  id: string;
  title: string;
  severity: "high" | "medium" | "low";
  status: string;
  owner?: string;
}

interface RiskTableProps {
  risks: RiskEntry[];
}

const severityColors = {
  high: { bg: "var(--danger-50)", text: "var(--danger-700)" },
  medium: { bg: "var(--warning-50)", text: "#92400e" },
  low: { bg: "var(--success-50)", text: "var(--success-700)" },
};

export function RiskTable({ risks }: RiskTableProps) {
  return (
    <div className="border border-[var(--border-default)] rounded-[var(--radius-xl)] overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-[var(--bg-secondary)] text-[var(--text-secondary)]">
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Risk</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Severity</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Status</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Owner</th>
          </tr>
        </thead>
        <tbody>
          {risks.map(risk => (
            <tr key={risk.id} className="border-t border-[var(--border-muted)] hover:bg-[var(--bg-inset)]">
              <td className="px-4 py-2.5 font-medium">{risk.title}</td>
              <td className="px-4 py-2.5">
                <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-semibold uppercase" style={{ background: severityColors[risk.severity].bg, color: severityColors[risk.severity].text }}>
                  {risk.severity}
                </span>
              </td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)]">{risk.status}</td>
              <td className="px-4 py-2.5 text-[var(--text-tertiary)]">{risk.owner || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {risks.length === 0 && <div className="text-center py-8 text-sm text-[var(--text-tertiary)]">No risks registered</div>}
    </div>
  );
}
