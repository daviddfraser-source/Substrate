#!/usr/bin/env bash
set -euo pipefail

# Primary docs should not require legacy Claude slash commands or sqlite DB recovery paths.
BAD_PATTERN='(/wbs-status|/claim-packet|/complete-packet|/reset-packet|/wbs-log|/wbs-report|sqlite3 .*wbs\.db|\.governance/wbs\.db)'

if rg -n -S "$BAD_PATTERN" \
  README.md AGENTS.md CLAUDE.md prompts docs \
  -g '!docs/codex-migration/command-map.md'; then
  echo "Found legacy command/db patterns in primary docs." >&2
  exit 1
fi

echo "Docs lint passed: no legacy command/db patterns in primary docs."
