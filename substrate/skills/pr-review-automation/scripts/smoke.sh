#!/usr/bin/env bash
set -euo pipefail

if ! command -v reviewdog >/dev/null 2>&1; then
  echo "reviewdog not found on PATH"
  exit 1
fi

echo "reviewdog available"
