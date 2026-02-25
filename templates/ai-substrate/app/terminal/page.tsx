"use client";

import { useMemo } from "react";

export default function TerminalPage() {
  const ttydUrl = useMemo(() => {
    const configured = process.env.NEXT_PUBLIC_TTYD_URL;
    if (configured) return configured;
    if (typeof window !== "undefined") {
      return `${window.location.protocol}//${window.location.hostname}:7681`;
    }
    return "http://127.0.0.1:7681";
  }, []);

  return (
    <div className="h-full flex flex-col p-6 space-y-4">
      <div>
        <div>
          <h1 className="text-2xl font-bold text-token-primary">Embedded CLI (ttyd)</h1>
          <p className="text-sm text-token-secondary mt-1">
            Direct ttyd terminal for low-latency PTY access.
          </p>
        </div>
      </div>

      <div className="bg-token-inset border border-token-border-default rounded-lg p-3">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-token-secondary">
          <p>Terminal endpoint: <span className="font-mono text-token-primary">{ttydUrl}</span></p>
          <a className="underline text-token-primary" href={ttydUrl} target="_blank" rel="noreferrer">
            Open in new tab
          </a>
        </div>
      </div>

      <iframe
        key={ttydUrl}
        src={ttydUrl}
        title="ttyd terminal"
        className="w-full flex-1 min-h-[600px] rounded-lg border border-token-border-default bg-black"
      />
    </div>
  );
}
