#!/usr/bin/env bash
set -euo pipefail

if ! command -v promptfoo >/dev/null 2>&1; then
  echo "promptfoo not found on PATH"
  exit 1
fi

echo "promptfoo available: $(promptfoo --version | head -n 1)"
