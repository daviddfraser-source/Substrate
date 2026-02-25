#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

AGENT_NAME="${1:-codex}"
PACKET_ID="${2:-}"

echo "[startup] Generating session brief"
python3 scripts/generate-session-brief.py

echo "[startup] Ready packets"
python3 .governance/wbs_cli.py ready --json

echo "[startup] Status snapshot"
python3 .governance/wbs_cli.py progress --json

if [[ -n "${PACKET_ID}" ]]; then
  echo "[startup] Claiming ${PACKET_ID} as ${AGENT_NAME}"
  python3 .governance/wbs_cli.py claim "${PACKET_ID}" "${AGENT_NAME}"
  echo "[startup] Generating packet bundle"
  python3 scripts/generate-packet-bundle.py "${PACKET_ID}"
  echo "[startup] Packet context"
  python3 .governance/wbs_cli.py context "${PACKET_ID}" --format json --max-events 40 --max-notes-bytes 4000
else
  echo "[startup] Pass packet id to auto-claim and bundle:"
  echo "  scripts/session-start.sh ${AGENT_NAME} <packet_id>"
fi
