#!/usr/bin/env bash
set -euo pipefail

for tool in semgrep trivy gitleaks; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "${tool} not found on PATH"
    exit 1
  fi
done

echo "security-gates smoke passed"
