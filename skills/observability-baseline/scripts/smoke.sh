#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STATE="${ROOT_DIR}/.governance/wbs-state.json"
SCHEMA="${ROOT_DIR}/skills/observability-baseline/assets/event-schema.json"
COLLECTOR="${ROOT_DIR}/skills/observability-baseline/assets/otel-collector.yaml"

[[ -f "${STATE}" ]] || { echo "Missing ${STATE}"; exit 1; }
[[ -f "${SCHEMA}" ]] || { echo "Missing ${SCHEMA}"; exit 1; }
[[ -f "${COLLECTOR}" ]] || { echo "Missing ${COLLECTOR}"; exit 1; }

echo "observability-baseline smoke passed"
