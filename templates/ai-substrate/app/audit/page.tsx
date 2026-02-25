"use client";

import { useEffect, useState } from "react";
import { AuditTable } from "@/components/governance/AuditTable";
import { fetchLog, type LogEntry } from "@/lib/governance/api-client";

export default function AuditPage() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    const loadLog = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchLog(limit);
        setEntries(data.log);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load audit log");
      } finally {
        setLoading(false);
      }
    };
    loadLog();
  }, [limit]);

  const handleRefresh = () => {
    setLimit(50);
    window.location.reload();
  };

  const handleLoadMore = () => {
    setLimit((prev) => prev + 50);
  };

  if (loading && entries.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-token-primary mx-auto mb-4"></div>
          <p className="text-token-secondary">Loading audit log...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-token-elevated border-b border-token-border-default p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-token-primary">Audit Log</h1>
            <p className="text-sm text-token-secondary">
              {entries.length} recent events
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              className="px-3 py-1.5 text-sm bg-token-inset text-token-primary rounded border border-token-border-default hover:border-token-border-strong transition-colors"
              disabled={loading}
            >
              ↻ Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="m-4 p-4 bg-token-danger-muted border border-token-danger rounded-md">
          <p className="text-sm text-token-danger">⚠️ {error}</p>
        </div>
      )}

      {/* Audit Table */}
      <div className="flex-1 overflow-auto p-4">
        <AuditTable entries={entries} />

        {/* Load More */}
        {entries.length >= limit && (
          <div className="mt-4 text-center">
            <button
              onClick={handleLoadMore}
              disabled={loading}
              className="px-4 py-2 text-sm bg-token-primary text-white rounded-md hover:bg-opacity-90 transition-colors disabled:opacity-50"
            >
              {loading ? "Loading..." : "Load More"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
