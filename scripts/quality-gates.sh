#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/5] Python syntax"
python3 -m py_compile .governance/wbs_cli.py .governance/wbs_server.py start.py

echo "[2/5] Shell syntax"
bash -n test.sh scripts/*.sh

echo "[3/5] Smoke tests"
bash ./test.sh

echo "[4/5] Unit/e2e/contract/concurrency tests"
python3 -m unittest discover -s tests -v

echo "[5/5] Docs lint"
bash ./scripts/check_docs_no_legacy_commands.sh

echo "Quality gates passed"
