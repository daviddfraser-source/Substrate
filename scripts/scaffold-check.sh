#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="${ROOT_DIR}/docs/codex-migration/scaffold-check-report.md"

cd "${ROOT_DIR}"

mkdir -p "$(dirname "${REPORT}")"

status="PASS"
notes=()

check_cmd() {
  local label="$1"
  shift
  if "$@" >/tmp/scaffold-check.out 2>/tmp/scaffold-check.err; then
    notes+=("- ${label}: PASS")
  else
    status="FAIL"
    notes+=("- ${label}: FAIL")
  fi
}

check_cmd "WBS validate" python3 .governance/wbs_cli.py validate
check_cmd "Packet schema validate" python3 .governance/wbs_cli.py validate-packet .governance/wbs.json
check_cmd "Template packet schema validate (minimal profile)" python3 .governance/wbs_cli.py validate-packet templates/wbs-codex-minimal.json
check_cmd "Runtime artifact tracked guard" ./scripts/governance-state-guard.sh --check-tracked
check_cmd "State json parse" python3 -m json.tool .governance/wbs-state.json
check_cmd "Definition json parse" python3 -m json.tool .governance/wbs.json
check_cmd "Residual risk schema json parse" python3 -m json.tool .governance/residual-risk-register.schema.json
check_cmd "CLI/server/start compile" python3 -m py_compile .governance/wbs_cli.py .governance/wbs_server.py start.py
check_cmd "Docs legacy command check" ./scripts/check_docs_no_legacy_commands.sh

{
  echo "# Scaffold Check Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "Overall: ${status}"
  echo
  echo "## Checks"
  printf "%s\n" "${notes[@]}"
} > "${REPORT}"

echo "Scaffold check: ${status}"
echo "Report: ${REPORT}"

if [[ "${status}" != "PASS" ]]; then
  exit 1
fi
