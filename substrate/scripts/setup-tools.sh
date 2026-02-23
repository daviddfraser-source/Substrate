#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="${ROOT_DIR}/docs/codex-migration/toolchain-report.md"

PYTHON_TARGET="3.10+"
NODE_TARGET="20+"
PRECOMMIT_TARGET="3.7.1"
PLAYWRIGHT_TARGET="@playwright/test@1.49.1"
PROMPTFOO_TARGET="promptfoo@0.95.0"

mkdir -p "$(dirname "${REPORT}")"

have() { command -v "$1" >/dev/null 2>&1; }

python_ver="$(python3 --version 2>/dev/null || true)"
node_ver="$(node --version 2>/dev/null || true)"
npm_ver="$(npm --version 2>/dev/null || true)"
precommit_ver="$(pre-commit --version 2>/dev/null || true)"

{
  echo "# Toolchain Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "## Target Versions"
  echo "- Python: ${PYTHON_TARGET}"
  echo "- Node: ${NODE_TARGET}"
  echo "- pre-commit: ${PRECOMMIT_TARGET}"
  echo "- Playwright package: ${PLAYWRIGHT_TARGET}"
  echo "- Promptfoo package: ${PROMPTFOO_TARGET}"
  echo
  echo "## Detected Versions"
  echo "- ${python_ver:-python3 not found}"
  echo "- ${node_ver:-node not found}"
  echo "- npm ${npm_ver:-not found}"
  echo "- ${precommit_ver:-pre-commit not found}"
} > "${REPORT}"

if [[ "${1:-}" == "--install" ]]; then
  if have pip; then
    pip install "pre-commit==${PRECOMMIT_TARGET}" || true
  fi
  if have npm; then
    npm install -g "${PLAYWRIGHT_TARGET}" "${PROMPTFOO_TARGET}" || true
  fi
  echo >> "${REPORT}"
  echo "Install attempt executed (`--install`)." >> "${REPORT}"
fi

echo "Wrote ${REPORT}"
