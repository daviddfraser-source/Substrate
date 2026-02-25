"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";

type RiskLevel = "low" | "medium" | "high";
type ApprovalStatus = "pending" | "approved" | "rejected";

interface ApprovalItem {
  key: string;
  title: string;
  owner: string;
  risk: RiskLevel;
  status: ApprovalStatus;
  diffSummary: string;
}

const seedApprovals: ApprovalItem[] = [
  { key: "A-201", title: "Promote template RC", owner: "release", risk: "medium", status: "pending", diffSummary: "+18 components, -4 legacy widgets" },
  { key: "A-202", title: "Enable terminal dev mode", owner: "platform", risk: "high", status: "pending", diffSummary: "Policy update on shell passthrough route" },
  { key: "A-203", title: "Archive old docs export", owner: "ops", risk: "low", status: "approved", diffSummary: "Read-only archival retention" },
];

export default function ApprovalsPage() {
  const [rows, setRows] = useState(seedApprovals);
  const [selected, setSelected] = useState<ApprovalItem | null>(null);
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  function decide(status: Extract<ApprovalStatus, "approved" | "rejected">, noteText: string) {
    if (!selected) return;
    setRows((prev) => prev.map((item) => (item.key === selected.key ? { ...item, status } : item)));
    setSelected(null);
    setNote("");
    setMsg({ type: "success", text: `${status.toUpperCase()}: ${noteText || "No note provided"}` });
    setTimeout(() => setMsg(null), 3000);
  }

  const handleReviewSubmit = (e: React.FormEvent, status: "approved" | "rejected") => {
    e.preventDefault();
    if (!note) {
      setMsg({ type: "error", text: "Note is required" });
      setTimeout(() => setMsg(null), 3000);
      return;
    }
    decide(status, note);
  };

  return (
    <div className="p-6 space-y-4">
      {msg && (
        <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-top-4 fade-in">
          <Alert type={msg.type} title={msg.text} />
        </div>
      )}

      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Approvals Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Enterprise review queue with table + drawer + decision workflow using custom components.</span>
      </div>

      <Card>
        <div className="overflow-x-auto w-full border border-[var(--border-default)] rounded-md">
          <table className="w-full text-left text-sm text-[var(--text-primary)]">
            <thead className="bg-[var(--bg-secondary)] border-b border-[var(--border-default)] text-[var(--text-secondary)]">
              <tr>
                <th className="px-4 py-3 font-medium">Request</th>
                <th className="px-4 py-3 font-medium">Owner</th>
                <th className="px-4 py-3 font-medium">Risk</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium cursor-pointer">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-default)]">
              {rows.map((record) => (
                <tr key={record.key} className="hover:bg-[var(--bg-inset)] transition-colors">
                  <td className="px-4 py-3">{record.title}</td>
                  <td className="px-4 py-3">{record.owner}</td>
                  <td className="px-4 py-3">
                    <Badge variant={record.risk === "high" ? "danger" : record.risk === "medium" ? "warning" : "success"}>
                      {record.risk}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={record.status === "approved" ? "success" : record.status === "rejected" ? "danger" : "info"}>
                      {record.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Button variant="outline" size="sm" onClick={() => { setSelected(record); setNote(""); }}>Review</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Drawer Overlay */}
      {selected && (
        <div className="fixed inset-0 z-40 flex justify-end bg-black/40 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-md bg-[var(--bg-primary)] h-full shadow-2xl border-l border-[var(--border-default)] flex flex-col animate-in slide-in-from-right">
            <div className="flex items-center justify-between p-4 border-b border-[var(--border-default)]">
              <h3 className="font-semibold text-lg text-[var(--text-primary)]">Review {selected.key}</h3>
              <button
                onClick={() => setSelected(null)}
                className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-xl font-bold p-1 leading-none"
              >&times;</button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-6">
              <div className="border border-[var(--border-default)] rounded divide-y divide-[var(--border-default)] text-sm shadow-sm bg-[var(--bg-secondary)]">
                <div className="flex px-3 py-2">
                  <div className="w-24 text-[var(--text-secondary)] font-medium">Title</div>
                  <div className="flex-1 text-[var(--text-primary)] font-semibold">{selected.title}</div>
                </div>
                <div className="flex px-3 py-2">
                  <div className="w-24 text-[var(--text-secondary)] font-medium">Owner</div>
                  <div className="flex-1 text-[var(--text-primary)]">{selected.owner}</div>
                </div>
                <div className="flex px-3 py-2">
                  <div className="w-24 text-[var(--text-secondary)] font-medium">Risk</div>
                  <div className="flex-1 text-[var(--text-primary)] uppercase font-semibold">{selected.risk}</div>
                </div>
                <div className="flex px-3 py-2">
                  <div className="w-24 text-[var(--text-secondary)] font-medium">Diff</div>
                  <div className="flex-1 text-[var(--text-primary)]">{selected.diffSummary}</div>
                </div>
              </div>

              <form className="flex flex-col gap-4 flex-1">
                <Input
                  label="Decision note"
                  placeholder="Enter review notes..."
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />

                <div className="flex gap-3 mt-auto pt-4 border-t border-[var(--border-default)]">
                  <Button
                    type="button"
                    variant="danger"
                    className="flex-1"
                    onClick={(e) => handleReviewSubmit(e, "rejected")}
                  >Reject</Button>
                  <Button
                    type="button"
                    variant="primary"
                    className="flex-1"
                    onClick={(e) => handleReviewSubmit(e, "approved")}
                  >Approve</Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
