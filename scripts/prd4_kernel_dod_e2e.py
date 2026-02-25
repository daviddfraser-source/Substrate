#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core import ActorContext, FileStorage, PacketEngine  # noqa: E402
from substrate_core.audit import export_provenance_snapshot  # noqa: E402


def main() -> int:
    started = time.time()
    actor = ActorContext(user_id="dod-runner", role="operator", source="script")

    definition = {
        "packets": [
            {"id": "A", "title": "Seed policy and dependencies"},
            {"id": "B", "title": "Execute governed work unit"},
        ],
        "dependencies": {"B": ["A"]},
        "policy": {
            "version": "1.0",
            "rules": [
                {
                    "id": "allow-operator-claim",
                    "domain": "governance",
                    "type": "role",
                    "effect": "allow",
                    "match": {"roles": ["operator"], "transition": "claim"},
                },
                {
                    "id": "allow-operator-done",
                    "domain": "governance",
                    "type": "role",
                    "effect": "allow",
                    "match": {"roles": ["operator"], "transition": "done"},
                },
            ],
        },
    }

    with tempfile.TemporaryDirectory() as td:
        state_path = Path(td) / "wbs-state.json"
        storage = FileStorage(state_path)
        engine = PacketEngine(storage=storage, definition=definition)

        events = []

        blocked = engine.claim("B", actor)
        events.append({"step": "claim_B_before_A", "ok": blocked.ok, "message": blocked.message})

        claim_a = engine.claim("A", actor)
        events.append({"step": "claim_A", "ok": claim_a.ok, "message": claim_a.message})

        done_a = engine.done("A", actor, "A completed")
        events.append({"step": "done_A", "ok": done_a.ok, "message": done_a.message})

        claim_b = engine.claim("B", actor)
        events.append({"step": "claim_B_after_A", "ok": claim_b.ok, "message": claim_b.message})

        done_b = engine.done("B", actor, "B completed")
        events.append({"step": "done_B", "ok": done_b.ok, "message": done_b.message})

        upstream_b = engine.upstream("B")
        downstream_a = engine.downstream("A")
        critical = engine.critical_path()
        impact_a = engine.impact_analysis("A")
        pg_templates = engine.postgres_query_templates()

        state = storage.read_state()
        prov_b = export_provenance_snapshot(state, "B")

        elapsed = round(time.time() - started, 3)
        result = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scenario": "PRD v4 kernel DoD E2E (isolated temp state)",
            "elapsed_seconds": elapsed,
            "events": events,
            "graph": {
                "upstream_B": upstream_b.payload.get("upstream", []),
                "downstream_A": downstream_a.payload.get("downstream", []),
                "critical_path": critical.payload.get("critical_path", []),
                "impact_A": impact_a.payload.get("impacted", []),
                "postgres_query_keys": sorted(list(pg_templates.payload.get("queries", {}).keys())),
            },
            "provenance_B_event_count": prov_b.get("event_count", 0),
            "checks": {
                "dependency_gate_enforced": (blocked.ok is False),
                "transition_sequence_success": all(x.ok for x in [claim_a, done_a, claim_b, done_b]),
                "provenance_export_present": prov_b.get("event_count", 0) > 0,
                "graph_queries_present": bool(critical.payload.get("critical_path")),
            },
        }

    reports = ROOT / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    out = reports / "prd-v4-kernel-dod-report.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
