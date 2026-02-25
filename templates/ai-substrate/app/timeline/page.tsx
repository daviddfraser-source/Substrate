"use client";

import { useMemo, useState } from "react";
import dayjs from "dayjs";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Timeline, TimelineItem } from "@/components/ui/timeline";

type TimelineEvent = {
  id: string;
  ts: string;
  source: "execution" | "approval" | "risk" | "release";
  actor: string;
  summary: string;
  severity: "low" | "medium" | "high";
};

const events: TimelineEvent[] = [
  { id: "T-501", ts: "2026-02-25T08:05:00Z", source: "execution", actor: "codex", summary: "Packet tranche claimed", severity: "low" },
  { id: "T-502", ts: "2026-02-25T08:21:00Z", source: "approval", actor: "ops-lead", summary: "Template rollout approved", severity: "medium" },
  { id: "T-503", ts: "2026-02-25T08:42:00Z", source: "risk", actor: "security", summary: "Cookie origin mismatch found", severity: "high" },
  { id: "T-504", ts: "2026-02-25T09:03:00Z", source: "execution", actor: "codex", summary: "Auth host matching patched", severity: "medium" },
  { id: "T-505", ts: "2026-02-25T09:17:00Z", source: "release", actor: "platform", summary: "RC template package published", severity: "low" },
];

export default function TimelinePage() {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<"all" | TimelineEvent["source"]>("all");
  const [severity, setSeverity] = useState<"all" | TimelineEvent["severity"]>("all");

  const filtered = useMemo(() => {
    return events.filter((event) => {
      if (source !== "all" && event.source !== source) return false;
      if (severity !== "all" && event.severity !== severity) return false;
      if (query && !`${event.id} ${event.actor} ${event.summary}`.toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
  }, [query, source, severity]);

  const timelineItems: TimelineItem[] = filtered.map((event) => ({
    title: dayjs(event.ts).format("MMM D, HH:mm"),
    color: event.severity === "high" ? "red" : event.severity === "medium" ? "orange" : "blue",
    children: (
      <div className="flex flex-col gap-2">
        <div className="font-semibold text-sm">
          {event.id} {event.summary}
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="default">{event.source}</Badge>
          <Badge variant="default">{event.actor}</Badge>
          <Badge variant={event.severity === "high" ? "danger" : event.severity === "medium" ? "warning" : "success"}>
            {event.severity}
          </Badge>
        </div>
      </div>
    ),
  }));

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Timeline Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Custom timeline and filter controls for audit/event streams.</span>
      </div>

      <Card>
        <div className="flex flex-wrap items-center gap-4">
          <div className="w-[280px]">
            <Input
              placeholder="Search events"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="w-[180px]">
            <Select
              value={source}
              onChange={(e) => setSource(e.target.value as any)}
              options={[
                { value: "all", label: "All Sources" },
                { value: "execution", label: "Execution" },
                { value: "approval", label: "Approval" },
                { value: "risk", label: "Risk" },
                { value: "release", label: "Release" },
              ]}
            />
          </div>
          <div className="w-[180px]">
            <Select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as any)}
              options={[
                { value: "all", label: "All Severity" },
                { value: "low", label: "Low" },
                { value: "medium", label: "Medium" },
                { value: "high", label: "High" },
              ]}
            />
          </div>
          <Badge variant="info" className="ml-auto text-[14px] px-3 py-1">{filtered.length} events</Badge>
        </div>
      </Card>

      <Card className="min-h-[400px]">
        {timelineItems.length > 0 ? (
          <Timeline items={timelineItems} className="mt-4" />
        ) : (
          <div className="text-center py-12 text-[var(--text-tertiary)] text-sm">
            No events match your criteria.
          </div>
        )}
      </Card>
    </div>
  );
}
