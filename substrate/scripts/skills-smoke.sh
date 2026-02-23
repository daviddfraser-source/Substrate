#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${ROOT_DIR}/skills"
REPORT="${ROOT_DIR}/docs/codex-migration/skills-smoke-report.md"

mkdir -p "$(dirname "${REPORT}")"

echo "# Skills Smoke Report" > "${REPORT}"
echo "" >> "${REPORT}"
echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "${REPORT}"
echo "" >> "${REPORT}"
echo "| Skill | Result | Notes |" >> "${REPORT}"
echo "|---|---|---|" >> "${REPORT}"

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "No skills directory found at ${SKILLS_DIR}"
  exit 1
fi

fail_count=0
ran_count=0

while IFS= read -r -d '' smoke; do
  ran_count=$((ran_count + 1))
  skill="$(basename "$(dirname "$(dirname "${smoke}")")")"

  if bash "${smoke}" >/tmp/"${skill}"-smoke.log 2>&1; then
    echo "| ${skill} | PASS | \`scripts/smoke.sh\` succeeded |" >> "${REPORT}"
  else
    fail_count=$((fail_count + 1))
    note="$(tail -n 1 /tmp/"${skill}"-smoke.log | sed 's/|/\\|/g')"
    echo "| ${skill} | FAIL | ${note:-smoke failed} |" >> "${REPORT}"
  fi
done < <(find "${SKILLS_DIR}" -type f -path "*/scripts/smoke.sh" -print0 | sort -z)

echo "" >> "${REPORT}"
echo "Ran ${ran_count} smoke checks; failures: ${fail_count}." >> "${REPORT}"

if [[ "${ran_count}" -eq 0 ]]; then
  echo "No smoke scripts found."
  exit 1
fi

if [[ "${fail_count}" -gt 0 ]]; then
  echo "Smoke checks completed with failures (${fail_count})."
  exit 1
fi

echo "Smoke checks passed (${ran_count}). Report: ${REPORT}"
