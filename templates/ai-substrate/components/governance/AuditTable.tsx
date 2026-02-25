"use client";
import { StatusBadge } from "./StatusBadge";

interface AuditEvent {
  packet_id: string;
  event: string;
  agent: string;
  timestamp: string;
  notes?: string;
}

interface AuditTableProps {
  events?: AuditEvent[];
  entries?: AuditEvent[];
}

export function AuditTable({ events, entries }: AuditTableProps) {
  const rows = events ?? entries ?? [];
  return (
    <div className="border border-[var(--border-default)] rounded-[var(--radius-xl)] overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-[var(--bg-secondary)] text-[var(--text-secondary)]">
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Packet</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Event</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Agent</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Time</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide">Notes</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((evt, i) => (
            <tr key={i} className="border-t border-[var(--border-muted)] hover:bg-[var(--bg-inset)]">
              <td className="px-4 py-2.5 font-mono text-[var(--text-link)]">{evt.packet_id}</td>
              <td className="px-4 py-2.5"><StatusBadge status={evt.event === "completed" ? "done" : evt.event === "started" ? "in_progress" : "pending"} /></td>
              <td className="px-4 py-2.5">{evt.agent}</td>
              <td className="px-4 py-2.5 text-[var(--text-tertiary)]">{new Date(evt.timestamp).toLocaleString()}</td>
              <td className="px-4 py-2.5 text-[var(--text-secondary)] max-w-[240px] truncate">{evt.notes || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <div className="text-center py-8 text-sm text-[var(--text-tertiary)]">No audit events</div>}
    </div>
  );
}
