"use client";

import { useMemo, useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface DocumentRow {
  key: string;
  name: string;
  owner: string;
  updatedAt: string;
  sizeKb: number;
  status: "draft" | "review" | "published" | "archived";
}

const seededRows: DocumentRow[] = [
  { key: "D-01", name: "phase5-template-rollout-plan.md", owner: "product", updatedAt: "2026-02-25", sizeKb: 42, status: "published" },
  { key: "D-02", name: "security-auth-controls.md", owner: "security", updatedAt: "2026-02-24", sizeKb: 27, status: "review" },
  { key: "D-03", name: "component-architecture.md", owner: "frontend", updatedAt: "2026-02-23", sizeKb: 35, status: "draft" },
  { key: "D-04", name: "legacy-export.csv", owner: "ops", updatedAt: "2026-02-20", sizeKb: 11, status: "archived" },
];

export default function DocumentsPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"all" | DocumentRow["status"]>("all");
  const [rows, setRows] = useState(seededRows);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach((uploaded) => {
      setTimeout(() => {
        setRows((prev) => [
          {
            key: `D-${Date.now()}-${Math.random()}`,
            name: uploaded.name,
            owner: "current-user",
            updatedAt: new Date().toISOString().slice(0, 10),
            sizeKb: Math.max(1, Math.round(uploaded.size / 1024)),
            status: "draft",
          },
          ...prev,
        ]);
        // Note: we removed antd message, ideally we'd use a toast context here.
      }, 600);
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const filtered = useMemo(() => {
    return rows.filter((row) => {
      if (status !== "all" && row.status !== status) return false;
      if (query && !`${row.name} ${row.owner}`.toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
  }, [query, rows, status]);

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Documents Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Custom Upload + native Table + filtering for enterprise document management starter.</span>
      </div>

      <Card>
        <div className="flex flex-wrap items-center gap-4">
          <div className="w-[280px]">
            <Input
              placeholder="Search file or owner"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>
          <div className="w-[180px]">
            <Select
              value={status}
              onChange={(e) => setStatus(e.target.value as any)}
              options={[
                { value: "all", label: "All status" },
                { value: "draft", label: "Draft" },
                { value: "review", label: "Review" },
                { value: "published", label: "Published" },
                { value: "archived", label: "Archived" },
              ]}
            />
          </div>
          <Badge variant="info" className="ml-auto px-3 py-1 font-semibold">{filtered.length} documents</Badge>
        </div>
      </Card>

      <Card>
        <div className="flex flex-col gap-4">
          <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2">Upload</h3>
          <div
            className="border-2 border-dashed border-[var(--border-strong)] rounded-lg p-8 text-center hover:bg-[var(--bg-secondary)] transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              multiple
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileUpload}
            />
            <p className="text-[var(--text-primary)] font-medium mb-1">Click to upload files</p>
            <p className="text-[var(--text-secondary)] text-sm">Template implementation uses custom request and can be mapped to your storage API.</p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-[var(--border-default)] pb-2">
            <h3 className="font-semibold text-lg">Repository</h3>
            <Button variant="outline" onClick={() => setRows(seededRows)}>Reset Seed Data</Button>
          </div>

          <div className="overflow-x-auto w-full border border-[var(--border-default)] rounded-md">
            <table className="w-full text-left text-sm text-[var(--text-primary)]">
              <thead className="bg-[var(--bg-secondary)] border-b border-[var(--border-default)] text-[var(--text-secondary)]">
                <tr>
                  <th className="px-4 py-3 font-medium">File</th>
                  <th className="px-4 py-3 font-medium">Owner</th>
                  <th className="px-4 py-3 font-medium">Updated</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-default)]">
                {filtered.length > 0 ? (
                  filtered.map((row) => (
                    <tr key={row.key} className="hover:bg-[var(--bg-inset)] transition-colors">
                      <td className="px-4 py-3 font-medium">{row.name}</td>
                      <td className="px-4 py-3">{row.owner}</td>
                      <td className="px-4 py-3">{row.updatedAt}</td>
                      <td className="px-4 py-3">{row.sizeKb} KB</td>
                      <td className="px-4 py-3">
                        <Badge variant={row.status === "published" ? "success" : row.status === "review" ? "warning" : row.status === "draft" ? "info" : "default"}>
                          {row.status}
                        </Badge>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-[var(--text-tertiary)]">No documents match the filters.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </Card>
    </div>
  );
}
