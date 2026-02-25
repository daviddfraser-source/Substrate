#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TTYD_BIN="${ROOT_DIR}/tools/bin/ttyd"
PID_FILE="${ROOT_DIR}/.ttyd.pid"
LOG_FILE="${ROOT_DIR}/logs/ttyd.log"
PORT="${TTYD_PORT:-7681}"
HOST="${TTYD_HOST:-0.0.0.0}"
CMD="${TTYD_CMD:-bash -l}"

mkdir -p "${ROOT_DIR}/logs"

if [[ ! -x "${TTYD_BIN}" ]]; then
  echo "ttyd binary missing at ${TTYD_BIN}" >&2
  echo "Install with: curl -fL https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.x86_64 -o tools/bin/ttyd && chmod +x tools/bin/ttyd" >&2
  exit 1
fi

if [[ -f "${PID_FILE}" ]]; then
  OLD_PID="$(cat "${PID_FILE}")"
  if kill -0 "${OLD_PID}" 2>/dev/null; then
    echo "ttyd already running (pid ${OLD_PID}) at http://${HOST}:${PORT}"
    exit 0
  fi
fi

setsid "${TTYD_BIN}" -i "${HOST}" -p "${PORT}" -W -w "${ROOT_DIR}" ${CMD} \
  </dev/null >> "${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"

sleep 1
echo "ttyd started at http://${HOST}:${PORT} (pid $(cat "${PID_FILE}"))"
