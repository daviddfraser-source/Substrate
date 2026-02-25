"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { KpiCard } from "@/components/governance/KpiCard";
import "@svar-ui/react-gantt/all.css";

const Gantt = dynamic(() => import("@svar-ui/react-gantt").then((mod) => mod.Gantt), { ssr: false });

const seedTasks = [
  {
    id: "G-01",
    text: "Discovery and architecture",
    start: new Date(2026, 1, 24),
    end: new Date(2026, 1, 27),
    duration: 3,
    progress: 90,
    type: "task",
  },
  {
    id: "G-02",
    text: "Template library integration",
    start: new Date(2026, 1, 27),
    end: new Date(2026, 2, 3),
    duration: 4,
    progress: 45,
    type: "task",
  },
  {
    id: "G-03",
    text: "Playwright and QA hardening",
    start: new Date(2026, 2, 3),
    end: new Date(2026, 2, 6),
    duration: 3,
    progress: 20,
    type: "task",
  },
  {
    id: "G-04",
    text: "Release candidate",
    start: new Date(2026, 2, 6),
    end: new Date(2026, 2, 7),
    duration: 1,
    progress: 0,
    type: "milestone",
  },
];

const seedLinks = [
  { id: 1, source: "G-01", target: "G-02", type: "0" },
  { id: 2, source: "G-02", target: "G-03", type: "0" },
  { id: 3, source: "G-03", target: "G-04", type: "0" },
];

export default function GanttPage() {
  const [tasks, setTasks] = useState(seedTasks);
  const [links, setLinks] = useState(seedLinks);
  const [viewMode, setViewMode] = useState<"day" | "week" | "month">("week");

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Gantt Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">
          Powered by `@svar-ui/react-gantt` with enterprise grid layout, drag-to-reschedule, and dependencies.
        </span>
      </div>

      <div className="flex flex-wrap gap-4 mb-4">
        <div className="w-48">
          <KpiCard title="Total Tasks" value={tasks.length} accent="primary" />
        </div>
        <div className="w-48">
          <KpiCard title="Dependencies" value={links.length} accent="success" />
        </div>
      </div>

      <Card className="!p-0 bg-transparent border-0 overflow-hidden shadow-none">
        <div className="flex flex-col gap-4">
          <div className="flex gap-2">
            {(["day", "week", "month"] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${viewMode === mode
                    ? "bg-[var(--primary)] text-white"
                    : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-inset)] hover:text-[var(--text-primary)] border border-[var(--border-default)]"
                  }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>

          <Alert
            showIcon
            type="info"
            title="Interactive Gantt"
            description="Drag a bar edge to change dates, drag the whole bar to reschedule, or connect points to create dependencies."
          />

          <div className="border border-[var(--border-default)] rounded-[12px] bg-[var(--bg-primary)] overflow-hidden shadow-sm h-[500px]">
            <Gantt
              tasks={tasks}
              links={links}
              scales={[
                { unit: "month", step: 1, format: "MMMM yyyy" },
                { unit: viewMode, step: 1, format: viewMode === "day" ? "dd" : "ww" }
              ]}
              columns={[
                { id: "text", header: "Task name", width: 250 },
                { id: "start", header: "Start time", width: 100 },
                { id: "duration", header: "Duration", width: 80 }
              ]}
            />
          </div>
        </div>
      </Card>
    </div>
  );
}
