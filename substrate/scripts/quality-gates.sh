#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/5] Python syntax"
python3 -m py_compile .governance/wbs_cli.py .governance/wbs_server.py ../start.py

echo "[2/5] Shell syntax"
bash -n scripts/test.sh scripts/*.sh

echo "[3/5] Smoke tests"
./scripts/test.sh

echo "[4/6] Unit/e2e/contract/concurrency tests"
python3 -m unittest discover -s tests -v

echo "[5/6] E2E run capture"
python3 scripts/e2e-run.py \
  --suite governance-viewer-smoke \
  --trigger local \
  --agent codex \
  --cmd "python3 -m unittest substrate/tests/test_root_docs_paths.py -v"

echo "[6/6] Docs lint"
./scripts/check_docs_no_legacy_commands.sh

echo "Quality gates passed"
