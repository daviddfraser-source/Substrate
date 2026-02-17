#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

WBS_SOURCE="${1:-.governance/wbs.json}"
STATE_FILE=".governance/wbs-state.json"
LEGACY_LOG_FILE=".governance/activity-log.jsonl"

if [[ ! -f "${WBS_SOURCE}" ]]; then
  echo "Missing WBS source: ${WBS_SOURCE}"
  exit 1
fi

echo "Resetting scaffold runtime state..."
rm -f "${STATE_FILE}" "${LEGACY_LOG_FILE}"

echo "Initializing scaffold from ${WBS_SOURCE}..."
python3 .governance/wbs_cli.py init "${WBS_SOURCE}"

echo "Validating scaffold..."
python3 .governance/wbs_cli.py validate

echo
echo "Scaffold reset complete."
echo "WBS source: ${WBS_SOURCE}"
echo "State file: ${STATE_FILE}"
echo
echo "Next:"
echo "  python3 .governance/wbs_cli.py ready"
