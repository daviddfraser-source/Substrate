#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

profile="codex-only"
auto_yes=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      profile="$2"
      shift 2
      ;;
    --yes)
      auto_yes="--yes"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: substrate/scripts/post-clone-cleanup.sh [--profile codex-only|minimal|all-agents] [--yes]" >&2
      exit 2
      ;;
  esac
done

"${ROOT_DIR}/substrate/scripts/clone-profile.sh" apply "$profile" ${auto_yes}
# Clean common transient root cache before hygiene verification.
if [[ -d "${ROOT_DIR}/__pycache__" ]]; then
  rm -r "${ROOT_DIR}/__pycache__"
fi
"${ROOT_DIR}/substrate/scripts/check-root-hygiene.sh"
