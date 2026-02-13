#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TEMPLATE="${ROOT_DIR}/skills/skill-authoring/assets/SKILL.template.md"

[[ -f "${TEMPLATE}" ]] || { echo "Missing template: ${TEMPLATE}"; exit 1; }
echo "skill-authoring smoke passed"
