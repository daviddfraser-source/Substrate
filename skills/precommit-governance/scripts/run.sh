#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "${ROOT_DIR}"

if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit not found on PATH"
  exit 1
fi

if [[ ! -f ".pre-commit-config.yaml" ]]; then
  echo ".pre-commit-config.yaml not found; run install.sh first"
  exit 1
fi

pre-commit run --all-files
