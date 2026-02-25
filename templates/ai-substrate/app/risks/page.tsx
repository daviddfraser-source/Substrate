"use client";

import { useEffect, useState } from "react";
import { RiskTable } from "@/components/governance/RiskTable";
import { fetchStatus, type StatusResponse } from "@/lib/governance/api-client";

interface Risk {
  id: string;
  packetId: string;
  title: string;
  severity: "low" | "medium" | "high" | "critical";
  likelihood: "low" | "medium" | "high";
  impact: string;
  mitigation: string;
  status: "open" | "mitigated" | "accepted";
}

export default function RisksPage() {
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadRisks = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch status data to extract risk information
        const statusData = await fetchStatus();

        // Extract risks from packet notes/metadata
        // This is a placeholder - in production, risks would come from dedicated endpoints
        const extractedRisks: Risk[] = [];

        statusData.areas.forEach((area) => {
          area.packets.forEach((packet) => {
            // Example: Extract risks from failed or blocked packets
            if (packet.status === "failed") {
              extractedRisks.push({
                id: `risk-${packet.id}`,
                packetId: packet.id,
                title: `Packet ${packet.wbs_ref} failed`,
                severity: "high",
                likelihood: "high",
                impact: packet.notes || "Packet execution failed",
                mitigation: "Review failure notes and restart packet",
                status: "open",
              });
            }
          });
        });

        setRisks(extractedRisks);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load risks");
      } finally {
        setLoading(false);
      }
    };
    loadRisks();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-token-primary mx-auto mb-4"></div>
          <p className="text-token-secondary">Loading risk register...</p>
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
            <h1 className="text-xl font-bold text-token-primary">Risk Register</h1>
            <p className="text-sm text-token-secondary">
              {risks.length} identified risks
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1.5 text-sm bg-token-inset text-token-primary rounded border border-token-border-default hover:border-token-border-strong transition-colors"
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

      {/* Risk Table */}
      <div className="flex-1 overflow-auto p-4">
        {risks.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-2xl mb-2">✅</p>
              <p className="text-token-secondary">No active risks identified</p>
              <p className="text-sm text-token-tertiary mt-1">
                All packets are executing within acceptable parameters
              </p>
            </div>
          </div>
        ) : (
          <RiskTable risks={risks} />
        )}
      </div>
    </div>
  );
}
