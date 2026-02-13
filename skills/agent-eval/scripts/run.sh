#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CONFIG="${ROOT_DIR}/skills/agent-eval/assets/promptfooconfig.yaml"
OUT_DIR="${ROOT_DIR}/docs/codex-migration/skills/agent-eval-results"
REPORT="${ROOT_DIR}/docs/codex-migration/skills/agent-eval-report.md"

mkdir -p "${OUT_DIR}"

if ! command -v promptfoo >/dev/null 2>&1; then
  echo "promptfoo not found on PATH"
  exit 1
fi

set +e
promptfoo eval -c "${CONFIG}" --output "${OUT_DIR}/results.json"
rc=$?
set -e

{
  echo "# agent-eval Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "Config: \`skills/agent-eval/assets/promptfooconfig.yaml\`"
  echo "Output: \`docs/codex-migration/skills/agent-eval-results/results.json\`"
  echo
  if [[ ${rc} -eq 0 ]]; then
    echo "Status: PASS"
  else
    echo "Status: FAIL (exit ${rc})"
  fi
} > "${REPORT}"

if [[ ${rc} -ne 0 ]]; then
  echo "agent-eval failed. See ${REPORT}"
  exit ${rc}
fi

echo "agent-eval completed. Report: ${REPORT}"
