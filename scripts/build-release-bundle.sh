#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="dist"
NAME="substrate-release-bundle-${STAMP}.tar.gz"
mkdir -p "$OUT_DIR"

# Keep bundle intentionally scoped to migration operators.
FILES=(
  AGENTS.md
  README.md
  CLAUDE.md
  .governance/wbs_cli.py
  .governance/wbs_server.py
  .governance/static/index.html
  templates/wbs-codex-refactor.json
  scripts
  prompts
  docs/codex-migration
  docs/PLAYBOOK.md
  docs/TEAM_PATTERNS.md
  docs/CRITICAL_APP_EXECUTION_CHECKLIST.md
)

tar -czf "$OUT_DIR/$NAME" "${FILES[@]}"

echo "Bundle created: $OUT_DIR/$NAME"
