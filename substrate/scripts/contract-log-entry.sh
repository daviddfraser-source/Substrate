#!/bin/bash
set -euo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 <summary> <file> [more files]"
  exit 1
fi
summary=$1
shift
date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
log="docs/codex-migration/ai-substrate/contract-changelog.md"
files=$(printf "%s, " "$@")
files=${files%, }
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  verified=$(git status -sb | head -n1)
else
  verified="git status unavailable (not in repo)"
fi
cat <<EOM >> "$log"
## $date
- Summary: $summary
- Files: $files
- Verified: $verified

EOM
