#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROFILE_DIR="${ROOT_DIR}/substrate/templates/clone-profiles"

usage() {
  cat <<USAGE
Usage:
  substrate/scripts/clone-profile.sh list
  substrate/scripts/clone-profile.sh show <profile>
  substrate/scripts/clone-profile.sh preview <profile>
  substrate/scripts/clone-profile.sh apply <profile> [--yes]
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

cmd="$1"
profile="${2:-}"

get_profile_path() {
  if [[ -z "$profile" ]]; then
    echo "Profile is required." >&2
    exit 2
  fi
  local path="${PROFILE_DIR}/${profile}.json"
  if [[ ! -f "$path" ]]; then
    echo "Profile not found: $profile" >&2
    exit 1
  fi
  echo "$path"
}

list_profiles() {
  find "$PROFILE_DIR" -maxdepth 1 -name '*.json' -printf '%f\n' | sed 's/\.json$//' | sort
}

load_remove_entries() {
  local p="$1"
  python3 - "$p" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, encoding='utf-8') as f:
    data = json.load(f)
for item in data.get("remove", []):
    print(item)
PY
}

case "$cmd" in
  list)
    list_profiles
    ;;
  show)
    p="$(get_profile_path)"
    cat "$p"
    ;;
  preview|apply)
    p="$(get_profile_path)"
    mapfile -t remove_list < <(load_remove_entries "$p")
    echo "Profile: $profile"
    if [[ ${#remove_list[@]} -eq 0 ]]; then
      echo "No paths to remove."
      exit 0
    fi
    echo "Paths to remove from repo root:"
    for item in "${remove_list[@]}"; do
      echo "  - $item"
      if [[ "$item" == ".git" || "$item" == "/" || "$item" == "" ]]; then
        echo "Unsafe removal target in profile: $item" >&2
        exit 1
      fi
    done

    if [[ "$cmd" == "preview" ]]; then
      exit 0
    fi

    confirm="${3:-}"
    if [[ "$confirm" != "--yes" ]]; then
      read -r -p "Apply profile '$profile'? [y/N] " ans
      if [[ ! "$ans" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
      fi
    fi

    cd "$ROOT_DIR"
    for item in "${remove_list[@]}"; do
      if [[ -e "$item" ]]; then
        rm -r "$item"
        echo "Removed: $item"
      fi
    done
    ;;
  *)
    usage
    exit 2
    ;;
esac
