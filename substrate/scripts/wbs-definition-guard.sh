#!/usr/bin/env bash
set -euo pipefail

MODE="staged"
COMMIT_MSG_FILE=""
RANGE=""

TRAILER_KEY="${WBS_CHANGE_TRAILER_KEY:-WBS-Change-Approved}"
PROJECT_TRAILER_KEY="${WBS_PROJECT_TRAILER_KEY:-WBS-Project}"
OVERRIDE_ENV="${ALLOW_WBS_DEFINITION_EDIT:-0}"

PROTECTED_PATTERNS=(
  ".governance/wbs.json"
  ".governance/current-project.json"
  ".governance/wbs-mutation-policy.json"
)

if [[ "${1:-}" == "--ci" ]]; then
  MODE="ci"
elif [[ "${1:-}" == "--commit-msg" ]]; then
  MODE="commit-msg"
  COMMIT_MSG_FILE="${2:-}"
elif [[ "${1:-}" == "--check-tracked" ]]; then
  MODE="tracked"
fi

get_changed_files() {
  if [[ -n "${WBS_DEFINITION_GUARD_CHANGED_FILES:-}" ]]; then
    printf "%s\n" "${WBS_DEFINITION_GUARD_CHANGED_FILES}"
    return 0
  fi

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "wbs-definition-guard: git worktree not detected; skipping"
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
    tracked)
      git ls-files
      ;;
    *)
      git diff --cached --name-only
      ;;
  esac
}

has_protected_change() {
  local changed="$1"
  if printf "%s\n" "${changed}" | grep -Eq '^projects/[^/]+/wbs\.json$'; then
    return 0
  fi
  for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if printf "%s\n" "${changed}" | grep -Fxq "${pattern}"; then
      return 0
    fi
  done
  return 1
}

has_required_trailer() {
  local text="$1"
  grep -Eiq "^${TRAILER_KEY}:[[:space:]]*[^[:space:]].*$" <<< "${text}"
}

if [[ "${OVERRIDE_ENV}" == "1" ]]; then
  echo "wbs-definition-guard: override accepted via ALLOW_WBS_DEFINITION_EDIT=1"
  exit 0
fi

changed_files="$(get_changed_files)"
if ! has_protected_change "${changed_files}"; then
  exit 0
fi

if [[ "${MODE}" == "tracked" ]]; then
  echo "wbs-definition-guard: protected files are tracked as expected"
  exit 0
fi

commit_text=""
if [[ "${MODE}" == "commit-msg" && -n "${COMMIT_MSG_FILE}" && -f "${COMMIT_MSG_FILE}" ]]; then
  commit_text="$(cat "${COMMIT_MSG_FILE}")"
elif [[ "${MODE}" == "ci" ]]; then
  commit_text="${WBS_DEFINITION_GUARD_COMMIT_MESSAGES:-}"
  if [[ -z "${commit_text}" && -n "${RANGE}" ]] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    commit_text="$(git log --format=%B "${RANGE}" 2>/dev/null || true)"
  fi
fi

if has_required_trailer "${commit_text}"; then
  exit 0
fi

cat >&2 <<EOF
ERROR: protected WBS/governance definition files changed without approval trailer.
Detected protected changes:
$(printf "%s\n" "${changed_files}" | sed 's/^/ - /')

Required commit trailer:
  ${TRAILER_KEY}: <ticket-or-change-id>

Recommended companion trailer:
  ${PROJECT_TRAILER_KEY}: <project-id>

Emergency local override:
  ALLOW_WBS_DEFINITION_EDIT=1
EOF
exit 1
