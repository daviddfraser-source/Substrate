"use client";

import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type JobStatus = "queued" | "running" | "done" | "failed";

interface AgentJob {
  key: string;
  task: string;
  agent: string;
  status: JobStatus;
  progress: number;
}

const seedJobs: AgentJob[] = [
  { key: "J-701", task: "Template route smoke", agent: "qa-bot", status: "running", progress: 55 },
  { key: "J-702", task: "WBS sync verification", agent: "ops-bot", status: "queued", progress: 0 },
  { key: "J-703", task: "Auth regression checks", agent: "sec-bot", status: "done", progress: 100 },
];

export default function AgentConsolePage() {
  const [jobs, setJobs] = useState(seedJobs);
  const [logs, setLogs] = useState<string[]>(["[info] agent console started"]);

  useEffect(() => {
    const id = window.setInterval(() => {
      setLogs((prev) => [`[${new Date().toLocaleTimeString()}] heartbeat: runtime healthy`, ...prev].slice(0, 30));
    }, 2500);
    return () => window.clearInterval(id);
  }, []);

  const stats = useMemo(() => ({
    total: jobs.length,
    running: jobs.filter((job) => job.status === "running").length,
    queued: jobs.filter((job) => job.status === "queued").length,
    done: jobs.filter((job) => job.status === "done").length,
  }), [jobs]);

  function runNext() {
    setJobs((prev) => {
      const idx = prev.findIndex((job) => job.status === "queued");
      if (idx < 0) return prev;
      return prev.map((job, i) => (i === idx ? { ...job, status: "running", progress: 10 } : job));
    });
    setLogs((prev) => ["[action] promoted queued job to running", ...prev].slice(0, 30));
  }

  function tickRunning() {
    setJobs((prev) => prev.map((job) => {
      if (job.status !== "running") return job;
      const next = Math.min(100, job.progress + 20);
      return { ...job, progress: next, status: next >= 100 ? "done" : "running" };
    }));
    setLogs((prev) => ["[action] advanced running jobs", ...prev].slice(0, 30));
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Agent Console Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Operations console starter using custom components, stats, and runtime log surfaces.</span>
      </div>

      <div className="flex gap-3">
        <Button variant="outline" onClick={runNext}>Run Next</Button>
        <Button variant="primary" onClick={tickRunning}>Advance Running</Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="flex flex-col items-center justify-center py-6">
          <div className="text-3xl font-bold text-[var(--text-primary)]">{stats.total}</div>
          <div className="text-sm text-[var(--text-secondary)] uppercase tracking-wide">Total</div>
        </Card>
        <Card className="flex flex-col items-center justify-center py-6">
          <div className="text-3xl font-bold text-[var(--warning-600)]">{stats.running}</div>
          <div className="text-sm text-[var(--text-secondary)] uppercase tracking-wide">Running</div>
        </Card>
        <Card className="flex flex-col items-center justify-center py-6">
          <div className="text-3xl font-bold text-[var(--primary-600)]">{stats.queued}</div>
          <div className="text-sm text-[var(--text-secondary)] uppercase tracking-wide">Queued</div>
        </Card>
        <Card className="flex flex-col items-center justify-center py-6">
          <div className="text-3xl font-bold text-[var(--success-600)]">{stats.done}</div>
          <div className="text-sm text-[var(--text-secondary)] uppercase tracking-wide">Done</div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-4">Jobs</h3>
          <div className="overflow-x-auto w-full border border-[var(--border-default)] rounded-md">
            <table className="w-full text-left text-sm text-[var(--text-primary)]">
              <thead className="bg-[var(--bg-secondary)] border-b border-[var(--border-default)] text-[var(--text-secondary)]">
                <tr>
                  <th className="px-4 py-3 font-medium">Task</th>
                  <th className="px-4 py-3 font-medium">Agent</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium w-32">Progress</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-default)]">
                {jobs.map((job) => (
                  <tr key={job.key} className="hover:bg-[var(--bg-inset)] transition-colors">
                    <td className="px-4 py-3 font-medium">{job.task}</td>
                    <td className="px-4 py-3">{job.agent}</td>
                    <td className="px-4 py-3">
                      <Badge variant={job.status === "done" ? "success" : job.status === "failed" ? "danger" : job.status === "running" ? "warning" : "info"}>
                        {job.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-[var(--bg-inset)] rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${job.status === "done" ? "bg-[var(--success-500)]" : job.status === "failed" ? "bg-[var(--danger-500)]" : "bg-[var(--primary-500)]"}`}
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                        <span className="text-xs text-[var(--text-secondary)] font-medium w-8 text-right">{job.progress}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <div className="lg:col-span-1 border border-[var(--border-default)] rounded flex flex-col overflow-hidden bg-[var(--bg-primary)] shadow-sm">
          <div className="bg-[var(--bg-secondary)] px-4 py-3 border-b border-[var(--border-default)] font-semibold text-[var(--text-primary)]">
            Runtime Log
          </div>
          <div className="p-4 flex flex-col gap-2 max-h-[420px] overflow-y-auto">
            {logs.map((item, index) => (
              <div key={`${item}-${index}`} className="font-mono text-xs bg-[var(--bg-inset)] text-[var(--text-primary)] px-2 py-1 rounded">
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
