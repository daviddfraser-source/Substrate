#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

allowed=(
  ".claude"
  ".claudeignore"
  ".codex"
  ".devcontainer"
  ".gemini"
  ".gitattributes"
  ".github"
  ".gitignore"
  ".pre-commit-config.yaml"
  "AGENTS.md"
  "CLAUDE.md"
  "GEMINI.md"
  "LICENSE"
  "Makefile"
  "README.md"
  "START.md"
  "app"
  "bootstrap.ps1"
  "bootstrap.sh"
  "codex.md"
  "constitution.md"
  "pyproject.toml"
  "start.py"
  "substrate"
)

declare -A allowmap=()
for item in "${allowed[@]}"; do
  allowmap["$item"]=1
done

violations=()
while IFS= read -r entry; do
  name="${entry#./}"
  if [[ "$name" == ".git" ]]; then
    continue
  fi
  if [[ -z "${allowmap[$name]:-}" ]]; then
    violations+=("$name")
  fi
done < <(find . -mindepth 1 -maxdepth 1 -print | sort)

if [[ ${#violations[@]} -gt 0 ]]; then
  echo "Root hygiene check failed. Unexpected root entries:" >&2
  for v in "${violations[@]}"; do
    echo "  - $v" >&2
  done
  exit 1
fi

echo "Root hygiene check passed."
