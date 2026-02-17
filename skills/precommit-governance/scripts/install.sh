#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SRC="${ROOT_DIR}/skills/precommit-governance/assets/pre-commit-config.yaml"
DST="${ROOT_DIR}/.pre-commit-config.yaml"

if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit not found on PATH"
  exit 1
fi

cp "${SRC}" "${DST}"
pre-commit install

echo "Installed pre-commit config at ${DST}"
