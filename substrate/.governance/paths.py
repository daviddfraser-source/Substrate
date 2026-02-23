#!/usr/bin/env python3
"""Canonical path constants for repository tooling."""

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

WBS_DEF_PATH = GOV_DIR / "wbs.json"
WBS_STATE_PATH = GOV_DIR / "wbs-state.json"
