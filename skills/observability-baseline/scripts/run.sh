#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STATE="${ROOT_DIR}/.governance/wbs-state.json"
OUT_EVENTS="${ROOT_DIR}/docs/codex-migration/skills/observability-events.json"
OUT_REPORT="${ROOT_DIR}/docs/codex-migration/skills/observability-report.md"

mkdir -p "$(dirname "${OUT_EVENTS}")"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(".").resolve()
state_path = root / ".governance" / "wbs-state.json"
events_path = root / "docs" / "codex-migration" / "skills" / "observability-events.json"
report_path = root / "docs" / "codex-migration" / "skills" / "observability-report.md"

state = json.loads(state_path.read_text())
log = state.get("log", [])
sample = log[-50:]

events_path.write_text(json.dumps(sample, indent=2) + "\n")

unique_events = sorted({e.get("event", "") for e in sample if isinstance(e, dict)})

report = [
    "# Observability Baseline Report",
    "",
    f"Generated events sample: `{events_path.relative_to(root)}`",
    "",
    f"Sample size: {len(sample)}",
    f"Unique event types: {', '.join(unique_events) if unique_events else '(none)'}",
    "",
    "Core event fields expected: `packet_id`, `event`, `timestamp`, `agent`, `notes`.",
]
report_path.write_text("\n".join(report) + "\n")
PY

echo "observability-baseline completed. Report: ${OUT_REPORT}"
