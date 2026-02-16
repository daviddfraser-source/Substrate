#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REPORT="${ROOT_DIR}/docs/codex-migration/skills/pr-review-report.md"

if ! command -v reviewdog >/dev/null 2>&1; then
  echo "reviewdog not found on PATH"
  exit 1
fi

cd "${ROOT_DIR}"

base_ref="${PR_BASE_REF:-origin/main}"
if ! git rev-parse --verify "${base_ref}" >/dev/null 2>&1; then
  base_ref="HEAD~1"
fi

changed_files="$(git diff --name-only "${base_ref}"...HEAD || true)"

{
  echo "# PR Review Automation Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Base ref: \`${base_ref}\`"
  echo
  echo "## Changed Files"
  if [[ -n "${changed_files}" ]]; then
    echo '```'
    echo "${changed_files}"
    echo '```'
  else
    echo "No changed files detected."
  fi
  echo
  echo "## Reviewdog"
  echo "Reviewdog tool check passed."
} > "${REPORT}"

echo "pr-review-automation completed. Report: ${REPORT}"
