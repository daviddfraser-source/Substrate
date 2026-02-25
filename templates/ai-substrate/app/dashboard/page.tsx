"use client";

import { useEffect, useState } from "react";
import { KpiCard } from "@/components/governance/KpiCard";
import { ProgressRing } from "@/components/governance/ProgressRing";
import { DependencyGraph } from "@/components/governance/DependencyGraph";
import { fetchStatus, fetchProgress, fetchDepsGraph, type StatusResponse, type ProgressResponse, type DepsGraphResponse } from "@/lib/governance/api-client";

export default function DashboardPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [graph, setGraph] = useState<DepsGraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [statusData, progressData, graphData] = await Promise.all([
          fetchStatus(),
          fetchProgress(),
          fetchDepsGraph(),
        ]);
        setStatus(statusData);
        setProgress(progressData);
        setGraph(graphData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-token-primary mx-auto mb-4"></div>
          <p className="text-token-secondary">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <p className="text-token-danger mb-2">⚠️ Error Loading Dashboard</p>
          <p className="text-sm text-token-secondary">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-token-primary text-white rounded-md hover:bg-opacity-90 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const counts = progress?.counts || { pending: 0, in_progress: 0, done: 0, failed: 0, blocked: 0 };
  const total = progress?.total || 0;
  const completionRate = total > 0 ? Math.round((counts.done / total) * 100) : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-token-primary mb-1">
          Operational Dashboard
        </h1>
        <p className="text-sm text-token-secondary">
          Real-time governance snapshot
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Total Packets"
          value={total}
          trend="neutral"
          icon="📦"
        />
        <KpiCard
          label="Completed"
          value={counts.done}
          trend="up"
          trendValue={`${completionRate}%`}
          icon="✅"
        />
        <KpiCard
          label="In Progress"
          value={counts.in_progress}
          trend="neutral"
          icon="⏳"
        />
        <KpiCard
          label="Blocked"
          value={counts.blocked}
          trend={counts.blocked > 0 ? "down" : "neutral"}
          icon="🚫"
        />
      </div>

      {/* Progress Ring */}
      <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
        <h2 className="text-lg font-semibold text-token-primary mb-4">
          Completion Progress
        </h2>
        <div className="flex items-center gap-8">
          <ProgressRing
            progress={completionRate}
            size={120}
            strokeWidth={10}
          />
          <div className="flex-1 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-token-secondary">Done</span>
              <span className="text-sm font-medium text-token-primary">
                {counts.done} / {total}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-token-secondary">Pending</span>
              <span className="text-sm font-medium text-token-primary">
                {counts.pending}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-token-secondary">Failed</span>
              <span className="text-sm font-medium text-token-danger">
                {counts.failed}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Critical Path / Dependency Graph */}
      {graph && (
        <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
          <h2 className="text-lg font-semibold text-token-primary mb-4">
            Dependency Graph
          </h2>
          <DependencyGraph nodes={graph.nodes} edges={graph.edges} />
        </div>
      )}

      {/* Work Areas Summary */}
      {status && (
        <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
          <h2 className="text-lg font-semibold text-token-primary mb-4">
            Work Areas
          </h2>
          <div className="space-y-3">
            {status.areas.map((area) => {
              const areaDone = area.packets.filter(p => p.status === "done").length;
              const areaTotal = area.packets.length;
              const areaCompletion = areaTotal > 0 ? Math.round((areaDone / areaTotal) * 100) : 0;

              return (
                <div key={area.id} className="flex items-center justify-between p-3 rounded bg-token-inset">
                  <div>
                    <h3 className="font-medium text-token-primary text-sm">{area.title}</h3>
                    <p className="text-xs text-token-tertiary">{area.id}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-token-secondary">
                      {areaDone}/{areaTotal}
                    </span>
                    <div className="w-24 h-2 bg-token-border-default rounded-full overflow-hidden">
                      <div
                        className="h-full bg-token-primary transition-all"
                        style={{ width: `${areaCompletion}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-token-primary w-10 text-right">
                      {areaCompletion}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
