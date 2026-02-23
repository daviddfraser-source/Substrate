#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

TEMPLATE="${1:-substrate/templates/wbs-codex-minimal.json}"
STATE="substrate/.governance/wbs-state.json"

if [ ! -f "${STATE}" ]; then
  echo "Initializing scaffold from ${TEMPLATE}..."
  ./substrate/scripts/init-scaffold.sh "${TEMPLATE}"
fi

echo
echo "Status"
python3 start.py --status

echo
echo "Briefing"
python3 substrate/.governance/wbs_cli.py briefing --format json

echo
echo "Ready"
python3 substrate/.governance/wbs_cli.py ready
