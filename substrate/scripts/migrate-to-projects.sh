#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

USAGE() {
  cat <<'EOF'
Usage: substrate/scripts/migrate-to-projects.sh [--create <project-id>] [--activate <project-id>] [--from <wbs.json>]

Migration helper for project-scoped governance.

Behavior:
1) Ensures `.governance/current-project.json` exists (defaults to `main`).
2) Optionally creates a project namespace from source WBS.
3) Optionally activates a project namespace.

Notes:
- Structural mutation commands require approval token in strict mode.
- Provide token via env:
    WBS_CHANGE_APPROVAL=WBS-APPROVED:<change-id>
EOF
}

CREATE_ID=""
ACTIVATE_ID=""
FROM_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --create)
      CREATE_ID="${2:-}"
      shift 2
      ;;
    --activate)
      ACTIVATE_ID="${2:-}"
      shift 2
      ;;
    --from)
      FROM_PATH="${2:-}"
      shift 2
      ;;
    -h|--help)
      USAGE
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      USAGE >&2
      exit 1
      ;;
  esac
done

if [[ ! -f ".governance/current-project.json" ]]; then
  cat > ".governance/current-project.json" <<'JSON'
{
  "active_project": "main",
  "updated_at": "2026-02-23T00:00:00Z"
}
JSON
  echo "Created .governance/current-project.json (active_project=main)"
fi

approval_args=()
if [[ -n "${WBS_CHANGE_APPROVAL:-}" ]]; then
  approval_args=(--wbs-approval "${WBS_CHANGE_APPROVAL}")
fi

if [[ -n "${CREATE_ID}" ]]; then
  if [[ -n "${FROM_PATH}" ]]; then
    python3 .governance/wbs_cli.py "${approval_args[@]}" project-create "${CREATE_ID}" "${FROM_PATH}"
  else
    python3 .governance/wbs_cli.py "${approval_args[@]}" project-create "${CREATE_ID}"
  fi
fi

if [[ -n "${ACTIVATE_ID}" ]]; then
  python3 .governance/wbs_cli.py "${approval_args[@]}" project-set "${ACTIVATE_ID}"
fi

python3 .governance/wbs_cli.py project-show
