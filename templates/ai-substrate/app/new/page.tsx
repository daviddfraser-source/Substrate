"use client";

import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { z } from "zod";

const schema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  summary: z.string().min(12, "Summary must be at least 12 characters"),
  owner: z.enum(["product", "platform", "security", "ops"]),
  priority: z.enum(["low", "medium", "high"]),
  tags: z.string().optional(),
});

type FormPayload = z.infer<typeof schema>;

export default function NewItemFormPage() {
  const [submitting, setSubmitting] = useState(false);
  const [createdId, setCreatedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [payload, setPayload] = useState<FormPayload>({
    title: "",
    summary: "",
    owner: "product",
    priority: "medium",
    tags: "",
  });

  const preview = useMemo(() => ({
    ...payload,
    tags: payload.tags
      ?.split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
  }), [payload]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCreatedId(null);
    const parsed = schema.safeParse(payload);
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message || "Invalid payload");
      return;
    }

    setSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 600));
    setCreatedId(`TPL-${Date.now().toString().slice(-6)}`);
    setSubmitting(false);
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">New Item Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Enterprise create-form starter with zod validation and payload preview using custom components.</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-4">Create</h3>
            <form onSubmit={submit} className="flex flex-col gap-5">
              <Input
                label="Title *"
                value={payload.title}
                onChange={(event) => setPayload((prev) => ({ ...prev, title: event.target.value }))}
              />

              <div className="flex flex-col gap-1">
                <label className="text-sm font-semibold text-[var(--text-secondary)]">Summary *</label>
                <textarea
                  rows={5}
                  className="w-full px-3 py-2 rounded-md border border-[var(--border-strong)] bg-[var(--bg-primary)] text-[var(--text-primary)] focus:border-[var(--primary)] outline-none transition-colors resize-y"
                  value={payload.summary}
                  onChange={(event) => setPayload((prev) => ({ ...prev, summary: event.target.value }))}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Select
                  label="Owner"
                  value={payload.owner}
                  options={[
                    { value: "product", label: "Product" },
                    { value: "platform", label: "Platform" },
                    { value: "security", label: "Security" },
                    { value: "ops", label: "Ops" },
                  ]}
                  onChange={(e) => setPayload((prev) => ({ ...prev, owner: e.target.value as any }))}
                />

                <Select
                  label="Priority"
                  value={payload.priority}
                  options={[
                    { value: "low", label: "Low" },
                    { value: "medium", label: "Medium" },
                    { value: "high", label: "High" },
                  ]}
                  onChange={(e) => setPayload((prev) => ({ ...prev, priority: e.target.value as any }))}
                />

                <Input
                  label="Tags (csv)"
                  value={payload.tags}
                  onChange={(event) => setPayload((prev) => ({ ...prev, tags: event.target.value }))}
                />
              </div>

              <div className="pt-2 border-t border-[var(--border-default)] flex flex-col items-start gap-3">
                {error && <div className="text-sm font-semibold text-[var(--danger)]">{error}</div>}
                {createdId && <div className="text-sm font-semibold text-[var(--success)]">Created item: <strong>{createdId}</strong></div>}

                <Button type="submit" variant="primary" loading={submitting}>Create Item</Button>
              </div>
            </form>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card className="h-full flex flex-col">
            <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-4">Payload Preview</h3>
            <pre className="text-xs whitespace-pre-wrap bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded p-4 text-[var(--text-secondary)] mb-4 flex-1">
              {JSON.stringify(preview, null, 2)}
            </pre>
            <div className="flex items-center gap-2 text-sm font-medium">
              Priority:
              <Badge variant={payload.priority === "high" ? "danger" : payload.priority === "medium" ? "warning" : "success"}>
                {payload.priority}
              </Badge>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
