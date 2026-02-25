"use client";

import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

type PromptStatus = "draft" | "active" | "archived";

interface PromptVersion {
  id: string;
  title: string;
  status: PromptStatus;
  updated: string;
  body: string;
}

const seededVersions: PromptVersion[] = [
  { id: "PV-41", title: "Enterprise governance assistant", status: "active", updated: "2026-02-25", body: "You are a governed operations assistant. Always cite artifacts." },
  { id: "PV-42", title: "Template rollout reviewer", status: "draft", updated: "2026-02-25", body: "Assess template readiness and identify blocking risks." },
  { id: "PV-39", title: "Legacy narrative mode", status: "archived", updated: "2026-02-18", body: "Generate free-form summary." },
];

export default function PromptLabPage() {
  const [versions, setVersions] = useState(seededVersions);
  const [selectedId, setSelectedId] = useState("PV-42");
  const [testInput, setTestInput] = useState("Generate implementation packets for template hardening.");
  const [result, setResult] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const selected = useMemo(() => versions.find((item) => item.id === selectedId) || versions[0], [selectedId, versions]);

  function updateSelectedBody(value: string) {
    setVersions((prev) => prev.map((item) => (item.id === selected.id ? { ...item, body: value, updated: new Date().toISOString().slice(0, 10) } : item)));
  }

  function setStatus(status: PromptStatus) {
    setVersions((prev) => prev.map((item) => {
      if (item.id === selected.id) return { ...item, status };
      if (status === "active" && item.status === "active") return { ...item, status: "draft" };
      return item;
    }));
  }

  async function runTest() {
    setIsRunning(true);
    setResult("Running test...");
    await new Promise((resolve) => setTimeout(resolve, 450));
    setResult(`Test result for ${selected.id}: generated structured output for \"${testInput}\" with compliance tags and citations.`);
    setIsRunning(false);
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Prompt Lab Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Versioned prompt management with edit, evaluate, and activate flow using custom components.</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 border border-[var(--border-default)] rounded p-4 bg-[var(--bg-primary)] shadow-sm">
          <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-3">Versions</h3>
          <div className="flex flex-col gap-3">
            {versions.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedId(item.id)}
                className={`flex flex-col border rounded p-3 transition-colors cursor-pointer ${selectedId === item.id
                    ? "border-[var(--primary)] bg-[var(--primary-50)] shadow-sm"
                    : "border-[var(--border-default)] hover:bg-[var(--bg-inset)] hover:border-[var(--border-strong)]"
                  }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-semibold text-sm text-[var(--text-primary)]">{item.id}</span>
                  <Badge variant={item.status === "active" ? "success" : item.status === "draft" ? "info" : "default"}>{item.status}</Badge>
                </div>
                <div className="text-sm text-[var(--text-primary)] font-medium mb-1">{item.title}</div>
                <div className="text-xs text-[var(--text-tertiary)]">Updated {item.updated}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 border border-[var(--border-default)] rounded p-4 bg-[var(--bg-primary)] shadow-sm">
          <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-4">Edit {selected.id}</h3>

          <div className="flex flex-col gap-6">
            <div className="flex bg-[var(--bg-inset)] rounded p-1 w-fit border border-[var(--border-default)]">
              {(["draft", "active", "archived"] as PromptStatus[]).map((status) => (
                <button
                  key={status}
                  onClick={() => setStatus(status)}
                  className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${selected.status === status
                      ? "bg-[var(--bg-primary)] shadow-sm text-[var(--text-primary)] border border-black/5"
                      : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-sm font-semibold text-[var(--text-secondary)]">Prompt Body</label>
              <textarea
                rows={8}
                className="w-full px-3 py-2 rounded-md border border-[var(--border-strong)] bg-[var(--bg-primary)] text-[var(--text-primary)] focus:border-[var(--primary)] outline-none transition-colors resize-y"
                value={selected.body}
                onChange={(event) => updateSelectedBody(event.target.value)}
              />
            </div>

            <Input
              label="Test Input"
              value={testInput}
              onChange={(event) => setTestInput(event.target.value)}
            />

            <div className="flex flex-wrap gap-3">
              <Button variant="primary" loading={isRunning} onClick={() => void runTest()}>Run Test</Button>
              <Button variant="outline" onClick={() => setStatus("active")}>Activate</Button>
              <Button variant="danger" onClick={() => setStatus("archived")}>Archive</Button>
            </div>

            <div className="border border-[var(--border-default)] rounded flex flex-col overflow-hidden">
              <div className="bg-[var(--bg-secondary)] px-3 py-2 border-b border-[var(--border-default)] text-sm font-semibold text-[var(--text-secondary)]">
                Test Output
              </div>
              <div className={`p-4 text-sm font-mono ${!result ? "text-[var(--text-tertiary)] italic" : "text-[var(--text-primary)]"}`}>
                {result || "No test run yet."}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
