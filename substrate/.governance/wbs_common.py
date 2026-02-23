#!/usr/bin/env python3
"""
Shared utilities for WBS orchestration.
"""

import json
import os
import sys
from datetime import datetime

from paths import GOV_DIR, SRC_DIR, resolve_runtime_paths

# Paths
GOV = GOV_DIR

# WBS_DEF and WBS_STATE are resolved at call-time via resolve_runtime_paths()
# so that project context set by apply_runtime_project() / WBS_PROJECT env var
# is always respected (module-level constants WBS_DEF_PATH/WBS_STATE_PATH were
# removed from paths.py as part of the multi-project refactor).
def _wbs_def() -> "Path":
    return resolve_runtime_paths()["wbs_def"]

def _wbs_state() -> "Path":
    return resolve_runtime_paths()["wbs_state"]

SRC_PATH = SRC_DIR
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    from governed_platform.governance.status import normalize_runtime_status, normalize_packet_status_map
    from governed_platform.governance.log_integrity import normalize_log_mode
except Exception:
    # Fallback keeps utility import-safe even before src is available.
    normalize_runtime_status = lambda value, default="pending", strict=False: str(value or default).lower()  # noqa: E731
    normalize_packet_status_map = lambda state: state  # noqa: E731
    normalize_log_mode = lambda value, strict=False: str(value or "plain").lower()  # noqa: E731

# Colors (respects NO_COLOR env var)
def c(code, text):
    if os.environ.get("NO_COLOR") or not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
        return text
    return f"\033[{code}m{text}\033[0m"

green = lambda t: c("32", t)
red = lambda t: c("31", t)
yellow = lambda t: c("33", t)
blue = lambda t: c("34", t)
bold = lambda t: c("1", t)
dim = lambda t: c("2", t)


def load_definition() -> dict:
    """Load WBS definition (read-only after init)."""
    path = _wbs_def()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def load_state() -> dict:
    """Load current execution state."""
    path = _wbs_state()
    if not path.exists():
        now = datetime.now().isoformat()
        return {
            "version": "1.0",
            "created_at": now,
            "updated_at": now,
            "packets": {},
            "log": [],
            "area_closeouts": {},
            "log_integrity_mode": "plain",
        }
    with open(path) as f:
        state = json.load(f)
    now = datetime.now().isoformat()
    state.setdefault("version", "1.0")
    state.setdefault("created_at", now)
    state.setdefault("updated_at", now)
    state.setdefault("packets", {})
    state.setdefault("log", [])
    state.setdefault("area_closeouts", {})
    state.setdefault("log_integrity_mode", "plain")
    state["log_integrity_mode"] = normalize_log_mode(state.get("log_integrity_mode"))
    return normalize_packet_status_map(state)


def get_counts(state: dict) -> dict:
    """Get packet counts by status."""
    counts = {}
    for pstate in state.get("packets", {}).values():
        s = normalize_runtime_status(pstate.get("status", "pending"))
        counts[s] = counts.get(s, 0) + 1
    return counts
