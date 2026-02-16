#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUT_DIR="${ROOT_DIR}/docs/codex-migration/skills/ui-regression"
REPORT="${ROOT_DIR}/docs/codex-migration/skills/ui-regression-report.md"
BASE="${UI_BASE_URL:-http://127.0.0.1:8090}"

mkdir -p "${OUT_DIR}"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found on PATH"
  exit 1
fi

cd "${ROOT_DIR}/skills/ui-regression"

set +e
UI_BASE_URL="${BASE}" npx playwright test --config=playwright.config.ts >"${OUT_DIR}/playwright.log" 2>&1
rc=$?
set -e

{
  echo "# ui-regression Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Base URL: \`${BASE}\`"
  echo "Log: \`docs/codex-migration/skills/ui-regression/playwright.log\`"
  echo
  if [[ ${rc} -eq 0 ]]; then
    echo "Status: PASS"
  else
    echo "Status: FAIL (exit ${rc})"
  fi
} > "${REPORT}"

if [[ ${rc} -ne 0 ]]; then
  echo "ui-regression failed. See ${REPORT}"
  exit ${rc}
fi

echo "ui-regression completed. Report: ${REPORT}"
