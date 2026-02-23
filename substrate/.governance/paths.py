#!/usr/bin/env python3
"""
This module defines canonical path constants and a dynamic path resolution contract for repository tooling.

Path Resolution Contract:
-------------------------
All critical runtime paths (e.g., WBS definition, WBS state, residual risk register, break-fix log)
MUST be resolved dynamically at the point of use via the `resolve_runtime_paths()` function.

This ensures that:
1. Paths accurately reflect the currently active project context, even if the project changes
   during a CLI session (e.g., via `project-set`).
2. There are no stale module-level global path constants that could diverge from the active
   project's files, leading to subtle and hard-to-diagnose bugs.

Module-level global path constants like `WBS_DEF_PATH` (and similar from previous versions)
have been removed or will be deprecated. Direct access to these module-level constants
is discouraged. Instead, always call `resolve_runtime_paths()` to get an up-to-date dictionary
of paths for the current project context.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# .../repo/substrate/.governance/paths.py -> repo root is parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]
SUBSTRATE_ROOT = REPO_ROOT / "substrate"
GOV_DIR = SUBSTRATE_ROOT / ".governance"
SRC_DIR = SUBSTRATE_ROOT / "src"
DOCS_DIR = SUBSTRATE_ROOT / "docs"
SCRIPTS_DIR = SUBSTRATE_ROOT / "scripts"
TEMPLATES_DIR = SUBSTRATE_ROOT / "templates"
TESTS_DIR = SUBSTRATE_ROOT / "tests"
PROJECTS_DIR = SUBSTRATE_ROOT / "projects"
CURRENT_PROJECT_PATH = GOV_DIR / "current-project.json"
DEFAULT_PROJECT_ID = "main"


def normalize_project_id(value: str) -> str:
    token = str(value or "").strip()
    if not token:
        return DEFAULT_PROJECT_ID
    token = token.lower()
    token = re.sub(r"[^a-z0-9._-]+", "-", token)
    token = re.sub(r"-{2,}", "-", token).strip("-.")
    return token or DEFAULT_PROJECT_ID


def get_active_project_id() -> str:
    env_project = normalize_project_id(str(os.environ.get("WBS_PROJECT", "")).strip())
    if env_project and env_project != DEFAULT_PROJECT_ID:
        return env_project
    if CURRENT_PROJECT_PATH.exists():
        try:
            payload = json.loads(CURRENT_PROJECT_PATH.read_text())
            if isinstance(payload, dict):
                return normalize_project_id(payload.get("active_project", DEFAULT_PROJECT_ID))
        except Exception:
            return DEFAULT_PROJECT_ID
    return DEFAULT_PROJECT_ID


def set_active_project_id(project_id: str) -> str:
    pid = normalize_project_id(project_id)
    CURRENT_PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CURRENT_PROJECT_PATH.write_text(
        json.dumps({"active_project": pid, "updated_at": datetime.now().isoformat()}, indent=2) + "\n"
    )
    return pid


def project_root(project_id: str) -> Path:
    pid = normalize_project_id(project_id)
    if pid == DEFAULT_PROJECT_ID:
        return GOV_DIR
    return PROJECTS_DIR / pid


def resolve_runtime_paths(project_id: str = "") -> dict:
    pid = normalize_project_id(project_id) if project_id else get_active_project_id()
    root = project_root(pid)
    return {
        "project_id": pid,
        "root": root,
        "wbs_def": root / "wbs.json",
        "wbs_state": root / "wbs-state.json",
        "residual_risk_register": root / "residual-risk-register.json",
        "break_fix_log": root / "break-fix-log.json",
        "e2e_runs": root / "e2e-runs.json",
        "current_project": CURRENT_PROJECT_PATH, # The current-project.json is a global path, not project-scoped
    }
