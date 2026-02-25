"use client";

import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

type DocKind = "policy" | "runbook" | "architecture";

type KnowledgeDoc = {
  id: string;
  title: string;
  kind: DocKind;
  tags: string[];
  body: string;
};

const docs: KnowledgeDoc[] = [
  {
    id: "KB-100",
    title: "Governance Packet Lifecycle",
    kind: "policy",
    tags: ["wbs", "audit"],
    body: "## Lifecycle\n\n1. `claim`\n2. execute\n3. `done`/`fail`\n4. `note` evidence\n",
  },
  {
    id: "KB-101",
    title: "Terminal Operation Modes",
    kind: "runbook",
    tags: ["pty", "security"],
    body: "## Mode Matrix\n\n- `sandbox`: governed command allowlist\n- `dev`: full shell passthrough\n- `prod`: constrained runtime with audit\n",
  },
  {
    id: "KB-102",
    title: "Template Composition Guidelines",
    kind: "architecture",
    tags: ["frontend", "components"],
    body: "## Guidance\n\n- Prefer mature OSS components\n- Keep data contracts explicit\n- Keep templates API-ready\n",
  },
];

export default function KnowledgePage() {
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState<"all" | DocKind>("all");
  const [selectedId, setSelectedId] = useState("KB-100");

  const filtered = useMemo(() => {
    return docs.filter((doc) => {
      if (kind !== "all" && doc.kind !== kind) return false;
      if (query && !`${doc.title} ${doc.tags.join(" ")}`.toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
  }, [kind, query]);

  const active = filtered.find((doc) => doc.id === selectedId) || filtered[0] || docs[0];

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Knowledge Base Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Enterprise docs explorer using custom list, filters, and markdown rendering.</span>
      </div>

      <Card>
        <div className="flex flex-wrap items-center gap-4">
          <div className="w-[280px]">
            <Input
              placeholder="Search knowledge"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>
          <div className="w-[180px]">
            <Select
              value={kind}
              onChange={(e) => setKind(e.target.value as any)}
              options={[
                { value: "all", label: "All Types" },
                { value: "policy", label: "Policy" },
                { value: "runbook", label: "Runbook" },
                { value: "architecture", label: "Architecture" },
              ]}
            />
          </div>
          <Badge variant="info" className="ml-auto px-3 py-1 font-semibold">{filtered.length} documents</Badge>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1">
          <Card>
            <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-2">Documents</h3>
            <div className="flex flex-col gap-1">
              {filtered.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => setSelectedId(doc.id)}
                  className={`flex flex-col items-start gap-1 p-2 rounded w-full text-left transition-colors ${selectedId === doc.id
                      ? "bg-[var(--primary-50)] border-l-4 border-[var(--primary)]"
                      : "hover:bg-[var(--bg-inset)] border-l-4 border-transparent"
                    }`}
                >
                  <span className="text-sm font-semibold text-[var(--text-primary)]">{doc.title}</span>
                  <Badge variant="default" className="text-[10px] px-1 py-0">{doc.kind}</Badge>
                </button>
              ))}
              {filtered.length === 0 && (
                <div className="text-sm text-[var(--text-tertiary)] py-4 text-center">No documents found.</div>
              )}
            </div>
          </Card>
        </div>
        <div className="lg:col-span-2">
          {active ? (
            <Card>
              <h3 className="font-semibold text-xl mb-3">{active.title}</h3>
              <div className="flex flex-wrap gap-2 mb-6">
                <Badge variant="info">{active.kind}</Badge>
                {active.tags.map((tag) => <Badge variant="default" key={tag}>{tag}</Badge>)}
              </div>
              <div className="prose prose-sm max-w-none text-[var(--text-primary)]">
                <ReactMarkdown>{active.body}</ReactMarkdown>
              </div>
            </Card>
          ) : (
            <Card className="flex items-center justify-center p-12 text-[var(--text-secondary)]">
              Select a document to view its contents.
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
