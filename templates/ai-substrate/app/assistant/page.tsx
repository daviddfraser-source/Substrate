"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";

const seedPrompt = "Summarize rollout risk for template pages and recommend mitigations.";

export default function AssistantPage() {
  const [prompt, setPrompt] = useState(seedPrompt);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [citations, setCitations] = useState<Array<{ source: string; section: string }>>([]);

  async function runAssistant(e?: React.FormEvent) {
    if (e) e.preventDefault();
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 700));
    setAnswer(
      [
        "## Executive Summary",
        "",
        "- UI consistency risk remains if route wrappers diverge.",
        "- Auth/session drift causes false-negative data fetch failures.",
        "- Template pages need stronger component reuse boundaries.",
        "",
        "## Recommended Actions",
        "",
        "1. Use shared route guards and API client wrappers.",
        "2. Add template smoke tests to CI for all route surfaces.",
        "3. Standardize on enterprise UI library components.",
      ].join("\n"),
    );
    setCitations([
      { source: "docs/codex-migration/template-pages-functionalization-plan.md", section: "Library selections" },
      { source: "templates/ai-substrate/app/layout.tsx", section: "Navigation + route grouping" },
      { source: "templates/ai-substrate/app/dashboard/page.tsx", section: "Dashboard fetch handling" },
    ]);
    setLoading(false);
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">RAG Assistant Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Custom form + markdown rendering + citation drawer pattern.</span>
      </div>

      <Card>
        <form onSubmit={runAssistant} className="flex flex-col gap-4">
          <Input
            label="Prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />
          <div className="flex items-center gap-2">
            <Button type="submit" variant="primary" loading={loading}>Run Assistant</Button>
            <Badge variant="info">Scoped retrieval</Badge>
            <Badge variant="success">Traceable output</Badge>
          </div>
        </form>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <Card>
            <h3 className="text-lg font-semibold mb-3">Answer</h3>
            {answer ? (
              <div className="prose prose-sm max-w-none text-[var(--text-primary)]">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            ) : (
              <Alert type="info" showIcon title="Run the assistant to generate a response." />
            )}
          </Card>
        </div>
        <div className="lg:col-span-1">
          <Card>
            <h3 className="text-lg font-semibold mb-3">Citations</h3>
            <div className="flex flex-col gap-3">
              {citations.length === 0 ? (
                <span className="text-[var(--text-secondary)] text-sm">No citations yet</span>
              ) : (
                citations.map((item) => (
                  <div key={`${item.source}-${item.section}`} className="border border-[var(--border-default)] rounded p-2 text-sm bg-[var(--bg-secondary)]">
                    <div className="font-semibold text-[var(--text-primary)] break-all">{item.source}</div>
                    <div className="text-[var(--text-secondary)] mt-1">{item.section}</div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
