#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

STAMP="$(date -u +%Y%m%d-%H%M%S)"
OUT_DIR="${ROOT_DIR}/dist"
BUNDLE_NAME="substrate-template-${STAMP}"
STAGE_DIR="$(mktemp -d)"
TARGET_DIR="${STAGE_DIR}/${BUNDLE_NAME}"
ARCHIVE="${OUT_DIR}/${BUNDLE_NAME}.tar.gz"

mkdir -p "${OUT_DIR}"

python3 - "${ROOT_DIR}" "${TARGET_DIR}" <<'PY'
import json
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()

ignore = shutil.ignore_patterns(
    ".git", ".github/workflows/*.tmp", "__pycache__", "*.pyc", ".DS_Store",
    "dist", ".venv", ".pytest_cache", "*.log"
)
shutil.copytree(root, target, ignore=ignore)

# Reset mutable execution state for template consumers.
state_path = target / ".governance" / "wbs-state.json"
state = {
    "packets": {},
    "log": [],
    "area_closeouts": {}
}
state_path.write_text(json.dumps(state, indent=2) + "\n")
PY

tar -C "${STAGE_DIR}" -czf "${ARCHIVE}" "${BUNDLE_NAME}"
rm -rf "${STAGE_DIR}"

echo "Built template bundle: ${ARCHIVE}"
