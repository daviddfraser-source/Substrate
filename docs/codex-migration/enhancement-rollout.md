# Session Continuity Enhancement Rollout

## Scope

This rollout covers the WBS `10.0` enhancement streams:
- briefing/context contracts (`UPG-044`, `UPG-045`, `UPG-047`)
- governed handover/resume (`UPG-046`)
- capability profile enforcement (`UPG-048`)
- guided planning and markdown import (`UPG-049`, `UPG-050`)

Primary owner: governance operator (`codex-lead` by default).  
Data/reporting owner: repository maintainer.

## KPI Definition

| KPI | Target | Collection Method | Owner | Cadence |
| --- | --- | --- | --- | --- |
| Session bootstrap latency (`briefing` p95) | <= 400 ms local p95 over 5 runs | timed CLI run | governance operator | weekly |
| Handover continuity success | >= 95% (`resumed` handovers completed without manual reset) | state log analysis | governance operator | weekly |
| Planning adoption | >= 80% of new WBS definitions include `metadata.planning_source` | inspect WBS metadata | repository maintainer | per new WBS |
| Capability-check signal quality | >= 90% of advisory warnings are actionable (known capability tags, known agent ids) | warning event review + registry check | governance operator | weekly |

## Evidence Commands

### Bootstrap latency

```bash
python3 - <<'PY'
import json
import statistics
import subprocess
import time

samples = []
for _ in range(5):
    t0 = time.perf_counter()
    subprocess.run(
        ["python3", ".governance/wbs_cli.py", "briefing", "--format", "json", "--recent", "20"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    samples.append((time.perf_counter() - t0) * 1000.0)

ordered = sorted(samples)
p95_idx = max(0, int(round(0.95 * (len(ordered) - 1))))
print(json.dumps({"samples_ms": samples, "p95_ms": ordered[p95_idx]}, indent=2))
PY
```

### Handover continuity success

```bash
python3 - <<'PY'
import json
from pathlib import Path

state = json.loads(Path(".governance/wbs-state.json").read_text())
log = [e for e in state.get("log", []) if isinstance(e, dict)]
handover = [e for e in log if e.get("event") == "handover"]
resumed = [e for e in log if e.get("event") == "resumed"]
completed = [e for e in log if e.get("event") == "completed"]
completed_after_resume = {
    e.get("packet_id")
    for e in completed
    if any(r.get("packet_id") == e.get("packet_id") for r in resumed)
}
total = len(handover)
success = len(completed_after_resume)
rate = 1.0 if total == 0 else success / total
print(json.dumps({
    "handover_count": total,
    "resume_count": len(resumed),
    "completed_after_resume": success,
    "success_rate": rate
}, indent=2))
PY
```

### Planning adoption

```bash
python3 - <<'PY'
import json
from pathlib import Path

wbs = json.loads(Path(".governance/wbs.json").read_text())
meta = wbs.get("metadata", {})
print(json.dumps({
    "project_name": meta.get("project_name"),
    "planning_source": meta.get("planning_source", "missing"),
    "planning_generated_at": meta.get("planning_generated_at", "missing")
}, indent=2))
PY
```

### Capability-check signal quality

```bash
python3 - <<'PY'
import json
from pathlib import Path

state = json.loads(Path(".governance/wbs-state.json").read_text())
registry = json.loads(Path(".governance/agents.json").read_text())
taxonomy = set(registry.get("capability_taxonomy", []))
warnings = [
    e for e in state.get("log", [])
    if isinstance(e, dict) and e.get("event") == "capability_warning"
]
actionable = 0
for w in warnings:
    notes = str(w.get("notes") or "")
    if "unknown required capability tags" not in notes and "not registered" not in notes:
        actionable += 1
print(json.dumps({
    "warning_count": len(warnings),
    "actionable_warning_count": actionable,
    "actionable_ratio": 1.0 if not warnings else actionable / len(warnings),
    "taxonomy_size": len(taxonomy)
}, indent=2))
PY
```

## Operational Runbook

### 1) Briefing + Context Contracts

Enable:
- `python3 .governance/wbs_cli.py briefing --format json --recent 20`
- `python3 .governance/wbs_cli.py context <packet_id> --format json --max-events 40 --max-notes-bytes 4000 --max-handovers 40`

Validate:
- envelope keys match `docs/codex-migration/briefing-context-schema.md`
- no parser failures in downstream consumers

Rollback:
- use text mode only (`--format text`) and reduce payload limits while consumer mismatch is resolved.

### 2) Handover + Resume

Enable:
- `python3 .governance/wbs_cli.py handover <packet_id> <agent> "<reason>" --to <next_agent> --remaining "item1|item2"`
- `python3 .governance/wbs_cli.py resume <packet_id> <next_agent>`

Validate:
- `done/fail` blocked during active handover
- `resume` closes active handover and reassigns owner

Rollback:
- avoid `handover` command temporarily and complete packets in single-session ownership.

### 3) Capability Profiles

Enable:
- `python3 .governance/wbs_cli.py agent-list`
- `python3 .governance/wbs_cli.py agent-mode advisory`
- `python3 .governance/wbs_cli.py agent-register <id> <type> <cap1,cap2,...>`

Validate:
- advisory mode emits `capability_warning` events without blocking
- strict mode blocks mismatched claims

Rollback:
- set `agent-mode disabled` to restore legacy claim behavior.

### 4) Guided Planning + Markdown Import

Enable:
- `python3 .governance/wbs_cli.py plan --from-json planner-spec.json --output .governance/wbs-draft.json`
- `python3 .governance/wbs_cli.py plan --import-markdown docs/proposal.md --output .governance/wbs-imported.json`

Validate:
- `python3 .governance/wbs_cli.py init <draft-file>`
- `python3 .governance/wbs_cli.py validate`
- imported drafts include `import_confidence` markers for uncertain mappings

Rollback:
- disable markdown import usage and return to manual/spec-driven `plan --from-json` only.

## Residual Risks

- advisory mode can accumulate warning debt if operators do not review logs.
- markdown import can still produce overly broad packet scopes requiring manual refinement.
- consumer scripts may lag schema additions if they enforce strict key sets.

## Go/No-Go Criteria

Go:
- all four KPI measurements collected at least once
- checklist in `docs/release-checklist-codex.md` passes
- no unresolved strict-mode claim blockers for active operators

No-Go:
- repeated cycle/validation failures from planner outputs
- handover success rate below target for two consecutive weekly checks
