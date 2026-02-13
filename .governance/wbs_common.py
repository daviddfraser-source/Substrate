#!/usr/bin/env python3
"""
Shared utilities for WBS orchestration.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
GOV = Path(__file__).parent
WBS_DEF = GOV / "wbs.json"
WBS_STATE = GOV / "wbs-state.json"

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
    if not WBS_DEF.exists():
        return {}
    with open(WBS_DEF) as f:
        return json.load(f)


def load_state() -> dict:
    """Load current execution state."""
    if not WBS_STATE.exists():
        now = datetime.now().isoformat()
        return {
            "version": "1.0",
            "created_at": now,
            "updated_at": now,
            "packets": {},
            "log": [],
            "area_closeouts": {},
        }
    with open(WBS_STATE) as f:
        state = json.load(f)
    now = datetime.now().isoformat()
    state.setdefault("version", "1.0")
    state.setdefault("created_at", now)
    state.setdefault("updated_at", now)
    state.setdefault("packets", {})
    state.setdefault("log", [])
    state.setdefault("area_closeouts", {})
    return state


def get_counts(state: dict) -> dict:
    """Get packet counts by status."""
    counts = {}
    for pstate in state.get("packets", {}).values():
        s = pstate.get("status", "pending")
        counts[s] = counts.get(s, 0) + 1
    return counts
