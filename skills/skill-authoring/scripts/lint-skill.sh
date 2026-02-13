#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: lint-skill.sh <path-to-SKILL.md>"
  exit 1
fi

file="$1"
[[ -f "${file}" ]] || { echo "Missing file: ${file}"; exit 1; }

required=(
  "## Purpose"
  "## Inputs"
  "## Outputs"
  "## Preconditions"
  "## Workflow"
  "## Commands"
  "## Failure Modes and Fallbacks"
  "## Validation"
  "## Evidence Notes Template"
)

for section in "${required[@]}"; do
  if ! rg -q "^${section}$" "${file}"; then
    echo "Missing section: ${section}"
    exit 1
  fi
done

echo "Skill lint passed: ${file}"
