#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: substrate/scripts/publish-git-ready.sh <snapshot-name>

Publishes a clean git-ready snapshot under:
  substrate/dist/git-ready/<snapshot-name>

Generated template artifacts are excluded automatically:
  - substrate/templates/ai-substrate/node_modules/
  - substrate/templates/ai-substrate/dist/
  - substrate/templates/ai-substrate/.next/
  - substrate/templates/ai-substrate/coverage/
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 1
fi

SNAPSHOT_NAME="$1"
if [[ -z "${SNAPSHOT_NAME}" || "${SNAPSHOT_NAME}" == .* ]]; then
  echo "Invalid snapshot name: ${SNAPSHOT_NAME}" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PUBLISH_PARENT="${REPO_ROOT}/substrate/dist/git-ready"
TARGET="${PUBLISH_PARENT}/${SNAPSHOT_NAME}"
STAGE="${PUBLISH_PARENT}/.stage-${SNAPSHOT_NAME}-$$"

cleanup() {
  rm -rf "${STAGE}"
}
trap cleanup EXIT

mkdir -p "${PUBLISH_PARENT}"
rm -rf "${STAGE}"
mkdir -p "${STAGE}"

RSYNC_EXCLUDES=(
  ".git/"
  "substrate/dist/git-ready/"
  "__pycache__/"
  ".pytest_cache/"
  ".mypy_cache/"
  "substrate/templates/ai-substrate/node_modules/"
  "substrate/templates/ai-substrate/dist/"
  "substrate/templates/ai-substrate/.next/"
  "substrate/templates/ai-substrate/coverage/"
)

RSYNC_ARGS=("-a" "--delete")
for exclude in "${RSYNC_EXCLUDES[@]}"; do
  RSYNC_ARGS+=("--exclude=${exclude}")
done

rsync "${RSYNC_ARGS[@]}" "${REPO_ROOT}/" "${STAGE}/"

rm -rf "${TARGET}"
mv "${STAGE}" "${TARGET}"

echo "Published clean git-ready snapshot:"
echo "  ${TARGET}"
echo "File count: $(find "${TARGET}" -type f | wc -l)"
echo "Size:       $(du -sh "${TARGET}" | awk '{print $1}')"
