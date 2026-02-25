"use client";

import { useMemo } from "react";

export default function WbsViewerPage() {
  const legacyViewerUrl = useMemo(() => {
    if (typeof window === "undefined") {
      return "http://127.0.0.1:8080/";
    }
    return `${window.location.protocol}//${window.location.hostname}:8080/`;
  }, []);

  return (
    <div className="h-full flex flex-col bg-token-canvas">
      <div className="bg-token-elevated border-b border-token-border-default px-4 py-3 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-base font-semibold text-token-primary">WBS Viewer</h1>
          <p className="text-xs text-token-secondary">Legacy AG Grid collapsible WBS manager.</p>
        </div>
        <a
          href={legacyViewerUrl}
          target="_blank"
          rel="noreferrer"
          className="px-3 py-1.5 text-xs bg-token-inset text-token-primary rounded border border-token-border-default hover:border-token-border-strong transition-colors"
        >
          Open Fullscreen
        </a>
      </div>
      <div className="flex-1 min-h-0">
        <iframe
          title="Legacy WBS Manager"
          src={legacyViewerUrl}
          className="w-full h-full border-0"
          loading="eager"
        />
      </div>
    </div>
  );
}
