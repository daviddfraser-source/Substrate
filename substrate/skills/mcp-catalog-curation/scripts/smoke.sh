#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

[[ -f "${ROOT_DIR}/skills/mcp-catalog-curation/assets/allowlist.json" ]] || { echo "Missing allowlist"; exit 1; }
[[ -f "${ROOT_DIR}/skills/mcp-catalog-curation/assets/review-checklist.md" ]] || { echo "Missing review checklist"; exit 1; }

echo "mcp-catalog-curation smoke passed"
