"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { PacketViewer } from "@/components/governance/PacketViewer";
import { fetchPacket, type PacketResponse } from "@/lib/governance/api-client";

export default function PacketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const packetId = params?.id as string;

  const [packet, setPacket] = useState<PacketResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!packetId) return;

    const loadPacket = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchPacket(packetId);
        setPacket(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load packet");
      } finally {
        setLoading(false);
      }
    };

    loadPacket();
  }, [packetId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-token-primary mx-auto mb-4"></div>
          <p className="text-token-secondary">Loading packet details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <p className="text-token-danger mb-2">⚠️ Error Loading Packet</p>
          <p className="text-sm text-token-secondary">{error}</p>
          <div className="flex gap-2 justify-center mt-4">
            <button
              onClick={() => router.back()}
              className="px-4 py-2 bg-token-inset text-token-primary rounded-md hover:bg-token-canvas transition-colors border border-token-border-default"
            >
              ← Back
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-token-primary text-white rounded-md hover:bg-opacity-90 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!packet) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-token-secondary">Packet not found</p>
          <button
            onClick={() => router.push("/packets")}
            className="mt-4 px-4 py-2 bg-token-primary text-white rounded-md hover:bg-opacity-90 transition-colors"
          >
            Back to Packets
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <div className="max-w-6xl mx-auto p-6">
        {/* Back Button */}
        <button
          onClick={() => router.push("/packets")}
          className="mb-4 text-sm text-token-secondary hover:text-token-primary transition-colors flex items-center gap-1"
        >
          ← Back to Packets
        </button>

        {/* Packet Viewer */}
        <PacketViewer
          packet={packet.packet}
          events={packet.events}
          documents={packet.documents}
        />
      </div>
    </div>
  );
}
