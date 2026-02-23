#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

required_files=(
  ".governance/wbs.json"
  ".governance/wbs_cli.py"
  ".governance/residual-risk-register.schema.json"
  "scripts/init-scaffold.sh"
  "scripts/reset-scaffold.sh"
  "scripts/scaffold-check.sh"
  "scripts/governance-state-guard.sh"
  "docs/template-usage.md"
)

required_any=(
  "README.md|../README.md"
)

echo "[1/6] Required scaffold assets"
for path in "${required_files[@]}"; do
  if [[ ! -f "${path}" ]]; then
    echo "Missing required scaffold artifact: ${path}" >&2
    exit 1
  fi
done

for spec in "${required_any[@]}"; do
  IFS='|' read -r -a options <<< "${spec}"
  found=0
  for candidate in "${options[@]}"; do
    if [[ -f "${candidate}" ]]; then
      found=1
      break
    fi
  done
  if [[ "${found}" -ne 1 ]]; then
    echo "Missing required scaffold artifact (any of): ${spec}" >&2
    exit 1
  fi
done

echo "[2/6] WBS structure validation"
python3 .governance/wbs_cli.py validate
python3 .governance/wbs_cli.py validate-packet .governance/wbs.json

echo "[3/6] Runtime artifact tracked guard"
./scripts/governance-state-guard.sh --check-tracked

echo "[4/6] Scaffold contract checks"
./scripts/scaffold-check.sh

echo "[5/6] Bootstrap command smoke (isolated workspace)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT
mkdir -p "${TMPDIR}/repo/substrate"
cp -r .governance "${TMPDIR}/repo/substrate/.governance"
cp -r src "${TMPDIR}/repo/substrate/src"
mkdir -p "${TMPDIR}/repo/substrate/scripts"
cp scripts/init-scaffold.sh scripts/reset-scaffold.sh "${TMPDIR}/repo/substrate/scripts/"
chmod +x "${TMPDIR}/repo/substrate/scripts/init-scaffold.sh" "${TMPDIR}/repo/substrate/scripts/reset-scaffold.sh"
(
  cd "${TMPDIR}/repo/substrate"
  ./scripts/init-scaffold.sh .governance/wbs.json >/tmp/template-integrity-init.log
  ./scripts/reset-scaffold.sh .governance/wbs.json >/tmp/template-integrity-reset.log
  python3 .governance/wbs_cli.py validate >/tmp/template-integrity-validate.log
)

echo "[6/6] Template integrity: PASS"
