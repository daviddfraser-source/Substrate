#!/usr/bin/env bash
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found on PATH"
  exit 1
fi

base="${UI_BASE_URL:-http://127.0.0.1:8090}"
if ! curl -fsS "${base}/api/status" >/dev/null; then
  echo "Dashboard not reachable at ${base}"
  exit 1
fi

echo "ui-regression smoke passed for ${base}"
