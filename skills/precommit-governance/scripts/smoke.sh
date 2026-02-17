#!/usr/bin/env bash
set -euo pipefail

if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit not found on PATH"
  exit 1
fi

echo "pre-commit available"
