#!/usr/bin/env bash
set -euo pipefail

TARGET_FILE=".governance/wbs-state.json"
OVERRIDE_TOKEN="[allow-wbs-state-edit]"

MODE="staged"
COMMIT_MSG_FILE=""
RANGE=""

if [[ "${1:-}" == "--ci" ]]; then
  MODE="ci"
elif [[ "${1:-}" == "--commit-msg" ]]; then
  MODE="commit-msg"
  COMMIT_MSG_FILE="${2:-}"
fi

get_changed_files() {
  if [[ -n "${GOV_STATE_GUARD_CHANGED_FILES:-}" ]]; then
    printf "%s\n" "${GOV_STATE_GUARD_CHANGED_FILES}"
    return 0
  fi

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "governance-state-guard: git worktree not detected; skipping"
    return 0
  fi

  case "${MODE}" in
    staged|commit-msg)
      git diff --cached --name-only
      ;;
    ci)
      if [[ -n "${GITHUB_BASE_REF:-}" ]]; then
        git fetch --no-tags --depth=1 origin "${GITHUB_BASE_REF}" >/dev/null 2>&1 || true
        RANGE="origin/${GITHUB_BASE_REF}...HEAD"
      elif git rev-parse HEAD~1 >/dev/null 2>&1; then
        RANGE="HEAD~1..HEAD"
      else
        RANGE="HEAD"
      fi
      git diff --name-only "${RANGE}"
      ;;
    *)
      git diff --cached --name-only
      ;;
  esac
}

changed_files="$(get_changed_files)"
if ! printf "%s\n" "${changed_files}" | grep -Fxq "${TARGET_FILE}"; then
  exit 0
fi

if [[ "${ALLOW_WBS_STATE_EDIT:-0}" == "1" ]]; then
  echo "governance-state-guard: override accepted via ALLOW_WBS_STATE_EDIT=1"
  exit 0
fi

if [[ "${MODE}" == "commit-msg" && -n "${COMMIT_MSG_FILE}" && -f "${COMMIT_MSG_FILE}" ]]; then
  if grep -Fqi "${OVERRIDE_TOKEN}" "${COMMIT_MSG_FILE}"; then
    echo "governance-state-guard: override token accepted from commit message"
    exit 0
  fi
fi

if [[ "${MODE}" == "ci" ]]; then
  commit_messages="${GOV_STATE_GUARD_COMMIT_MESSAGES:-}"
  if [[ -z "${commit_messages}" && -n "${RANGE}" ]] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    commit_messages="$(git log --format=%B "${RANGE}" 2>/dev/null || true)"
  fi
  if [[ -n "${commit_messages}" ]] && grep -Fqi "${OVERRIDE_TOKEN}" <<<"${commit_messages}"; then
    echo "governance-state-guard: override token accepted from CI commit range"
    exit 0
  fi
fi

cat >&2 <<EOF
ERROR: direct changes to ${TARGET_FILE} are blocked by governance guard.

Allowed paths:
1) Run lifecycle commands through the CLI (preferred):
   python3 .governance/wbs_cli.py <claim|done|note|fail|reset|closeout-l2> ...
2) For emergency/manual corrections, include override token in commit message:
   ${OVERRIDE_TOKEN}
3) For local one-off bypass, set:
   ALLOW_WBS_STATE_EDIT=1
EOF
exit 1
