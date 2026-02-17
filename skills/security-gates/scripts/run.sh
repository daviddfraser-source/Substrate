#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUT_DIR="${ROOT_DIR}/docs/codex-migration/skills/security"
REPORT="${ROOT_DIR}/docs/codex-migration/skills/security-gates-report.md"

mkdir -p "${OUT_DIR}"

run_or_capture() {
  local name="$1"
  shift
  set +e
  "$@" >"${OUT_DIR}/${name}.json" 2>"${OUT_DIR}/${name}.stderr"
  local rc=$?
  set -e
  echo "${rc}"
}

if ! command -v semgrep >/dev/null 2>&1 || ! command -v trivy >/dev/null 2>&1 || ! command -v gitleaks >/dev/null 2>&1; then
  echo "Required tools missing. Run smoke first."
  exit 1
fi

semgrep_rc="$(run_or_capture semgrep semgrep scan --config auto --json "${ROOT_DIR}")"
trivy_rc="$(run_or_capture trivy trivy fs --format json "${ROOT_DIR}")"
gitleaks_rc="$(run_or_capture gitleaks gitleaks detect --source "${ROOT_DIR}" --report-format json --report-path /dev/stdout)"

{
  echo "# security-gates Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "| Tool | Exit Code |"
  echo "|---|---|"
  echo "| semgrep | ${semgrep_rc} |"
  echo "| trivy | ${trivy_rc} |"
  echo "| gitleaks | ${gitleaks_rc} |"
} > "${REPORT}"

fail=0
if [[ "${SECURITY_FAIL_ON_SEMGREP:-1}" == "1" && "${semgrep_rc}" -ne 0 ]]; then fail=1; fi
if [[ "${SECURITY_FAIL_ON_TRIVY:-1}" == "1" && "${trivy_rc}" -ne 0 ]]; then fail=1; fi
if [[ "${SECURITY_FAIL_ON_GITLEAKS:-1}" == "1" && "${gitleaks_rc}" -ne 0 ]]; then fail=1; fi

if [[ "${fail}" -ne 0 ]]; then
  echo "security-gates completed with policy failures. See ${REPORT}"
  exit 1
fi

echo "security-gates completed. Report: ${REPORT}"
