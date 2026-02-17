#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

WBS_TEMPLATE="${1:-.governance/wbs.json}"
WBS_FILE=".governance/wbs.json"
STATE_FILE=".governance/wbs-state.json"

if [[ ! -f "${WBS_TEMPLATE}" ]]; then
  echo "Missing WBS template: ${WBS_TEMPLATE}"
  exit 1
fi

echo "Initializing scaffold from ${WBS_TEMPLATE}..."
python3 .governance/wbs_cli.py init "${WBS_TEMPLATE}"

echo "Validating WBS and packet schema..."
python3 .governance/wbs_cli.py validate
python3 .governance/wbs_cli.py validate-packet "${WBS_FILE}"

if command -v pre-commit >/dev/null 2>&1 && [[ -f ".pre-commit-config.yaml" ]]; then
  echo "Installing pre-commit hooks..."
  pre-commit install
fi

echo
echo "Scaffold initialized."
echo "WBS:   ${WBS_FILE}"
echo "State: ${STATE_FILE}"
echo
echo "Next:"
echo "  python3 .governance/wbs_cli.py ready"
