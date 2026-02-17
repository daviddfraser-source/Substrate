#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

INIT_SOURCE="${1:-.governance/wbs.json}"

echo "== WBS Preflight =="

echo "[1/6] Tooling"
python3 --version
git --version || true

echo "[2/6] Required files"
for f in .governance/wbs_cli.py .governance/wbs.json; do
  [ -f "$f" ] || { echo "Missing required file: $f" >&2; exit 1; }
  echo "ok: $f"
done

echo "[3/6] JSON integrity"
python3 -m json.tool .governance/wbs.json >/dev/null
if [ -f .governance/wbs-state.json ]; then
  python3 -m json.tool .governance/wbs-state.json >/dev/null
fi

echo "[4/6] CLI sanity"
python3 .governance/wbs_cli.py --help >/dev/null

echo "[5/6] State bootstrap"
if [ ! -f .governance/wbs-state.json ]; then
  echo "state missing: initializing from $INIT_SOURCE"
  python3 .governance/wbs_cli.py init "$INIT_SOURCE"
else
  echo "state present"
fi

echo "[6/6] Next work"
python3 .governance/wbs_cli.py progress
python3 .governance/wbs_cli.py ready

echo "Preflight complete"
