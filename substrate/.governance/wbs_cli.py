#!/usr/bin/env python3
"""
WBS Orchestration CLI — JSON-based state management.
Simple, readable, git-friendly.
"""

import json
import sys
import csv
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent)) # Add .governance to sys.path


from wbs_common import (
    GOV,
    green, red, yellow, bold, dim,
    load_definition, load_state, get_counts
)

sys.path.insert(0, str(Path(__file__).parent)) # Add .governance to sys.path


from wbs_common import (
    GOV,
    green, red, yellow, bold, dim,
    load_definition, load_state, get_counts
)

SRC_PATH = GOV.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from governed_platform.governance.engine import GovernanceEngine
from governed_platform.governance.file_lock import atomic_write_json
from governed_platform.governance.git_ledger import (
    GIT_MODE_ADVISORY,
    GIT_MODE_DISABLED,
    GIT_MODE_STRICT,
    GIT_MODES,
    PROTOCOL_VERSION as GIT_PROTOCOL_VERSION,
    REQUIRED_TRAILERS as GIT_PROTOCOL_REQUIRED_TRAILERS,
    build_closeout_tag,
    close_packet_branch,
    create_tag,
    current_branch,
    ensure_git_worktree,
    format_governance_commit,
    load_git_governance_config,
    open_packet_branch,
    parse_governance_commit_from_hash,
    parse_governance_commit,
    reconstruct_governance_history,
    run_governance_auto_commit,
    save_git_governance_config,
)
from governed_platform.governance.log_integrity import (
    LOG_MODE_HASH_CHAIN,
    LOG_MODE_PLAIN,
    normalize_log_mode,
    verify_log_integrity,
)
from governed_platform.governance.state_manager import StateManager
from governed_platform.governance.residual_risks import (
    add_risks,
    get_risk,
    list_risks,
    load_register,
    normalize_risk_input,
    normalize_risk_status,
    risk_summary,
    update_risk_status,
)
from governed_platform.governance.break_fix import (
    break_fix_summary,
    get_break_fix,
    list_break_fixes,
    note_break_fix,
    open_break_fix,
    reject_break_fix,
    resolve_break_fix,
    start_break_fix,
)
from governed_platform.governance.schema_registry import SchemaRegistry
from governed_platform.governance.status import (
    PACKET_STATUS_VALUES,
    normalize_packet_status,
    normalize_packet_status_map,
    normalize_runtime_status,
)
from governed_platform.governance.supervisor import (
    ENFORCEMENT_ADVISORY,
    ENFORCEMENT_DISABLED,
    ENFORCEMENT_MODES,
    ENFORCEMENT_STRICT,
    default_agent_registry,
    load_agent_registry,
    normalize_enforcement_mode,
    save_agent_registry,
)
from planner import (
    build_definition as build_planned_definition,
    collect_import_review_warnings,
    import_markdown_to_spec,
    load_plan_spec,
    prompt_plan_spec,
    validate_definition as validate_planned_definition,
    write_definition as write_planned_definition,
)
from paths import (
    DEFAULT_PROJECT_ID,
    PROJECTS_DIR,
    get_active_project_id,
    normalize_project_id,
    resolve_runtime_paths,
    set_active_project_id,
)

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

# Global flags
JSON_OUTPUT = False
PACKET_SCHEMA_PATH = GOV / "packet-schema.json"
WBS_SCHEMA_PATH = GOV / "wbs-schema.json"
SCHEMA_REGISTRY_PATH = GOV / "schema-registry.json"
AGENTS_REGISTRY_PATH = GOV / "agents.json"
GIT_GOVERNANCE_PATH = GOV / "git-governance.json"
WBS_MUTATION_POLICY_PATH = GOV / "wbs-mutation-policy.json"
WBS_APPROVAL_ENV = "WBS_CHANGE_APPROVAL"
WBS_APPROVAL_FLAG = "--wbs-approval"
DEFAULT_WBS_MUTATION_POLICY = {
    "mode": "strict",
    "approval_prefix": "WBS-APPROVED:",
}

REQUIRED_PACKET_FIELDS = [
    "packet_id",
    "wbs_refs",
    "title",
    "purpose",
    "status",
    "owner",
    "priority",
    "preconditions",
    "required_inputs",
    "required_actions",
    "required_outputs",
    "validation_checks",
    "exit_criteria",
    "halt_conditions",
]

PACKET_PRIORITY_VALUES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
REQUIRED_DRIFT_SECTIONS = [
    "## Scope Reviewed",
    "## Expected vs Delivered",
    "## Drift Assessment",
    "## Evidence Reviewed",
    "## Residual Risks",
    "## Immediate Next Actions",
]
PRD_REQUIRED_SECTIONS = [
    "## Problem Statement",
    "## Goals",
    "## Non-Goals",
    "## Users and Use Cases",
    "## Scope",
    "## Requirements",
    "## Success Metrics",
    "## Risks and Assumptions",
    "## Open Questions",
    "## Acceptance Criteria",
]

MODE_PROFILES = {
    "speed": {
        "verify_evidence_on_done": False,
        "require_checklist_on_done": False,
        "stale_warn_factor": 1.5,
        "stale_critical_factor": 4.0,
    },
    "balanced": {
        "verify_evidence_on_done": False,
        "require_checklist_on_done": False,
        "stale_warn_factor": 1.0,
        "stale_critical_factor": 3.0,
    },
    "strict": {
        "verify_evidence_on_done": True,
        "require_checklist_on_done": False,
        "stale_warn_factor": 0.75,
        "stale_critical_factor": 2.0,
    },
}
DEFAULT_MODE_PROFILE = "balanced"
WBS_APPROVAL_TOKEN = ""

# ---------------------------------------------------------------------------
# Use-time runtime path accessors
# ---------------------------------------------------------------------------
# These helpers replace stale module-level path constants (WBS_DEF, WBS_STATE,
# RESIDUAL_RISK_REGISTER_PATH, BREAK_FIX_STORE_PATH).  Each call goes through
# resolve_runtime_paths() so the correct project-scoped path is always returned,
# even if apply_runtime_project() was invoked after module import.
#
# Convention:
#   - Reference these names directly in each function that needs a path.
#   - They are implemented as callables that always resolve at call-time.
# ---------------------------------------------------------------------------

def _wbs_def_path() -> "Path":
    """Return the active project's wbs.json path (resolved at call-time)."""
    return resolve_runtime_paths()["wbs_def"]


def _residual_risk_register_path() -> "Path":
    """Return the active project's residual-risk-register.json path (resolved at call-time)."""
    return resolve_runtime_paths()["residual_risk_register"]


def _break_fix_log_path() -> "Path":
    """Return the active project's break-fix-log.json path (resolved at call-time)."""
    return resolve_runtime_paths()["break_fix_log"]


# Module-level names used throughout this file.
# Each evaluates to the correct project-scoped path by calling the accessor.
# Using a _PathAccessor class so bare-name usage (e.g. WBS_DEF) acts like a Path
# for the common operations (exists, open, str, etc.) while resolving at call-time.

class _PathAccessor(os.PathLike):
    """Proxy that resolves a runtime path at call-time and delegates all Path/os operations.

    Implements os.PathLike so it is accepted by open(), Path(), os.fspath(),
    and all stdlib functions that consume path-like objects.
    The underlying Path is resolved fresh on every attribute access, which means
    project context set by apply_runtime_project() is always reflected correctly.
    """
    def __init__(self, resolver):
        self._resolver = resolver

    def __fspath__(self) -> str:
        return str(self._resolver())

    def __str__(self) -> str:
        return str(self._resolver())

    def __repr__(self) -> str:
        return repr(self._resolver())

    def __eq__(self, other) -> bool:
        p = self._resolver()
        if isinstance(other, _PathAccessor):
            return p == other._resolver()
        return p == other

    def __hash__(self):
        return hash(self._resolver())

    def __truediv__(self, other):
        return self._resolver() / other

    def __rtruediv__(self, other):
        return Path(other) / self._resolver()

    def __getattr__(self, name):
        # Delegate any unknown attribute to the resolved Path object.
        # This covers exists(), read_text(), write_text(), open(), unlink(),
        # resolve(), stat(), parent, name, suffix, etc.
        return getattr(self._resolver(), name)


WBS_DEF = _PathAccessor(_wbs_def_path)
RESIDUAL_RISK_REGISTER_PATH = _PathAccessor(_residual_risk_register_path)
BREAK_FIX_STORE_PATH = _PathAccessor(_break_fix_log_path)


def apply_runtime_project(project_id: str, persist: bool = False) -> str:
    """Apply project context to runtime path globals for this CLI process.

    Path resolution strategy: all governance paths (WBS_STATE, WBS_DEF, etc.)
    are resolved at use-time by calling resolve_runtime_paths() inside each
    function that needs them.  This function writes the selected project id
    into os.environ["WBS_PROJECT"] so that any subsequent resolve_runtime_paths()
    call automatically picks up the correct project-scoped paths.  No module-level
    path constants are used; this avoids stale-path bugs when project context
    changes mid-process.
    """
    pid = normalize_project_id(project_id)
    if persist:
        pid = set_active_project_id(pid)
    os.environ["WBS_PROJECT"] = pid
    # resolve_runtime_paths is called here to validate the project paths exist;
    # the return value is intentionally unused — callers resolve at use-time.
    resolve_runtime_paths(pid)
    return pid

PACKET_PRESETS = {
    "api-change": {
        "scope_template": "Implement API contract change for {title}. Output: API code + tests + docs.",
    },
    "doc-only": {
        "scope_template": "Implement documentation-only update for {title}. Output: updated docs + links + validation notes.",
    },
    "refactor": {
        "scope_template": "Implement refactor for {title}. Output: code changes preserving behavior + regression checks.",
    },
    "break-fix": {
        "scope_template": "Implement break-fix for {title}. Output: root cause note + fix + evidence and verification paths.",
    },
}

ERROR_HINTS = [
    ("not found", "WBS-E-001", "Run `python3 .governance/wbs_cli.py status` to confirm packet/area ids."),
    ("not pending", "WBS-E-002", "Use `status` to inspect owner/state, then `reset` if appropriate."),
    ("dependencies", "WBS-E-003", "Run `ready` to see claimable packets and complete upstream dependencies."),
    ("blocked by", "WBS-E-003", "Run `ready` to see claimable packets and complete upstream dependencies."),
    ("not in_progress", "WBS-E-004", "Claim the packet first, then mark done/fail from in_progress state."),
    ("incomplete packets", "WBS-E-301", "Complete all packets in the level-2 area before running `closeout-l2`."),
    ("missing required section", "WBS-E-302", "Use `docs/drift-assessment-template.md` and include all required headers."),
    ("assessment file not found", "WBS-E-303", "Verify the drift assessment path exists and retry."),
    ("schema registry", "WBS-E-103", "Check `.governance/schema-registry.json` and registered schema paths."),
]


def output_json(data):
    """Output as JSON if --json flag set."""
    if JSON_OUTPUT:
        print(json.dumps(data, indent=2, default=str))
        return True
    return False


def _load_wbs_mutation_policy() -> dict:
    policy = dict(DEFAULT_WBS_MUTATION_POLICY)
    if not WBS_MUTATION_POLICY_PATH.exists():
        return policy
    try:
        loaded = json.loads(WBS_MUTATION_POLICY_PATH.read_text())
    except Exception:
        return policy
    if isinstance(loaded, dict):
        policy.update({k: v for k, v in loaded.items() if v is not None})
    policy["mode"] = str(policy.get("mode") or "strict").strip().lower()
    if policy["mode"] not in {"strict", "advisory", "disabled"}:
        policy["mode"] = "strict"
    policy["approval_prefix"] = str(policy.get("approval_prefix") or "WBS-APPROVED:")
    return policy


def _approval_candidate(explicit_token: str = "") -> str:
    token = str(explicit_token or "").strip()
    if token:
        return token
    if str(WBS_APPROVAL_TOKEN or "").strip():
        return str(WBS_APPROVAL_TOKEN).strip()
    return str(os.environ.get(WBS_APPROVAL_ENV, "")).strip()


def _approval_token_valid(token: str, prefix: str) -> bool:
    if not token or not prefix or not token.startswith(prefix):
        return False
    tail = token[len(prefix):].strip()
    return bool(re.fullmatch(r"[A-Za-z0-9._:/-]{3,128}", tail))


def require_wbs_mutation_approval(action: str, explicit_token: str = "") -> bool:
    """Enforce approval policy for structural WBS mutations."""
    policy = _load_wbs_mutation_policy()
    mode = policy.get("mode", "strict")
    if mode == "disabled":
        return True
    prefix = str(policy.get("approval_prefix") or "WBS-APPROVED:")
    token = _approval_candidate(explicit_token)
    if _approval_token_valid(token, prefix):
        return True
    message = (
        f"WBS mutation approval required for {action}. "
        f"Provide {WBS_APPROVAL_FLAG} {prefix}<change-id> or set {WBS_APPROVAL_ENV}."
    )
    if mode == "advisory":
        print(yellow(message))
        return True
    print(red(message))
    return False


def _format_error(message: str) -> str:
    """Attach stable error code and action guidance to known failure patterns."""
    text = (message or "").strip()
    lower = text.lower()
    for pattern, code, hint in ERROR_HINTS:
        if pattern in lower:
            return f"[{code}] {text}\nAction: {hint}"
    return text


def enforce_schema_contracts(required_schemas=None) -> tuple:
    """Enforce schema registry contract at runtime boundaries."""
    required_schemas = required_schemas or [("packet", "1.0")]
    if not SCHEMA_REGISTRY_PATH.exists():
        return False, f"Schema registry missing: {SCHEMA_REGISTRY_PATH}"
    try:
        reg = SchemaRegistry.from_registry_file(SCHEMA_REGISTRY_PATH, root=GOV.parent)
    except Exception as e:
        return False, f"Schema registry load failed: {e}"

    for schema_name, expected_version in required_schemas:
        try:
            schema_ok = reg.validate_version(schema_name, expected_version)
            schema_record = reg.get(schema_name)
        except Exception as e:
            return False, f"Schema registry invalid: {e}"
        if not schema_ok:
            return False, f"Schema registry version mismatch for {schema_name}"
        if not schema_record.path.exists():
            return False, f"Registered schema not found ({schema_name}): {schema_record.path}"
    return True, "ok"


def ensure_state_shape(state: dict) -> dict:
    """Ensure optional top-level state keys exist."""
    state.setdefault("packets", {})
    state.setdefault("log", [])
    state.setdefault("area_closeouts", {})
    state.setdefault("log_integrity_mode", LOG_MODE_PLAIN)
    state.setdefault("operator_mode", DEFAULT_MODE_PROFILE)
    state.setdefault("mode_overrides", {})
    if str(state.get("operator_mode", "")).strip().lower() not in MODE_PROFILES:
        state["operator_mode"] = DEFAULT_MODE_PROFILE
    state["log_integrity_mode"] = normalize_log_mode(state.get("log_integrity_mode"))
    return normalize_packet_status_map(state)


def get_mode_config(state: dict = None) -> dict:
    """Return effective mode profile config merged with optional overrides."""
    state_obj = ensure_state_shape(state or load_state())
    mode = str(state_obj.get("operator_mode") or DEFAULT_MODE_PROFILE).strip().lower()
    base = dict(MODE_PROFILES.get(mode, MODE_PROFILES[DEFAULT_MODE_PROFILE]))
    overrides = state_obj.get("mode_overrides", {})
    if isinstance(overrides, dict):
        base.update({k: v for k, v in overrides.items() if k in base})
    base["mode"] = mode
    return base


def save_state(state: dict):
    """Save state with cross-platform lock + atomic replace.

    Resolves the state path at call-time via resolve_runtime_paths() so that
    the correct project-scoped path is always used, even if apply_runtime_project()
    was called after module import.
    """
    atomic_write_json(resolve_runtime_paths()["wbs_state"], state)


def governance_engine() -> GovernanceEngine:
    """Build governance engine from current definition and state path.

    Resolves paths at call-time so project context set by apply_runtime_project()
    is respected.
    """
    definition = load_definition()
    sm = StateManager(resolve_runtime_paths()["wbs_state"])
    state = sm.load()
    changed = False
    # Ensure all packets in definition exist in state
    for packet in definition.get("packets", []):
        pid = packet["id"]
        state.setdefault("packets", {})
        if pid not in state["packets"]:
            state["packets"][pid] = {
                "status": "pending",
                "assigned_to": None,
                "started_at": None,
                "completed_at": None,
                "notes": None,
            }
            changed = True
    if changed:
        sm.save(state)
    return GovernanceEngine(definition, sm)


def log_event(state: dict, packet_id: str, event: str, agent: str = None, notes: str = None):
    """Add entry to completion log."""
    state["log"].append({
        "packet_id": packet_id,
        "event": event,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
        "notes": notes
    })


def detect_circular(dependencies: dict) -> Optional[list]:
    """Detect circular dependencies. Returns cycle path if found."""
    visited, rec_stack, path = set(), set(), []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                result = dfs(neighbor)
                if result:
                    return result
            elif neighbor in rec_stack:
                return path[path.index(neighbor):] + [neighbor]
        path.pop()
        rec_stack.remove(node)
        return None

    for node in dependencies:
        if node not in visited:
            result = dfs(node)
            if result:
                return result
    return None


def cmd_init(wbs_path: str, approval_token: str = "") -> bool:
    """Initialize state from WBS definition."""
    ok, msg = enforce_schema_contracts()
    if not ok:
        print(red(msg))
        return False
    try:
        with open(wbs_path) as f:
            definition = json.load(f)
    except FileNotFoundError:
        print(red(f"File not found: {wbs_path}"))
        return False
    except json.JSONDecodeError as e:
        print(red(f"Invalid JSON: {e}"))
        return False

    # Check for circular dependencies
    deps = definition.get("dependencies", {})
    cycle = detect_circular(deps)
    if cycle:
        print(red(f"Circular dependency: {' -> '.join(cycle)}"))
        return False

    # Copy definition to .governance/wbs.json if different path
    runtime = resolve_runtime_paths()
    wbs_def = runtime["wbs_def"]
    if Path(wbs_path).resolve() != wbs_def.resolve():
        policy = _load_wbs_mutation_policy()
        if bool(policy.get("enforce_init_replace", False)):
            if not require_wbs_mutation_approval("init_replace", approval_token):
                return False
        with open(wbs_def, "w") as f:
            json.dump(definition, f, indent=2)
            f.write("\n")

    # Initialize or update state
    state = ensure_state_shape(load_state())

    # Preserve existing packet states, add new ones
    for packet in definition.get("packets", []):
        pid = packet["id"]
        if pid not in state["packets"]:
            state["packets"][pid] = {
                "status": "pending",
                "assigned_to": None,
                "started_at": None,
                "completed_at": None,
                "notes": None
            }

    save_state(state)
    print(green(f"Initialized from {wbs_path}"))
    return True


def cmd_init_wizard() -> bool:
    """Interactive setup wizard."""
    print(bold("WBS Setup Wizard"))
    print()

    name = input("Project name [My Project]: ").strip() or "My Project"

    print("\nStarting template:")
    print("  1) Critical app delivery (20 packets)")
    print("  2) Feature development (9 packets)")
    print("  3) Bug fix campaign (7 packets)")
    print("  4) Blank (you'll add packets)")

    choice = input("Choice [1]: ").strip() or "1"

    templates = {
        "1": GOV.parent / "templates" / "wbs-critical-delivery.json",
        "2": GOV.parent / "templates" / "wbs-feature.json",
        "3": GOV.parent / "templates" / "wbs-bugfix.json",
        "4": GOV / "wbs-template.json"
    }

    source = templates.get(choice, templates["1"])

    # Handle missing template file
    try:
        with open(source) as f:
            definition = json.load(f)
    except FileNotFoundError:
        # Fall back to blank template
        definition = {
            "metadata": {"project_name": name, "version": "1.0"},
            "work_areas": [{"id": "MAIN", "title": "Main Work"}],
            "packets": [],
            "dependencies": {}
        }
    except json.JSONDecodeError as e:
        print(red(f"Invalid template JSON: {e}"))
        return False

    import os
    definition["metadata"]["project_name"] = name
    definition["metadata"]["approved_by"] = os.environ.get("USER", "wizard")
    definition["metadata"]["approved_at"] = datetime.now().isoformat()

    runtime = resolve_runtime_paths()
    wbs_def = runtime["wbs_def"]
    with open(wbs_def, "w") as f:
        json.dump(definition, f, indent=2)
        f.write("\n")

    print(green(f"\nCreated {wbs_def}"))
    return cmd_init(str(wbs_def), approval_token=WBS_APPROVAL_TOKEN)


def cmd_plan(
    from_json: str = "",
    import_markdown: str = "",
    output_path: str = "",
    apply: bool = False,
    allow_ambiguous: bool = False,
) -> bool:
    """Guided WBS planner workflow with optional non-interactive input."""
    ok, msg = enforce_schema_contracts([("wbs_definition", "1.0")])
    if not ok:
        print(red(msg))
        return False

    try:
        if from_json and import_markdown:
            print(red("Use either --from-json or --import-markdown, not both."))
            return False
        if from_json:
            spec = load_plan_spec(Path(from_json))
        elif import_markdown:
            spec = import_markdown_to_spec(Path(import_markdown))
        else:
            spec = prompt_plan_spec(default_actor=os.environ.get("USER", "planner"))
        if import_markdown:
            planning_source = "import_markdown"
        elif from_json:
            planning_source = "from_json"
        else:
            planning_source = "interactive"
        spec.setdefault("planning_source", planning_source)
        spec.setdefault("planning_generated_at", datetime.now().isoformat())
        definition = build_planned_definition(spec)
        errors = validate_planned_definition(definition)
        if errors:
            print(red("Planner validation failed:"))
            for err in errors:
                print(f"  - {err}")
            return False

        import_warnings = collect_import_review_warnings(definition)
        if import_warnings:
            print(yellow("Import warnings (manual review required):"))
            for warning in import_warnings:
                print(f"  - {warning}")
            if apply and not allow_ambiguous:
                print(
                    red(
                        "Planner import includes ambiguous mappings; export and correct the draft first, "
                        "or rerun with --allow-ambiguous to force apply."
                    )
                )
                return False

        if output_path:
            target = Path(output_path).expanduser()
            if not target.is_absolute():
                target = GOV.parent / target
        elif apply:
            runtime = resolve_runtime_paths()
            target = runtime["wbs_def"]
        else:
            target = GOV / "wbs-planned.json"

        written = write_planned_definition(definition, target)
        print(green(f"Planner exported WBS: {written}"))

        if apply:
            return cmd_init(str(written), approval_token=WBS_APPROVAL_TOKEN)
        return True
    except FileNotFoundError as e:
        print(red(f"Planner input not found: {e}"))
        return False
    except json.JSONDecodeError as e:
        print(red(f"Planner input is not valid JSON: {e}"))
        return False
    except ValueError as e:
        print(red(f"Planner input error: {e}"))
        return False


def _slug_filename(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "-", str(value or "").strip().lower())
    token = re.sub(r"-{2,}", "-", token).strip("-")
    return token or "prd"


def _split_pipe_csv_lines(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    if "\n" in text:
        return [line.strip("-* ").strip() for line in text.splitlines() if line.strip("-* ").strip()]
    normalized = text.replace("|", ",")
    return [token.strip() for token in normalized.split(",") if token.strip()]


def _load_prd_spec(path: Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text())
    if not isinstance(payload, dict):
        raise ValueError("PRD spec must be a JSON object")
    return payload


def _ask_prd(prompt: str, default: str = "", required: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if not value:
            value = default
        if required and not value:
            print("Value required.")
            continue
        return value


def _render_prd_markdown(spec: Dict[str, Any]) -> str:
    project_name = str(spec.get("project_name") or "Product").strip()
    owner = str(spec.get("owner") or spec.get("approved_by") or os.environ.get("USER", "planner")).strip()
    date = str(spec.get("date") or datetime.now().date().isoformat()).strip()
    status = str(spec.get("status") or "draft").strip()
    goals = _split_pipe_csv_lines(spec.get("goals"))
    non_goals = _split_pipe_csv_lines(spec.get("non_goals"))
    users = _split_pipe_csv_lines(spec.get("users"))
    in_scope = _split_pipe_csv_lines(spec.get("in_scope"))
    out_scope = _split_pipe_csv_lines(spec.get("out_of_scope"))
    functional = _split_pipe_csv_lines(spec.get("functional_requirements"))
    non_functional = _split_pipe_csv_lines(spec.get("non_functional_requirements"))
    metrics = _split_pipe_csv_lines(spec.get("success_metrics"))
    risks = _split_pipe_csv_lines(spec.get("risks_assumptions"))
    questions = _split_pipe_csv_lines(spec.get("open_questions"))
    acceptance = _split_pipe_csv_lines(spec.get("acceptance_criteria"))
    constraints = _split_pipe_csv_lines(spec.get("constraints"))

    def bullets(items: List[str], fallback: str) -> str:
        if not items:
            return f"- {fallback}"
        return "\n".join(f"- {item}" for item in items)

    problem = str(spec.get("problem_statement") or "Describe the user or business problem being solved.").strip()
    use_cases = str(spec.get("use_cases") or "Describe primary use cases and flows.").strip()
    delivery_plan = str(spec.get("delivery_plan") or "Outline milestones and release sequencing.").strip()

    return "\n".join(
        [
            f"# {project_name} PRD",
            "",
            "## Document Control",
            f"- Owner: {owner}",
            f"- Date: {date}",
            f"- Status: {status}",
            "",
            "## Problem Statement",
            problem,
            "",
            "## Goals",
            bullets(goals, "TBD"),
            "",
            "## Non-Goals",
            bullets(non_goals, "TBD"),
            "",
            "## Users and Use Cases",
            "### Users",
            bullets(users, "TBD"),
            "",
            "### Use Cases",
            use_cases,
            "",
            "## Scope",
            "### In Scope",
            bullets(in_scope, "TBD"),
            "",
            "### Out of Scope",
            bullets(out_scope, "TBD"),
            "",
            "## Requirements",
            "### Functional Requirements",
            bullets(functional, "TBD"),
            "",
            "### Non-Functional Requirements",
            bullets(non_functional, "TBD"),
            "",
            "### Constraints",
            bullets(constraints, "TBD"),
            "",
            "## Success Metrics",
            bullets(metrics, "TBD"),
            "",
            "## Risks and Assumptions",
            bullets(risks, "TBD"),
            "",
            "## Open Questions",
            bullets(questions, "TBD"),
            "",
            "## Acceptance Criteria",
            bullets(acceptance, "TBD"),
            "",
            "## Delivery Plan",
            delivery_plan,
            "",
            "## Traceability",
            "- Constitution: `constitution.md`",
            "- Governance contract: `AGENTS.md`",
            "- Related agent docs: `CLAUDE.md`, `GEMINI.md`, `codex.md`",
            "",
        ]
    ) + "\n"


def _prompt_prd_spec(default_actor: str = "") -> Dict[str, Any]:
    print("PRD Ideation (optional)")
    print("Create a PRD markdown draft. You can refine it manually before conversion to WBS.")
    print("")
    actor = (default_actor or os.environ.get("USER", "planner")).strip() or "planner"
    project_name = _ask_prd("Project/Product name", required=True)
    owner = _ask_prd("Owner", default=actor, required=True)
    problem_statement = _ask_prd("Problem statement", required=True)
    goals = _ask_prd("Goals (comma-separated)")
    users = _ask_prd("Users/personas (comma-separated)")
    functional = _ask_prd("Functional requirements (comma-separated)")
    acceptance = _ask_prd("Acceptance criteria (comma-separated)")
    return {
        "project_name": project_name,
        "owner": owner,
        "problem_statement": problem_statement,
        "goals": goals,
        "users": users,
        "functional_requirements": functional,
        "acceptance_criteria": acceptance,
    }


def cmd_prd(
    from_json: str = "",
    output_path: str = "",
    to_wbs: str = "",
    apply: bool = False,
    allow_ambiguous: bool = False,
) -> bool:
    """Optional PRD ideation mode with optional PRD->WBS conversion."""
    try:
        if from_json:
            spec = _load_prd_spec(Path(from_json))
        else:
            spec = _prompt_prd_spec(default_actor=os.environ.get("USER", "planner"))

        project_name = str(spec.get("project_name") or "product").strip()
        default_prd = GOV.parent / "docs" / "prd" / f"{_slug_filename(project_name)}-prd.md"
        prd_path = Path(output_path).expanduser() if output_path else default_prd
        if not prd_path.is_absolute():
            prd_path = GOV.parent / prd_path
        prd_path.parent.mkdir(parents=True, exist_ok=True)
        markdown = _render_prd_markdown(spec)
        prd_path.write_text(markdown)
        print(green(f"PRD exported: {prd_path}"))

        missing = [section for section in PRD_REQUIRED_SECTIONS if section not in markdown]
        if missing:
            print(yellow(f"PRD warning: missing sections: {', '.join(missing)}"))

        if not to_wbs and not apply:
            return True

        import_spec = import_markdown_to_spec(prd_path)
        import_spec.setdefault("project_name", project_name)
        import_spec.setdefault("approved_by", str(spec.get("owner") or os.environ.get("USER", "planner")).strip())
        import_spec.setdefault("planning_source", "prd_markdown")
        import_spec.setdefault("planning_generated_at", datetime.now().isoformat())

        definition = build_planned_definition(import_spec)
        errors = validate_planned_definition(definition)
        if errors:
            print(red("PRD->WBS planner validation failed:"))
            for err in errors:
                print(f"  - {err}")
            return False

        import_warnings = collect_import_review_warnings(definition)
        if import_warnings:
            print(yellow("PRD->WBS import warnings (manual review required):"))
            for warning in import_warnings:
                print(f"  - {warning}")
            if apply and not allow_ambiguous:
                print(
                    red(
                        "PRD import includes ambiguous mappings; review exported WBS first, "
                        "or rerun with --allow-ambiguous to force apply."
                    )
                )
                return False

        if to_wbs:
            wbs_target = Path(to_wbs).expanduser()
            if not wbs_target.is_absolute():
                wbs_target = GOV.parent / wbs_target
        elif apply:
            runtime = resolve_runtime_paths()
            wbs_target = runtime["wbs_def"]
        else:
            wbs_target = GOV / "wbs-from-prd.json"

        written = write_planned_definition(definition, wbs_target)
        print(green(f"PRD->WBS exported: {written}"))

        if apply:
            return cmd_init(str(written), approval_token=WBS_APPROVAL_TOKEN)
        return True
    except FileNotFoundError as e:
        print(red(f"PRD input not found: {e}"))
        return False
    except json.JSONDecodeError as e:
        print(red(f"PRD input is not valid JSON: {e}"))
        return False
    except ValueError as e:
        print(red(f"PRD input error: {e}"))
        return False


def cmd_git_protocol(parse_path: str = "") -> bool:
    """Show or parse structured governance commit protocol."""
    if parse_path:
        try:
            payload = Path(parse_path).read_text()
        except FileNotFoundError:
            print(red(f"File not found: {parse_path}"))
            return False
        except Exception as e:
            print(red(f"Failed to read file: {e}"))
            return False
        try:
            parsed = parse_governance_commit(payload)
        except ValueError as e:
            print(red(f"Protocol parse failed: {e}"))
            return False
        if output_json(parsed):
            return True
        print(green("Protocol parse OK"))
        print(f"  packet: {parsed['packet_id']}")
        print(f"  action: {parsed['action']}")
        print(f"  actor:  {parsed['actor']}")
        print(f"  event:  {parsed['event_id']}")
        print(f"  proto:  {parsed['protocol_version']}")
        return True

    sample = format_governance_commit(
        packet_id="IMP-001",
        action="claim",
        actor="codex-lead",
        event_id="evt-00000001",
        timestamp="2026-02-17T00:00:00+00:00",
        protocol_version=GIT_PROTOCOL_VERSION,
    )

    payload = {
        "protocol_version": GIT_PROTOCOL_VERSION,
        "required_trailers": list(GIT_PROTOCOL_REQUIRED_TRAILERS),
        "subject_format": "substrate(packet=<PACKET_ID>,action=<ACTION>,actor=<ACTOR>)",
        "sample": sample,
    }
    if output_json(payload):
        return True

    print("Git Governance Commit Protocol")
    print("-" * 60)
    print(f"Protocol: {GIT_PROTOCOL_VERSION}")
    print("Subject:")
    print("  substrate(packet=<PACKET_ID>,action=<ACTION>,actor=<ACTOR>)")
    print("Required trailers:")
    for key in GIT_PROTOCOL_REQUIRED_TRAILERS:
        print(f"  - {key}")
    print()
    print("Sample commit message:")
    print(sample)
    return True


def _ensure_git_governance_exists() -> dict:
    config = load_git_governance_config(GIT_GOVERNANCE_PATH)
    if not GIT_GOVERNANCE_PATH.exists():
        save_git_governance_config(GIT_GOVERNANCE_PATH, config)
    return config


def cmd_git_governance() -> bool:
    """Show effective git-native governance configuration."""
    config = _ensure_git_governance_exists()
    if output_json(config):
        return True
    print(f"\nGit Governance Config ({GIT_GOVERNANCE_PATH})")
    print("-" * 60)
    print(f"Mode: {config.get('mode')}")
    print(f"Auto-commit: {bool(config.get('auto_commit'))}")
    print(f"Protocol version: {config.get('commit_protocol_version')}")
    print(f"Stage files: {', '.join(config.get('stage_files', []))}")
    return True


def cmd_git_governance_mode(mode: str) -> bool:
    """Set git-native governance mode."""
    token = str(mode or "").strip().lower()
    if token not in GIT_MODES:
        print(red(f"Invalid mode: {mode}. Use one of: {', '.join(sorted(GIT_MODES))}"))
        return False
    config = _ensure_git_governance_exists()
    config["mode"] = token
    save_git_governance_config(GIT_GOVERNANCE_PATH, config)
    print(green(f"Git governance mode set: {token}"))
    return True


def cmd_git_governance_autocommit(value: str) -> bool:
    """Set git-native governance auto-commit toggle."""
    token = str(value or "").strip().lower()
    enabled = token in {"on", "true", "1", "yes", "enable", "enabled"}
    disabled = token in {"off", "false", "0", "no", "disable", "disabled"}
    if not (enabled or disabled):
        print(red("Invalid value. Use one of: on|off"))
        return False
    config = _ensure_git_governance_exists()
    config["auto_commit"] = bool(enabled)
    save_git_governance_config(GIT_GOVERNANCE_PATH, config)
    state_label = "enabled" if enabled else "disabled"
    print(green(f"Git governance auto-commit {state_label}"))
    return True


def cmd_git_verify_ledger(strict: bool = False) -> bool:
    """Verify git linkage integrity recorded on lifecycle log entries."""
    state = ensure_state_shape(load_state())
    entries = state.get("log", [])
    issues = []
    warnings = []

    repo_ok, repo_reason = ensure_git_worktree(GOV.parent)

    checked = 0
    linked = 0
    warning_count = 0
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        has_git_fields = any(str(key).startswith("git_") for key in entry.keys())
        if not has_git_fields:
            continue
        checked += 1
        status = str(entry.get("git_link_status") or "").strip().lower()
        if status == "linked":
            linked += 1
            for key in ("git_commit", "git_event_id", "git_action", "git_actor"):
                if not str(entry.get(key) or "").strip():
                    issues.append(f"log[{idx}] missing required git linkage field: {key}")
            commit_hash = str(entry.get("git_commit") or "").strip()
            if commit_hash and not repo_ok:
                warnings.append(f"log[{idx}] linked commit cannot be verified: {repo_reason}")
            elif commit_hash:
                ok, parsed, reason = parse_governance_commit_from_hash(GOV.parent, commit_hash)
                if not ok:
                    issues.append(f"log[{idx}] commit parse failed: {reason}")
                else:
                    if parsed.get("packet_id") != str(entry.get("packet_id") or "").strip():
                        issues.append(f"log[{idx}] packet mismatch between log and commit trailer")
                    if parsed.get("action") != str(entry.get("git_action") or "").strip():
                        issues.append(f"log[{idx}] action mismatch between log and commit trailer")
                    if parsed.get("actor") != str(entry.get("git_actor") or "").strip():
                        issues.append(f"log[{idx}] actor mismatch between log and commit trailer")
                    if parsed.get("event_id") != str(entry.get("git_event_id") or "").strip():
                        issues.append(f"log[{idx}] event_id mismatch between log and commit trailer")
        elif status == "warning":
            warning_count += 1
            detail = str(entry.get("git_link_error") or "").strip()
            if detail:
                warnings.append(f"log[{idx}] advisory warning: {detail}")
            else:
                warnings.append(f"log[{idx}] warning status missing git_link_error detail")
        else:
            warnings.append(f"log[{idx}] has git fields with unsupported status '{status or '<empty>'}'")

    valid = len(issues) == 0 and (not strict or (warning_count == 0 and len(warnings) == 0))
    payload = {
        "valid": valid,
        "strict": strict,
        "checked_entries": checked,
        "linked_entries": linked,
        "warning_entries": warning_count,
        "issues": issues,
        "warnings": warnings,
    }
    if output_json(payload):
        return valid

    if valid:
        print(green("Git ledger verification passed"))
    else:
        print(red("Git ledger verification failed"))
    print(
        f"checked={checked} linked={linked} warning_entries={warning_count} "
        f"issues={len(issues)} warnings={len(warnings)} strict={strict}"
    )
    for issue in issues:
        print(red(f"  - {issue}"))
    for warning in warnings:
        print(yellow(f"  - {warning}"))
    return valid


def cmd_git_export_ledger(out_path: str) -> bool:
    """Export git-linked governance log entries."""
    state = ensure_state_shape(load_state())
    entries = []
    for entry in state.get("log", []):
        if not isinstance(entry, dict):
            continue
        if not any(str(key).startswith("git_") for key in entry.keys()):
            continue
        entries.append(
            {
                "packet_id": entry.get("packet_id"),
                "event": entry.get("event"),
                "agent": entry.get("agent"),
                "timestamp": entry.get("timestamp"),
                "git_link_status": entry.get("git_link_status"),
                "git_mode": entry.get("git_mode"),
                "git_commit": entry.get("git_commit"),
                "git_event_id": entry.get("git_event_id"),
                "git_action": entry.get("git_action"),
                "git_actor": entry.get("git_actor"),
                "git_closeout_tag": entry.get("git_closeout_tag"),
                "git_tag_error": entry.get("git_tag_error"),
                "git_link_error": entry.get("git_link_error"),
                "notes": entry.get("notes"),
            }
        )

    out = Path(out_path).expanduser()
    if not out.is_absolute():
        out = GOV.parent / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"entries": entries}, indent=2) + "\n")
    print(green(f"Git ledger exported: {out}"))
    return True


def cmd_git_reconstruct(limit: int = 500, out_path: str = "") -> bool:
    """Reconstruct governance transition records from git commit history."""
    ok, entries, reason = reconstruct_governance_history(GOV.parent, limit=limit)
    if not ok:
        print(red(f"Reconstruction failed: {reason}"))
        return False

    payload = {"count": len(entries), "entries": entries}
    if out_path:
        out = Path(out_path).expanduser()
        if not out.is_absolute():
            out = GOV.parent / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(green(f"Reconstructed governance history written: {out}"))
        return True

    if output_json(payload):
        return True

    print(green(f"Reconstructed governance records: {len(entries)}"))
    for row in entries[:20]:
        print(
            f"  {row.get('commit', '')[:12]} "
            f"{row.get('packet_id')} {row.get('action')} {row.get('actor')} "
            f"{row.get('event_id')}"
        )
    if len(entries) > 20:
        print(dim(f"... {len(entries) - 20} additional records omitted"))
    return True


def _packet_state(packet_id: str) -> dict:
    state = ensure_state_shape(load_state())
    return state.get("packets", {}).get(packet_id, {})


def cmd_git_branch_open(packet_id: str, agent: str, from_ref: str = "") -> bool:
    """Open an opt-in packet execution branch for the assigned owner."""
    pkt = _packet_state(packet_id)
    if not pkt:
        print(red(f"Packet {packet_id} not found"))
        return False
    status = normalize_runtime_status(pkt.get("status"))
    owner = str(pkt.get("assigned_to") or "")
    if status != "in_progress":
        print(red(f"Packet {packet_id} is {status}, not in_progress"))
        return False
    if owner and owner != agent:
        print(red(f"Packet {packet_id} assigned to {owner}, not {agent}"))
        return False

    ok, branch, reason = open_packet_branch(GOV.parent, packet_id=packet_id, agent=agent, from_ref=from_ref)
    if not ok:
        print(red(f"Branch open failed: {reason}"))
        return False
    active_ok, active_branch = current_branch(GOV.parent)
    active_label = active_branch if active_ok else branch
    print(green(f"Opened packet branch: {branch}"))
    print(dim(f"Active branch: {active_label}"))
    return True


def cmd_git_branch_close(packet_id: str, agent: str, base_branch: str = "main", delete_branch: bool = True) -> bool:
    """Close packet execution branch via fast-forward merge into base."""
    pkt = _packet_state(packet_id)
    if not pkt:
        print(red(f"Packet {packet_id} not found"))
        return False
    owner = str(pkt.get("assigned_to") or "")
    if owner and owner != agent:
        print(red(f"Packet {packet_id} assigned to {owner}, not {agent}"))
        return False

    ok, branch, reason = close_packet_branch(
        GOV.parent,
        packet_id=packet_id,
        agent=agent,
        base_branch=base_branch,
        delete_branch=delete_branch,
    )
    if not ok:
        print(red(f"Branch close failed: {reason}"))
        return False

    active_ok, active_branch = current_branch(GOV.parent)
    active_label = active_branch if active_ok else base_branch
    delete_label = "deleted" if delete_branch else "retained"
    print(green(f"Merged packet branch: {branch} -> {base_branch} ({delete_label})"))
    print(dim(f"Active branch: {active_label}"))
    return True


def _snapshot_state_bytes():
    wbs_state = resolve_runtime_paths()["wbs_state"]
    if wbs_state.exists():
        return wbs_state.read_bytes()
    return None


def _restore_state_bytes(snapshot) -> None:
    wbs_state = resolve_runtime_paths()["wbs_state"]
    if snapshot is None:
        wbs_state.unlink(missing_ok=True)
    else:
        wbs_state.write_bytes(snapshot)


def _annotate_git_link(
    packet_id: str,
    *,
    action: str,
    actor: str,
    mode: str,
    status: str,
    commit_hash: str = "",
    event_id: str = "",
    error: str = "",
) -> None:
    state = ensure_state_shape(load_state())
    entries = state.get("log", [])
    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        if entry.get("packet_id") != packet_id:
            continue
        if entry.get("git_link_status"):
            continue
        entry["git_link_status"] = status
        entry["git_mode"] = mode
        entry["git_action"] = action
        entry["git_actor"] = actor
        if commit_hash:
            entry["git_commit"] = commit_hash
        if event_id:
            entry["git_event_id"] = event_id
        if error:
            entry["git_link_error"] = error
        save_state(state)
        return


def _annotate_git_tag(packet_id: str, *, tag_name: str = "", error: str = "") -> None:
    state = ensure_state_shape(load_state())
    entries = state.get("log", [])
    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        if entry.get("packet_id") != packet_id:
            continue
        if tag_name:
            entry["git_closeout_tag"] = tag_name
        if error:
            entry["git_tag_error"] = error
        save_state(state)
        return


def _run_lifecycle_with_git(
    packet_id: str,
    action: str,
    agent: str,
    operation,
    *,
    area_id: str = "",
    closeout_area: str = "",
) -> tuple:
    config = load_git_governance_config(GIT_GOVERNANCE_PATH)
    mode = config.get("mode", GIT_MODE_DISABLED)
    auto_commit = bool(config.get("auto_commit"))

    snapshot = None
    if auto_commit and mode != GIT_MODE_DISABLED:
        snapshot = _snapshot_state_bytes()

    ok, msg = operation()
    if not ok:
        return ok, msg

    if not auto_commit or mode == GIT_MODE_DISABLED:
        return ok, msg

    commit_ok, commit_msg, commit_hash, git_event_id = run_governance_auto_commit(
        repo_root=GOV.parent,
        packet_id=packet_id,
        action=action,
        actor=agent or "system",
        stage_files=config.get("stage_files", []),
        protocol_version=config.get("commit_protocol_version", GIT_PROTOCOL_VERSION),
        area_id=area_id,
        closeout_area=closeout_area,
    )
    if commit_ok:
        _annotate_git_link(
            packet_id,
            action=action,
            actor=agent or "system",
            mode=mode,
            status="linked",
            commit_hash=commit_hash,
            event_id=git_event_id,
        )
        suffix = f" [git:{commit_hash[:12]}]"
        if action == "closeout-l2":
            tag_name = build_closeout_tag(closeout_area or area_id or packet_id)
            tag_ok, tag_reason = create_tag(GOV.parent, tag_name=tag_name, commit_hash=commit_hash)
            if tag_ok:
                _annotate_git_tag(packet_id, tag_name=tag_name)
                suffix += f" [tag:{tag_name}]"
            else:
                _annotate_git_tag(packet_id, error=tag_reason)
                suffix += f" (tag warning: {tag_reason})"
        return True, f"{msg}{suffix}"

    if mode == GIT_MODE_STRICT:
        _restore_state_bytes(snapshot)
        return (
            False,
            f"Git-native strict mode: auto-commit failed ({commit_msg}). Transition rolled back.",
        )

    _annotate_git_link(
        packet_id,
        action=action,
        actor=agent or "system",
        mode=mode,
        status="warning",
        error=commit_msg,
        event_id=git_event_id,
    )
    return True, f"{msg} (Git-native advisory warning: {commit_msg})"


def check_deps_met(packet_id: str, definition: dict, state: dict) -> tuple:
    """Check if all dependencies are done. Returns (ready, blocking_id)."""
    deps = definition.get("dependencies", {}).get(packet_id, [])
    for dep_id in deps:
        dep_state = state["packets"].get(dep_id, {})
        if normalize_runtime_status(dep_state.get("status")) != "done":
            return False, dep_id
    return True, None


def cmd_claim(packet_id: str, agent: str) -> bool:
    """Claim a packet."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="claim",
        agent=agent,
        operation=lambda: governance_engine().claim(packet_id, agent),
    )
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def _load_risk_entries_from_file(path: str) -> list:
    fp = Path(path).expanduser()
    if not fp.is_absolute():
        fp = GOV.parent / fp
    if not fp.exists():
        raise ValueError(f"Risk file not found: {path}")
    try:
        payload = json.loads(fp.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Risk file is not valid JSON: {e}")
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("risks"), list):
            return payload["risks"]
        return [payload]
    raise ValueError("Risk file must contain a risk object or risk array")


def _load_risk_entries_from_json(raw: str) -> list:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Risk JSON is invalid: {e}")
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("risks"), list):
            return payload["risks"]
        return [payload]
    raise ValueError("Risk JSON must be an object or array")


def _resolve_repo_path(path: str) -> Path:
    raw = Path(str(path or "").strip()).expanduser()
    if raw.is_absolute():
        return raw
    repo_root = GOV.parent.parent
    candidates = [
        (GOV.parent / raw).resolve(),
        (repo_root / raw).resolve(),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _extract_evidence_paths_from_text(text: str) -> list:
    token_re = re.compile(r"[A-Za-z0-9_./-]+\.[A-Za-z][A-Za-z0-9]{0,8}")
    out = []
    seen = set()
    for token in token_re.findall(str(text or "")):
        if token.startswith("http://") or token.startswith("https://"):
            continue
        cleaned = token.strip(" ,;:()[]{}<>\"'`")
        if not cleaned:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        out.append(cleaned)
    return out


def _verify_evidence_paths(paths: list) -> tuple:
    missing = []
    checked = []
    for rel in paths:
        target = _resolve_repo_path(rel)
        checked.append({"path": rel, "exists": target.exists()})
        if not target.exists():
            missing.append(rel)
    return (len(missing) == 0), missing, checked


def _validate_done_checklist(checklist_path: str) -> tuple:
    if not checklist_path:
        return True, "no checklist provided"
    target = _resolve_repo_path(checklist_path)
    if not target.exists():
        return False, f"Checklist file not found: {checklist_path}"
    text = target.read_text(errors="replace")
    if target.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as e:
            return False, f"Checklist JSON invalid: {e}"
        if not isinstance(payload, dict):
            return False, "Checklist JSON must be an object"
        required = payload.get("required_checks", [])
        checks = payload.get("checks", {})
        if required and not isinstance(required, list):
            return False, "checklist required_checks must be an array"
        if not isinstance(checks, dict):
            return False, "checklist checks must be an object"
        missing = []
        for key in required or checks.keys():
            if not bool(checks.get(key)):
                missing.append(str(key))
        if missing:
            return False, f"Checklist has incomplete checks: {', '.join(missing)}"
        return True, f"checklist passed ({checklist_path})"

    unchecked = re.findall(r"^\s*[-*]\s+\[\s\]\s+.+$", text, flags=re.MULTILINE)
    if unchecked:
        return False, f"Checklist has unchecked items ({len(unchecked)} pending)"
    checked = re.findall(r"^\s*[-*]\s+\[[xX]\]\s+.+$", text, flags=re.MULTILINE)
    if not checked:
        return False, "Checklist contains no completed checkbox items"
    return True, f"checklist passed ({checklist_path})"


def _annotate_done_risk_ack(
    packet_id: str,
    ack: str,
    risk_ids: list,
    *,
    risk_git_commit: str = "",
    risk_git_status: str = "",
    risk_git_error: str = "",
) -> None:
    state = ensure_state_shape(load_state())
    entries = state.get("log", [])
    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        if entry.get("packet_id") != packet_id:
            continue
        if entry.get("event") != "completed":
            continue
        entry["risk_ack"] = ack
        entry["risk_ids"] = list(risk_ids or [])
        if risk_git_commit:
            entry["risk_git_commit"] = risk_git_commit
        if risk_git_status:
            entry["risk_git_status"] = risk_git_status
        if risk_git_error:
            entry["risk_git_error"] = risk_git_error
        save_state(state)
        return


def _auto_commit_residual_risk_update(packet_id: str, actor: str) -> tuple:
    """Optionally persist residual-risk register updates under git governance protocol."""
    config = load_git_governance_config(GIT_GOVERNANCE_PATH)
    mode = config.get("mode", GIT_MODE_DISABLED)
    auto_commit = bool(config.get("auto_commit"))
    if not auto_commit or mode == GIT_MODE_DISABLED:
        return True, "", ""

    runtime = resolve_runtime_paths()
    risk_register_path = runtime["residual_risk_register"]
    
    ok, msg, commit_hash, _event_id = run_governance_auto_commit(
        repo_root=GOV.parent,
        packet_id=packet_id,
        action="note",
        actor=actor or "system",
        stage_files=[str(risk_register_path.relative_to(GOV.parent))],
        protocol_version=config.get("commit_protocol_version", GIT_PROTOCOL_VERSION),
    )
    if ok:
        return True, commit_hash, ""
    if mode == GIT_MODE_STRICT:
        return False, "", f"Git-native strict mode: residual risk auto-commit failed ({msg})"
    return True, "", f"Git-native advisory warning: residual risk auto-commit failed ({msg})"


def cmd_done(
    packet_id: str,
    agent: str,
    notes: str = "",
    *,
    risk_ack: str = "",
    risk_entries: list = None,
    checklist_path: str = "",
    verify_evidence: bool = False,
    require_checklist: bool = False,
) -> bool:
    """Mark packet done."""
    ack = str(risk_ack or "").strip().lower()
    risks = list(risk_entries or [])
    if ack not in {"none", "declared"}:
        print(red("Residual risk acknowledgement is required: use --risk none or provide --risk-file/--risk-json"))
        return False
    if ack == "none" and risks:
        print(red("Invalid risk input: --risk none cannot be combined with risk entries"))
        return False
    if ack == "declared" and not risks:
        print(red("Invalid risk input: --risk declared requires at least one risk entry"))
        return False

    mode_cfg = get_mode_config()
    if not verify_evidence and bool(mode_cfg.get("verify_evidence_on_done")):
        verify_evidence = True
    if not require_checklist and bool(mode_cfg.get("require_checklist_on_done")):
        require_checklist = True

    if require_checklist and not checklist_path:
        print(red("Checklist is required for done in current mode profile (use --checklist <path>)"))
        return False
    checklist_ok, checklist_msg = _validate_done_checklist(checklist_path)
    if not checklist_ok:
        print(red(checklist_msg))
        return False

    if verify_evidence:
        evidence_paths = _extract_evidence_paths_from_text(notes)
        if not evidence_paths:
            print(red("Evidence verification enabled but no file paths were found in notes"))
            return False
        paths_ok, missing_paths, _checked = _verify_evidence_paths(evidence_paths)
        if not paths_ok:
            print(red(f"Evidence path verification failed. Missing: {', '.join(missing_paths)}"))
            return False

    # Validate risk payload before lifecycle mutation so data errors fail fast.
    if risks:
        try:
            for raw in risks:
                normalize_risk_input(raw, packet_id=packet_id, actor=agent)
        except ValueError as e:
            print(red(str(e)))
            return False

    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="done",
        agent=agent,
        operation=lambda: governance_engine().done(packet_id, agent, notes),
    )
    risk_ids = []
    risk_git_commit = ""
    risk_git_error = ""
    if ok:
        if risks:
            try:
                risk_ids = add_risks(RESIDUAL_RISK_REGISTER_PATH, packet_id=packet_id, actor=agent, entries=risks)
            except Exception as e:
                msg = f"{msg} (risk register warning: {e})"
            if risk_ids:
                commit_ok, commit_hash, commit_error = _auto_commit_residual_risk_update(packet_id, agent)
                if not commit_ok:
                    msg = f"{msg} ({commit_error})"
                risk_git_commit = commit_hash
                risk_git_error = commit_error
        _annotate_done_risk_ack(
            packet_id,
            ack=ack,
            risk_ids=risk_ids,
            risk_git_commit=risk_git_commit,
            risk_git_status=("linked" if risk_git_commit else ("warning" if risk_git_error else "")),
            risk_git_error=risk_git_error,
        )
    if ok:
        if checklist_path:
            msg = f"{msg} ({checklist_msg})"
        if risk_ids:
            msg = f"{msg} (residual risks declared: {', '.join(risk_ids)})"
            if risk_git_commit:
                msg += f" [risk-git:{risk_git_commit[:12]}]"
            elif risk_git_error:
                msg += f" ({risk_git_error})"
        else:
            msg = f"{msg} (residual risk ack: none)"
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_note(packet_id: str, agent: str, notes: str) -> bool:
    """Update notes for any existing packet state."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="note",
        agent=agent,
        operation=lambda: governance_engine().note(packet_id, agent, notes),
    )
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_fail(packet_id: str, agent: str, reason: str = "") -> bool:
    """Mark packet failed and block downstream."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="fail",
        agent=agent,
        operation=lambda: governance_engine().fail(packet_id, agent, reason),
    )
    if ok:
        print(yellow(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_reset(packet_id: str) -> bool:
    """Reset packet to pending."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="reset",
        agent="system",
        operation=lambda: governance_engine().reset(packet_id),
    )
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_handover(
    packet_id: str,
    agent: str,
    reason: str,
    progress_notes: str = "",
    files_modified=None,
    remaining_work=None,
    to_agent: str = "",
) -> bool:
    """Create governed handover record for an in-progress packet."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="handover",
        agent=agent,
        operation=lambda: governance_engine().handover(
            packet_id=packet_id,
            agent=agent,
            reason=reason,
            progress_notes=progress_notes,
            files_modified=files_modified or [],
            remaining_work=remaining_work or [],
            to_agent=to_agent or None,
        ),
    )
    if ok:
        print(yellow(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_resume(packet_id: str, agent: str) -> bool:
    """Resume a packet from active handover and atomically assign owner."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=packet_id,
        action="resume",
        agent=agent,
        operation=lambda: governance_engine().resume(packet_id, agent),
    )
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_project_show() -> bool:
    active_project_id = get_active_project_id()
    runtime = resolve_runtime_paths(active_project_id)
    payload = {
        "active_project": active_project_id,
        "default_project": DEFAULT_PROJECT_ID,
        "current_project_file": str(runtime["current_project"]),
    }
    if output_json(payload):
        return True
    print(f"Active project: {active_project_id}")
    print(f"Default project: {DEFAULT_PROJECT_ID}")
    print(f"Current project file: {runtime['current_project']}")
    return True


def cmd_project_list() -> bool:
    projects = [DEFAULT_PROJECT_ID]
    active_project_id = get_active_project_id()
    if PROJECTS_DIR.exists():
        for item in sorted(PROJECTS_DIR.iterdir()):
            if item.is_dir():
                projects.append(normalize_project_id(item.name))
    projects = sorted(set(projects))
    payload = {"active_project": active_project_id, "projects": projects}
    if output_json(payload):
        return True
    print("Projects:")
    for project in projects:
        marker = "*" if project == active_project_id else " "
        print(f"{marker} {project}")
    return True


def cmd_project_set(project_id: str, approval_token: str = "") -> bool:
    if not require_wbs_mutation_approval("project-set", approval_token):
        return False
    pid = apply_runtime_project(project_id, persist=True)
    print(green(f"Active project set to {pid}"))
    return True


def cmd_project_create(project_id: str, source_path: str = "", approval_token: str = "") -> bool:
    if not require_wbs_mutation_approval("project-create", approval_token):
        return False
    pid = normalize_project_id(project_id)
    if pid == DEFAULT_PROJECT_ID:
        print(red("project-create: 'main' already exists as default project"))
        return False
    runtime = resolve_runtime_paths(pid)
    wbs_path = runtime["wbs_def"]
    state_path = runtime["wbs_state"]
    if wbs_path.exists():
        print(red(f"Project already exists: {pid} ({wbs_path})"))
        return False
    source_runtime = resolve_runtime_paths()
    source_wbs_def = source_runtime["wbs_def"]
    source = Path(source_path).expanduser() if source_path else source_wbs_def
    if not source.is_absolute():
        source = source.resolve()
    if not source.exists():
        print(red(f"Project source WBS not found: {source}"))
        return False
    try:
        definition = json.loads(source.read_text())
    except json.JSONDecodeError as e:
        print(red(f"Project source WBS invalid JSON: {e}"))
        return False
    errors = validate_planned_definition(definition)
    if errors:
        print(red("Project source WBS failed validation:"))
        for err in errors:
            print(f"  - {err}")
        return False
    wbs_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(wbs_path, definition)
    now = datetime.now().isoformat()
    state = {
        "version": "1.0",
        "created_at": now,
        "updated_at": now,
        "packets": {},
        "log": [],
        "area_closeouts": {},
        "log_integrity_mode": "plain",
        "operator_mode": DEFAULT_MODE_PROFILE,
        "mode_overrides": {},
    }
    for packet in definition.get("packets", []):
        pid_packet = packet["id"]
        state["packets"][pid_packet] = {
            "status": "pending",
            "assigned_to": None,
            "started_at": None,
            "completed_at": None,
            "notes": None,
        }
    atomic_write_json(state_path, state)
    print(green(f"Created project {pid}: {wbs_path}"))
    return True


def _ensure_agent_registry_exists() -> dict:
    registry = load_agent_registry(AGENTS_REGISTRY_PATH)
    if not AGENTS_REGISTRY_PATH.exists():
        save_agent_registry(registry, AGENTS_REGISTRY_PATH)
    return registry


def cmd_agent_list() -> bool:
    """List registered agents and capability enforcement mode."""
    registry = _ensure_agent_registry_exists()
    if output_json(registry):
        return True

    mode = normalize_enforcement_mode(registry.get("enforcement_mode"))
    print(f"\nAgent Registry ({AGENTS_REGISTRY_PATH})")
    print("-" * 60)
    print(f"Mode: {mode}")
    print(f"Taxonomy: {', '.join(registry.get('capability_taxonomy', []))}")
    print("-" * 60)
    agents = registry.get("agents", [])
    if not agents:
        print("No agents registered")
        return True
    for agent in agents:
        caps = ", ".join(agent.get("capabilities", [])) or "-"
        constraints = agent.get("constraints", {})
        print(f"{agent.get('id'):<16} {agent.get('type', '-'):<14} caps=[{caps}] constraints={constraints}")
    return True


def cmd_agent_mode(mode: str) -> bool:
    """Set capability enforcement mode (disabled|advisory|strict)."""
    raw = str(mode or "").strip().lower()
    if raw not in ENFORCEMENT_MODES:
        print(red(f"Invalid mode: {mode}. Use one of: {', '.join(sorted(ENFORCEMENT_MODES))}"))
        return False
    normalized = normalize_enforcement_mode(raw)
    registry = _ensure_agent_registry_exists()
    registry["enforcement_mode"] = normalized
    save_agent_registry(registry, AGENTS_REGISTRY_PATH)
    print(green(f"Agent capability enforcement mode set: {normalized}"))
    return True


def cmd_mode_profile(action: str = "show", mode: str = "") -> bool:
    """Show or set optional operator mode profile (speed|balanced|strict)."""
    state = ensure_state_shape(load_state())
    action_token = str(action or "show").strip().lower()
    if action_token == "show":
        cfg = get_mode_config(state)
        payload = {"mode": cfg.get("mode"), "config": cfg}
        if output_json(payload):
            return True
        print("\nOperator Mode Profile")
        print("-" * 40)
        print(f"mode: {cfg.get('mode')}")
        for key in sorted(k for k in cfg.keys() if k != "mode"):
            print(f"{key}: {cfg[key]}")
        print()
        return True

    if action_token == "set":
        mode_token = str(mode or "").strip().lower()
        if mode_token not in MODE_PROFILES:
            print(red(f"Invalid mode profile: {mode}. Use one of: {', '.join(sorted(MODE_PROFILES.keys()))}"))
            return False
        state["operator_mode"] = mode_token
        save_state(state)
        print(green(f"Operator mode profile set: {mode_token}"))
        return True

    print(red("Usage: wbs_cli.py mode-profile [show|set <speed|balanced|strict>]"))
    return False


def cmd_agent_register(agent_id: str, agent_type: str, capabilities_csv: str) -> bool:
    """Register or update an agent profile."""
    aid = (agent_id or "").strip()
    atype = (agent_type or "").strip()
    if not aid or not atype:
        print(red("agent_id and agent_type are required"))
        return False

    caps = [cap.strip() for cap in (capabilities_csv or "").split(",") if cap.strip()]
    registry = _ensure_agent_registry_exists()
    taxonomy = registry.setdefault("capability_taxonomy", default_agent_registry()["capability_taxonomy"])
    for cap in caps:
        if cap not in taxonomy:
            taxonomy.append(cap)

    agents = registry.setdefault("agents", [])
    existing = next((a for a in agents if a.get("id") == aid), None)
    profile = {
        "id": aid,
        "type": atype,
        "capabilities": caps,
        "constraints": {"max_concurrent_packets": 1},
        "metadata": {},
    }
    if existing:
        existing.update(profile)
        action = "updated"
    else:
        agents.append(profile)
        action = "registered"
    save_agent_registry(registry, AGENTS_REGISTRY_PATH)
    print(green(f"Agent {aid} {action}"))
    return True


def cmd_ready():
    """List packets ready to claim."""
    definition = load_definition()
    state = ensure_state_shape(load_state())

    packets = definition.get("packets", [])
    ready = []
    for pkt in packets:
        pid = pkt["id"]
        if normalize_runtime_status(state["packets"].get(pid, {}).get("status")) == "pending":
            ok, _ = check_deps_met(pid, definition, state)
            if ok:
                ready.append({"id": pkt["id"], "wbs_ref": pkt["wbs_ref"], "title": pkt["title"]})

    if output_json({"ready": ready}):
        return

    if not ready:
        print("No packets ready")
        return

    print(f"\n{'Packet':<12} {'Ref':<8} {'Title'}")
    print("-" * 60)
    for p in ready:
        print(f"{p['id']:<12} {p['wbs_ref']:<8} {p['title']}")


def cmd_status():
    """Full status overview."""
    definition = load_definition()
    state = ensure_state_shape(load_state())
    bf_summary = break_fix_summary(BREAK_FIX_STORE_PATH)
    bf_active_by_packet = bf_summary.get("by_packet_active", {})

    # JSON output
    if JSON_OUTPUT:
        areas = []
        for area in definition.get("work_areas", []):
            pkts = []
            for pkt in definition.get("packets", []):
                if pkt.get("area_id") == area["id"]:
                    ps = state["packets"].get(pkt["id"], {})
                    pkts.append({
                        "id": pkt["id"], "wbs_ref": pkt["wbs_ref"], "title": pkt["title"],
                        "status": normalize_runtime_status(ps.get("status", "pending")), "assigned_to": ps.get("assigned_to"),
                        "notes": ps.get("notes"),
                        "break_fix_active": int(bf_active_by_packet.get(pkt["id"], 0)),
                    })
            areas.append({
                "id": area["id"],
                "title": area["title"],
                "packets": pkts,
                "closeout": state.get("area_closeouts", {}).get(area["id"])
            })
        output_json(
            {
                "metadata": definition.get("metadata", {}),
                "areas": areas,
                "counts": get_counts(state),
                "break_fix_summary": bf_summary,
            }
        )
        return

    meta = definition.get("metadata", {})
    print(f"\n{'=' * 70}")
    print(f"  {meta.get('project_name', 'Project')} — WBS Status")
    print(f"{'=' * 70}\n")

    for area in definition.get("work_areas", []):
        closeout = state.get("area_closeouts", {}).get(area["id"])
        closeout_label = green("L2 CLOSED") if closeout else yellow("L2 OPEN")
        print(f"[{area['id']}] {bold(area['title'])} ({closeout_label})")
        if closeout:
            closed_at = (closeout.get("closed_at") or "")[:19]
            drift_path = closeout.get("drift_assessment_path") or "-"
            closed_by = closeout.get("closed_by") or "-"
            print(dim(f"  drift: {drift_path} | by: {closed_by} | at: {closed_at}"))
        print("-" * 60)

        for pkt in definition.get("packets", []):
            if pkt.get("area_id") == area["id"]:
                pid = pkt["id"]
                pstate = state["packets"].get(pid, {})
                status = normalize_runtime_status(pstate.get("status", "pending")).upper()
                assigned = pstate.get("assigned_to") or "-"

                status_color = {"DONE": green, "FAILED": red, "BLOCKED": red, "IN_PROGRESS": yellow}.get(status, dim)
                bf_active = int(bf_active_by_packet.get(pid, 0))
                bf_suffix = f" | BF active: {bf_active}" if bf_active else ""
                print(
                    f"  {pid:<10} {pkt['wbs_ref']:<6} {status_color(status):<14} {assigned:<12} "
                    f"{pkt['title'][:30]}{bf_suffix}"
                )
        print()

    # Summary
    counts = get_counts(state)
    print(f"{'=' * 70}")
    print("Summary:", ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    print(f"Break-Fix Active: {bf_summary.get('active', 0)} (total: {bf_summary.get('total', 0)})")
    print()


def cmd_progress():
    """Summary counts."""
    state = ensure_state_shape(load_state())
    counts = get_counts(state)
    total = sum(counts.values())

    if output_json({"counts": counts, "total": total}):
        return

    print("\nProgress:")
    print("-" * 25)
    for status in ["pending", "in_progress", "done", "failed", "blocked"]:
        n = counts.get(status, 0)
        if n > 0:
            print(f"  {status:<12}: {n:>3}")
    print("-" * 25)
    print(f"  {'TOTAL':<12}: {total:>3}")
    print()


def cmd_scope(packet_id: str):
    """Show packet details."""
    definition = load_definition()
    state = ensure_state_shape(load_state())

    pkt = next((p for p in definition.get("packets", []) if p["id"] == packet_id), None)
    if not pkt:
        print(red(f"Packet {packet_id} not found"))
        return

    pstate = state["packets"].get(packet_id, {})
    deps = definition.get("dependencies", {}).get(packet_id, [])

    print(f"\nPacket: {pkt['id']}")
    print(f"Title: {pkt['title']}")
    print(f"WBS Ref: {pkt['wbs_ref']}")
    print(f"Status: {normalize_runtime_status(pstate.get('status', 'pending'))}")
    if pstate.get("assigned_to"):
        print(f"Assigned: {pstate['assigned_to']}")
    if deps:
        print(f"Depends on: {', '.join(deps)}")
    print(f"\nScope:\n{pkt['scope']}")
    print()


def cmd_context(
    packet_id: str,
    output_format: str = "text",
    compact: bool = False,
    max_events: int = 40,
    max_notes_bytes: int = 4000,
    max_handovers: int = 40,
) -> bool:
    """Show governed packet context bundle."""
    ok, payload = governance_engine().context_bundle(
        packet_id=packet_id,
        compact=compact,
        max_events=max_events,
        max_notes_bytes=max_notes_bytes,
        max_handovers=max_handovers,
    )
    if not ok:
        print(red(_format_error(payload.get("message", "Unknown error"))))
        return False

    if JSON_OUTPUT or output_format == "json":
        print(json.dumps(payload, indent=2, default=str))
        return True

    print("\nPacket Definition")
    print("-" * 60)
    definition = payload.get("packet_definition", {})
    print(f"ID: {definition.get('id')}")
    print(f"Ref: {definition.get('wbs_ref')}")
    print(f"Title: {definition.get('title')}")
    print(f"Scope: {definition.get('scope', '')[:400]}")

    print("\nRuntime State")
    print("-" * 60)
    runtime = payload.get("runtime_state", {})
    print(f"Status: {runtime.get('status')}")
    print(f"Assigned: {runtime.get('assigned_to') or '-'}")
    print(f"Started: {(runtime.get('started_at') or '-')[:19]}")
    print(f"Completed: {(runtime.get('completed_at') or '-')[:19]}")
    if runtime.get("notes"):
        print(f"Notes: {runtime.get('notes')[:300]}")

    print("\nDependencies")
    print("-" * 60)
    deps = payload.get("dependencies", {})
    upstream = deps.get("upstream", [])
    downstream = deps.get("downstream", [])
    print("Upstream:")
    if upstream:
        for item in upstream:
            print(f"  - {item.get('packet_id')} ({item.get('status')})")
    else:
        print("  - None")
    print("Downstream:")
    if downstream:
        for item in downstream:
            print(f"  - {item.get('packet_id')} ({item.get('status')})")
    else:
        print("  - None")

    print("\nHistory")
    print("-" * 60)
    history = payload.get("history", [])
    if history:
        for event in history:
            ts = (event.get("timestamp") or "")[:19]
            print(
                f"{event.get('packet_id'):<10} {event.get('event'):<10} "
                f"{event.get('agent') or '-':<12} {ts} {(event.get('notes') or '')[:40]}"
            )
    else:
        print("None")

    print("\nHandovers")
    print("-" * 60)
    handovers = payload.get("handovers", [])
    if handovers:
        for handover in handovers:
            print(
                f"{handover.get('handover_id'):<8} from={handover.get('from_agent') or '-'} "
                f"to={handover.get('to_agent') or '-'} active={handover.get('active')}"
            )
    else:
        print("None")

    print("\nFile Manifest")
    print("-" * 60)
    manifest = payload.get("file_manifest", [])
    if manifest:
        for item in manifest[:50]:
            marker = "ok" if item.get("exists") else "missing"
            print(f"{marker:<8} {item.get('path')}")
    else:
        print("None")

    if payload.get("truncated"):
        print(yellow(f"\nTruncated: true {payload.get('truncation')}"))
    print()
    return True


def cmd_log(limit: int = 20):
    """Show recent activity."""
    state = ensure_state_shape(load_state())
    entries = state.get("log", [])[-limit:]

    if output_json({"log": entries}):
        return

    print(f"\nRecent Activity (last {limit}):")
    print("-" * 80)
    print(f"{'Packet':<10} {'Event':<10} {'Agent':<12} {'Time':<20} {'Notes'}")
    print("-" * 80)

    for e in entries:
        notes = (e.get("notes") or "")[:25]
        ts = e.get("timestamp", "")[:19]
        print(f"{e['packet_id']:<10} {e['event']:<10} {(e.get('agent') or '-'):<12} {ts:<20} {notes}")
    print()


def _select_report_scope(definition: dict, scope: str) -> tuple:
    token = str(scope or "").strip()
    work_areas = definition.get("work_areas", [])
    packets = definition.get("packets", [])
    if not token or token.lower() == "all":
        return "all", [a.get("id") for a in work_areas], packets

    area_id = _resolve_area_id(definition, token)
    if any(a.get("id") == area_id for a in work_areas):
        scoped_packets = [p for p in packets if p.get("area_id") == area_id]
        return "area", [area_id], scoped_packets

    packet = next((p for p in packets if p.get("id") == token), None)
    if packet:
        return "packet", [packet.get("area_id")], [packet]

    return "none", [], []


def cmd_delivery_report(scope: str = "all") -> bool:
    """Emit full delivery report for all/area/packet scope."""
    definition = load_definition()
    state = ensure_state_shape(load_state())
    report_type, area_ids, scoped_packets = _select_report_scope(definition, scope)
    if report_type == "none":
        print(red(f"Scope not found: {scope}"))
        return False

    status_counts = {"done": 0, "in_progress": 0, "pending": 0, "failed": 0, "blocked": 0}
    packet_lines = []
    entries = state.get("log", [])
    for pkt in scoped_packets:
        pid = pkt.get("id")
        pstate = state.get("packets", {}).get(pid, {})
        runtime_status = normalize_runtime_status(pstate.get("status", "pending"))
        status_counts[runtime_status] = status_counts.get(runtime_status, 0) + 1

        packet_events = [e for e in entries if e.get("packet_id") == pid]
        started_event = next((e for e in packet_events if e.get("event") == "started"), None)
        completed_event = next((e for e in reversed(packet_events) if e.get("event") == "completed"), None)
        note_event = next((e for e in reversed(packet_events) if e.get("event") in {"noted", "completed"}), None)
        notes = str((note_event or {}).get("notes") or pstate.get("notes") or "")
        evidence_refs = _extract_evidence_paths_from_text(notes)

        packet_lines.append(
            {
                "packet_id": pid,
                "title": pkt.get("title", ""),
                "owner": pstate.get("assigned_to") or "-",
                "status": runtime_status,
                "started_at": (started_event or {}).get("timestamp") or pstate.get("started_at"),
                "completed_at": (completed_event or {}).get("timestamp") or pstate.get("completed_at"),
                "notes": notes,
                "evidence_refs": evidence_refs,
            }
        )

    break_fix = break_fix_summary(BREAK_FIX_STORE_PATH)
    risk = risk_summary(RESIDUAL_RISK_REGISTER_PATH)
    payload = {
        "scope": scope or "all",
        "scope_type": report_type,
        "area_ids": area_ids,
        "summary": status_counts,
        "packet_lines": packet_lines,
        "evidence_sources": ["substrate/.governance/wbs-state.json", "lifecycle log entries"],
        "break_fix": break_fix,
        "residual_risk": risk,
        "risks_gaps": [
            f"open_residual_risks={risk.get('open', 0)}",
            f"active_break_fix={break_fix.get('active', 0)}",
        ],
        "immediate_next_actions": [
            "Complete in_progress packets",
            "Resolve failed/blocked packets",
            "Close open residual risks and break-fix items",
        ],
    }
    if output_json(payload):
        return True

    print("\nDelivery Report")
    print("-" * 80)
    print(f"Scope covered: {payload['scope']} ({report_type})")
    print(
        "Completion summary: "
        + ", ".join(f"{k}={v}" for k, v in payload["summary"].items())
    )
    print("\nPer-packet status lines:")
    for row in packet_lines:
        print(
            f"- {row['packet_id']} | {row['title'][:40]} | owner={row['owner']} | status={row['status']} | "
            f"start={str(row['started_at'] or '-')[:19]} | complete={str(row['completed_at'] or '-')[:19]}"
        )
        if row["notes"]:
            print(f"  notes: {row['notes'][:200]}")
        if row["evidence_refs"]:
            print(f"  evidence: {', '.join(row['evidence_refs'][:8])}")
    print("\nEvidence source references: .governance/wbs-state.json and lifecycle log")
    print(
        "Risks/gaps: "
        + ", ".join(payload["risks_gaps"])
    )
    print("Immediate next actions:")
    for action in payload["immediate_next_actions"]:
        print(f"- {action}")
    print()
    return True


def cmd_risk_list(packet_id: str = "", status: str = "", limit: int = 100) -> bool:
    """List residual risks with optional packet/status filters."""
    if status:
        try:
            status = normalize_risk_status(status)
        except ValueError as e:
            print(red(str(e)))
            return False

    rows = list_risks(
        RESIDUAL_RISK_REGISTER_PATH,
        packet_id=(packet_id or "").strip(),
        status=status,
        limit=max(0, int(limit or 0)),
    )
    payload = {"risks": rows}
    if output_json(payload):
        return True

    if not rows:
        print("No residual risks")
        return True

    print(f"\nResidual Risks ({len(rows)}):")
    print("-" * 96)
    print(f"{'Risk ID':<10} {'Packet':<12} {'Status':<12} {'Impact':<10} {'Likelihood':<10} {'Summary'}")
    print("-" * 96)
    for row in rows:
        summary = str(row.get("description") or "")[:45]
        print(
            f"{(row.get('risk_id') or ''):<10} {(row.get('packet_id') or ''):<12} "
            f"{(row.get('status') or ''):<12} {(row.get('impact') or ''):<10} "
            f"{(row.get('likelihood') or ''):<10} {summary}"
        )
    print()
    return True


def cmd_risk_show(risk_id: str) -> bool:
    """Show a single residual risk record."""
    risk = get_risk(RESIDUAL_RISK_REGISTER_PATH, risk_id)
    if not risk:
        print(red(f"Risk {risk_id} not found"))
        return False
    if output_json({"risk": risk}):
        return True
    print(json.dumps(risk, indent=2))
    return True


def cmd_risk_add(
    packet_id: str,
    actor: str,
    description: str,
    likelihood: str = "medium",
    impact: str = "medium",
    confidence: str = "medium",
    notes: str = "",
) -> bool:
    """Create a residual risk entry directly."""
    entry = {
        "description": description,
        "likelihood": likelihood,
        "impact": impact,
        "confidence": confidence,
        "notes": notes,
    }
    try:
        risk_ids = add_risks(RESIDUAL_RISK_REGISTER_PATH, packet_id=packet_id, actor=actor, entries=[entry])
    except ValueError as e:
        print(red(str(e)))
        return False
    rid = risk_ids[0]
    if output_json({"risk_id": rid}):
        return True
    print(green(f"Residual risk created: {rid}"))
    return True


def cmd_risk_update_status(risk_id: str, status: str, actor: str, notes: str = "") -> bool:
    """Update residual risk status."""
    try:
        ok, msg = update_risk_status(
            RESIDUAL_RISK_REGISTER_PATH,
            risk_id=risk_id,
            status=status,
            actor=actor,
            notes=notes,
        )
    except ValueError as e:
        print(red(str(e)))
        return False
    if ok:
        print(green(msg))
    else:
        print(red(msg))
    return ok


def cmd_risk_summary() -> bool:
    """Show aggregate residual risk counts."""
    summary = risk_summary(RESIDUAL_RISK_REGISTER_PATH)
    if output_json(summary):
        return True
    counts = summary.get("counts", {})
    print("\nResidual Risk Summary")
    print("-" * 40)
    print(f"Total: {summary.get('total', 0)}")
    print(f"Open: {summary.get('open', 0)}")
    for status in sorted(counts.keys()):
        print(f"  {status:<11}: {counts[status]}")
    print()
    return True


def _parse_csv_items(raw: str) -> list:
    if not raw:
        return []
    return [token.strip() for token in str(raw).split(",") if token.strip()]


def _parse_pipe_items(raw: str) -> list:
    if not raw:
        return []
    return [token.strip() for token in str(raw).split("|") if token.strip()]


def cmd_break_fix_open(
    actor: str,
    title: str,
    description: str,
    severity: str = "medium",
    packet_id: str = "",
    linked_packets=None,
    findings=None,
    evidence=None,
) -> bool:
    """Create a break-fix item."""
    try:
        fix_id = open_break_fix(
            BREAK_FIX_STORE_PATH,
            actor=actor,
            title=title,
            description=description,
            severity=severity,
            packet_id=packet_id,
            linked_packets=linked_packets or [],
            findings=findings or [],
            evidence=evidence or [],
        )
    except ValueError as e:
        print(red(str(e)))
        return False
    if output_json({"fix_id": fix_id}):
        return True
    print(green(f"Break-fix item created: {fix_id}"))
    return True


def cmd_break_fix_start(fix_id: str, actor: str, owner: str = "", notes: str = "") -> bool:
    """Start break-fix work item."""
    try:
        ok, msg = start_break_fix(BREAK_FIX_STORE_PATH, fix_id=fix_id, actor=actor, owner=owner, note=notes)
    except ValueError as e:
        print(red(str(e)))
        return False
    if ok:
        print(green(msg))
    else:
        print(red(msg))
    return ok


def cmd_break_fix_resolve(
    fix_id: str,
    actor: str,
    summary: str,
    evidence=None,
    findings=None,
    notes: str = "",
) -> bool:
    """Resolve break-fix item and enforce evidence presence."""
    try:
        ok, msg = resolve_break_fix(
            BREAK_FIX_STORE_PATH,
            fix_id=fix_id,
            actor=actor,
            resolution_summary=summary,
            evidence=evidence or [],
            findings=findings or [],
            note=notes,
        )
    except ValueError as e:
        print(red(str(e)))
        return False
    if ok:
        print(green(msg))
    else:
        print(red(msg))
    return ok


def cmd_break_fix_reject(fix_id: str, actor: str, reason: str, notes: str = "") -> bool:
    """Reject break-fix item."""
    try:
        ok, msg = reject_break_fix(BREAK_FIX_STORE_PATH, fix_id=fix_id, actor=actor, reason=reason, note=notes)
    except ValueError as e:
        print(red(str(e)))
        return False
    if ok:
        print(yellow(msg))
    else:
        print(red(msg))
    return ok


def cmd_break_fix_note(fix_id: str, actor: str, notes: str, evidence=None, findings=None) -> bool:
    """Add note/evidence/findings to break-fix item."""
    try:
        ok, msg = note_break_fix(
            BREAK_FIX_STORE_PATH,
            fix_id=fix_id,
            actor=actor,
            note=notes,
            evidence=evidence or [],
            findings=findings or [],
        )
    except ValueError as e:
        print(red(str(e)))
        return False
    if ok:
        print(green(msg))
    else:
        print(red(msg))
    return ok


def cmd_break_fix_list(
    status: str = "",
    severity: str = "",
    packet_id: str = "",
    owner: str = "",
    limit: int = 100,
) -> bool:
    """List break-fix items with filters."""
    try:
        rows = list_break_fixes(
            BREAK_FIX_STORE_PATH,
            status=status,
            severity=severity,
            packet_id=packet_id,
            owner=owner,
            limit=max(0, int(limit or 0)),
        )
    except ValueError as e:
        print(red(str(e)))
        return False
    summary = break_fix_summary(BREAK_FIX_STORE_PATH)
    if output_json({"break_fixes": rows, "summary": summary}):
        return True
    if not rows:
        print("No break-fix items")
        return True
    print(f"\nBreak-Fix Items ({len(rows)}):")
    print("-" * 120)
    print(f"{'Fix ID':<12} {'Status':<12} {'Severity':<10} {'Owner':<16} {'Packet':<12} {'Title'}")
    print("-" * 120)
    for row in rows:
        print(
            f"{(row.get('fix_id') or ''):<12} {(row.get('status') or ''):<12} {(row.get('severity') or ''):<10} "
            f"{(row.get('owner') or '-'):<16} {(row.get('packet_id') or '-'):<12} {str(row.get('title') or '')[:40]}"
        )
    print()
    return True


def cmd_break_fix_show(fix_id: str) -> bool:
    """Show full break-fix item."""
    row = get_break_fix(BREAK_FIX_STORE_PATH, fix_id)
    if not row:
        print(red(f"Break-fix item not found: {fix_id}"))
        return False
    if output_json({"break_fix": row}):
        return True
    print(json.dumps(row, indent=2))
    return True


def cmd_briefing(output_format: str = "text", compact: bool = False, recent_events: int = 10):
    """Render a structured session bootstrap summary."""
    payload = governance_engine().briefing(recent_events=recent_events, compact=compact)
    payload["break_fix"] = break_fix_summary(BREAK_FIX_STORE_PATH)
    if JSON_OUTPUT or output_format == "json":
        print(json.dumps(payload, indent=2, default=str))
        return

    project = payload.get("project", {})
    counts = payload.get("counts", {})
    ready = payload.get("ready_packets", [])
    blocked = payload.get("blocked_packets", [])
    active = payload.get("active_assignments", [])
    recent = payload.get("recent_events", [])
    break_fix = payload.get("break_fix", {})

    print("\nSummary")
    print("-" * 60)
    print(f"Project: {project.get('project_name') or '-'}")
    print(f"Generated: {payload.get('generated_at')}")
    print(f"Mode: {payload.get('mode')}  Schema: {payload.get('schema_id')}@{payload.get('schema_version')}")
    print(
        "Counts: "
        + ", ".join(
            f"{name}={counts.get(name, 0)}"
            for name in ("pending", "in_progress", "done", "failed", "blocked")
        )
    )
    if payload.get("truncated"):
        print(yellow(f"Truncated: true (limits={payload.get('limits')})"))

    print("\nReady Packets")
    print("-" * 60)
    if ready:
        for item in ready:
            print(f"{item.get('id'):<10} {item.get('wbs_ref', '-'):<8} {item.get('title', '')}")
    else:
        print("None")

    print("\nBlocked Packets")
    print("-" * 60)
    if blocked:
        for item in blocked:
            reasons = ", ".join(
                f"{b.get('packet_id')}({b.get('status')})" for b in item.get("blockers", [])
            )
            print(f"{item.get('id'):<10} {item.get('wbs_ref', '-'):<8} {item.get('status', '-'):<10} {reasons}")
    else:
        print("None")

    print("\nActive Assignments")
    print("-" * 60)
    if active:
        for item in active:
            started = (item.get("started_at") or "")[:19]
            print(f"{item.get('packet_id'):<10} {item.get('agent') or '-':<12} {started}")
    else:
        print("None")

    print("\nRecent Events")
    print("-" * 60)
    if recent:
        for event in recent:
            ts = (event.get("timestamp") or "")[:19]
            print(
                f"{event.get('packet_id'):<10} {event.get('event'):<10} "
                f"{event.get('agent') or '-':<12} {ts} {(event.get('notes') or '')[:40]}"
            )
    else:
        print("None")
    print("\nBreak-Fix Summary")
    print("-" * 60)
    counts = break_fix.get("counts", {})
    print(
        f"Active: {break_fix.get('active', 0)} | Total: {break_fix.get('total', 0)} | "
        f"open={counts.get('open', 0)} in_progress={counts.get('in_progress', 0)} "
        f"resolved={counts.get('resolved', 0)} rejected={counts.get('rejected', 0)}"
    )
    print()


def cmd_log_mode(mode: str) -> bool:
    """Set lifecycle log integrity mode (plain or hash-chain)."""
    try:
        normalized = normalize_log_mode(mode, strict=True)
    except ValueError as e:
        print(red(str(e)))
        return False

    state = ensure_state_shape(load_state())
    state["log_integrity_mode"] = normalized
    save_state(state)

    if normalized == LOG_MODE_HASH_CHAIN:
        print(green("Log integrity mode set: hash-chain (tamper-evident)"))
    else:
        print(green("Log integrity mode set: plain"))
    return True


def cmd_verify_log() -> bool:
    """Verify lifecycle log hash chain integrity."""
    state = ensure_state_shape(load_state())
    entries = state.get("log", [])
    valid, issues = verify_log_integrity(entries)
    result = {
        "valid": valid,
        "events": len(entries),
        "hashed_events": sum(1 for e in entries if isinstance(e, dict) and e.get("hash")),
        "mode": state.get("log_integrity_mode", LOG_MODE_PLAIN),
        "issues": issues,
    }
    if output_json(result):
        return valid

    if valid:
        print(green(f"Log integrity OK: {result['hashed_events']} hashed events across {result['events']} total events"))
        return True

    print(red(f"Log integrity FAILED ({len(issues)} issues):"))
    for issue in issues:
        print(f"  - {issue}")
    return False


def cmd_next():
    """Show recommended next action."""
    definition = load_definition()
    state = ensure_state_shape(load_state())

    # Check for in-progress
    for pkt in definition.get("packets", []):
        pid = pkt["id"]
        if normalize_runtime_status(state["packets"].get(pid, {}).get("status")) == "in_progress":
            agent = state["packets"][pid].get("assigned_to", "your-name")
            print("Next action:")
            print(f"  python3 .governance/wbs_cli.py done {pid} {agent} \"notes\"")
            print(f"Reason: {pid} is in progress")
            return

    # Check for ready
    for pkt in definition.get("packets", []):
        pid = pkt["id"]
        if normalize_runtime_status(state["packets"].get(pid, {}).get("status")) == "pending":
            ok, _ = check_deps_met(pid, definition, state)
            if ok:
                print("Next action:")
                print(f"  python3 .governance/wbs_cli.py claim {pid} your-name")
                print(f"Reason: {pid} is ready ({pkt['title']})")
                return

    # Check completion
    done = sum(1 for p in state["packets"].values() if normalize_runtime_status(p.get("status")) == "done")
    total = len(state["packets"])

    if done == total and total > 0:
        print("Next action: None — all packets complete!")
    else:
        print("Next action:")
        print("  python3 .governance/wbs_cli.py status")
        print("Reason: Check for blocked/failed packets")


def cmd_stale(minutes: int, warn_factor: float = None, critical_factor: float = None) -> bool:
    """Find stale in-progress packets with severity and recommended next action."""
    state = ensure_state_shape(load_state())
    mode_cfg = get_mode_config(state)
    if warn_factor is None:
        warn_factor = float(mode_cfg.get("stale_warn_factor", 1.0))
    if critical_factor is None:
        critical_factor = float(mode_cfg.get("stale_critical_factor", 3.0))
    now = datetime.now()
    rows = []

    for pid, pstate in state["packets"].items():
        status = normalize_runtime_status(pstate.get("status"))
        if status == "in_progress" and pstate.get("started_at"):
            started = datetime.fromisoformat(pstate["started_at"])
            elapsed = (now - started).total_seconds() / 60
            if elapsed > minutes:
                severity = "warning"
                action = "nudge owner and add note with current evidence"
                if elapsed >= (minutes * critical_factor):
                    severity = "critical"
                    action = "handover or fail packet with dependency impact"
                elif elapsed >= (minutes * warn_factor):
                    severity = "warning"
                    action = "update notes and re-validate active progress"
                rows.append(
                    {
                        "packet_id": pid,
                        "owner": pstate.get("assigned_to"),
                        "elapsed_minutes": int(elapsed),
                        "severity": severity,
                        "recommended_action": action,
                        "started_at": pstate.get("started_at"),
                    }
                )

    rows.sort(key=lambda r: r["elapsed_minutes"], reverse=True)
    if output_json({"threshold_minutes": minutes, "warn_factor": warn_factor, "critical_factor": critical_factor, "stale": rows}):
        return True

    if not rows:
        print(green("No stale packets"))
        return True

    print("\nStale Packet Watchdog")
    print("-" * 96)
    print(f"{'Packet':<14} {'Owner':<14} {'Elapsed(min)':<12} {'Severity':<10} {'Recommended action'}")
    print("-" * 96)
    for row in rows:
        sev = red(row["severity"]) if row["severity"] == "critical" else yellow(row["severity"])
        print(
            f"{row['packet_id']:<14} {str(row['owner'] or '-'):<14} {row['elapsed_minutes']:<12} "
            f"{sev:<10} {row['recommended_action']}"
        )
    print()
    return True


def cmd_closeout_readiness(area_id: str) -> bool:
    """Score closeout readiness for a level-2 area and show blockers."""
    definition = load_definition()
    state = ensure_state_shape(load_state())
    resolved_area_id = _resolve_area_id(definition, area_id)
    area = next((a for a in definition.get("work_areas", []) if a.get("id") == resolved_area_id), None)
    if not area:
        print(red(f"Area not found: {area_id}"))
        return False

    packets = [p for p in definition.get("packets", []) if p.get("area_id") == resolved_area_id]
    total = len(packets)
    done_packets = []
    incomplete_packets = []
    missing_evidence = []

    for pkt in packets:
        pid = pkt.get("id")
        pstate = state.get("packets", {}).get(pid, {})
        status = normalize_runtime_status(pstate.get("status", "pending"))
        if status == "done":
            done_packets.append(pid)
            note_text = str(pstate.get("notes") or "")
            refs = _extract_evidence_paths_from_text(note_text)
            if not refs:
                missing_evidence.append({"packet_id": pid, "reason": "no evidence refs in notes"})
            else:
                ok, missing, _checked = _verify_evidence_paths(refs)
                if not ok:
                    missing_evidence.append({"packet_id": pid, "reason": f"missing files: {', '.join(missing[:5])}"})
        else:
            incomplete_packets.append({"packet_id": pid, "status": status})

    packet_ids = {p.get("id") for p in packets}
    break_fix = break_fix_summary(BREAK_FIX_STORE_PATH)
    active_break_fix = sum(
        int(v)
        for pid, v in break_fix.get("by_packet_active", {}).items()
        if pid in packet_ids
    )
    open_risks = list_risks(RESIDUAL_RISK_REGISTER_PATH, status="open", limit=0)
    open_risk_count = sum(1 for r in open_risks if str(r.get("packet_id") or "") in packet_ids)

    done_ratio = (len(done_packets) / total) if total else 0.0
    completion_score = round(done_ratio * 60.0, 2)
    break_fix_score = max(0.0, 20.0 - (5.0 * active_break_fix))
    risk_score = max(0.0, 10.0 - (2.0 * open_risk_count))
    evidence_score = max(0.0, 10.0 - (2.0 * len(missing_evidence)))
    score = round(min(100.0, completion_score + break_fix_score + risk_score + evidence_score), 2)

    payload = {
        "area_id": resolved_area_id,
        "area_title": area.get("title", ""),
        "score": score,
        "components": {
            "completion": completion_score,
            "break_fix": break_fix_score,
            "risk": risk_score,
            "evidence": evidence_score,
        },
        "totals": {
            "packets_total": total,
            "packets_done": len(done_packets),
            "packets_incomplete": len(incomplete_packets),
            "active_break_fix": active_break_fix,
            "open_residual_risks": open_risk_count,
            "done_packets_missing_evidence": len(missing_evidence),
        },
        "blockers": {
            "incomplete_packets": incomplete_packets,
            "missing_evidence": missing_evidence,
        },
        "ready_for_closeout": (
            len(incomplete_packets) == 0
            and active_break_fix == 0
            and open_risk_count == 0
            and len(missing_evidence) == 0
        ),
    }
    if output_json(payload):
        return True

    print("\nCloseout Readiness")
    print("-" * 80)
    print(f"Area: {payload['area_id']} ({payload['area_title']})")
    print(f"Score: {payload['score']}/100")
    print(
        f"Totals: packets={total}, done={len(done_packets)}, incomplete={len(incomplete_packets)}, "
        f"active_break_fix={active_break_fix}, open_risks={open_risk_count}, missing_evidence={len(missing_evidence)}"
    )
    print(
        "Components: "
        + ", ".join(f"{k}={v}" for k, v in payload["components"].items())
    )
    if payload["ready_for_closeout"]:
        print(green("Ready for closeout-l2"))
    else:
        print(yellow("Not ready for closeout-l2"))
        if incomplete_packets:
            print("Incomplete packets:")
            for row in incomplete_packets:
                print(f"- {row['packet_id']} ({row['status']})")
        if missing_evidence:
            print("Done packets with evidence gaps:")
            for row in missing_evidence[:20]:
                print(f"- {row['packet_id']}: {row['reason']}")
    print()
    return True


def _resolve_area_id(definition: dict, area_id: str) -> str:
    """Allow passing either 'N' or 'N.0' for level-2 area id."""
    area_id = (area_id or "").strip()
    area_ids = {a["id"] for a in definition.get("work_areas", [])}
    if area_id in area_ids:
        return area_id
    if area_id.isdigit():
        candidate = f"{area_id}.0"
        if candidate in area_ids:
            return candidate
    return area_id


def _validate_drift_assessment(path: str) -> tuple:
    """Validate drift assessment document exists and includes required sections."""
    if not path.strip():
        return False, None, ["assessment path is required"]

    raw = Path(path.strip())
    target = raw if raw.is_absolute() else (GOV.parent / raw)
    if not target.exists() or not target.is_file():
        return False, None, [f"assessment file not found: {path}"]

    text = target.read_text(errors="replace")
    lower = text.lower()
    missing = [section for section in REQUIRED_DRIFT_SECTIONS if section.lower() not in lower]
    if missing:
        return False, target.resolve(), [f"missing required section: {section}" for section in missing]
    return True, target.resolve(), []


def cmd_closeout_l2(area_id: str, agent: str, assessment_path: str, notes: str = "") -> bool:
    """Close out a level-2 area with required drift assessment evidence."""
    ok, msg = _run_lifecycle_with_git(
        packet_id=f"AREA-{area_id}",
        action="closeout-l2",
        agent=agent,
        operation=lambda: governance_engine().closeout_l2(area_id, agent, assessment_path, notes),
        area_id=area_id,
        closeout_area=area_id,
    )
    if ok:
        print(green(msg))
        print(dim(f"Drift assessment: {assessment_path}"))
    else:
        print(red(_format_error(msg)))
    return ok


def require_state():
    """Check state file exists. Resolves path at call-time."""
    if not resolve_runtime_paths()["wbs_state"].exists():
        print(red("Not initialized. Run: python3 .governance/wbs_cli.py init .governance/wbs.json"))
        return False
    return True


def save_definition(defn: dict):
    """Save WBS definition with cross-platform lock + atomic replace.

    Resolves the definition path at call-time via resolve_runtime_paths().
    """
    atomic_write_json(resolve_runtime_paths()["wbs_def"], defn)


def cmd_add_area(area_id: str, title: str, description: str = "", approval_token: str = "") -> bool:
    """Add a work area."""
    if not require_wbs_mutation_approval("add-area", approval_token):
        return False
    defn = load_definition()

    if any(a["id"] == area_id for a in defn.get("work_areas", [])):
        print(red(f"Area {area_id} already exists"))
        return False

    defn.setdefault("work_areas", []).append({
        "id": area_id,
        "title": title,
        "description": description
    })
    save_definition(defn)
    print(green(f"Added area: {area_id} - {title}"))
    return True


def cmd_add_packet(
    packet_id: str,
    area_id: str,
    title: str,
    scope: str,
    wbs_ref: str = None,
    preset: str = "",
    approval_token: str = "",
) -> bool:
    """Add a packet."""
    if not require_wbs_mutation_approval("add-packet", approval_token):
        return False
    defn = load_definition()

    if any(p["id"] == packet_id for p in defn.get("packets", [])):
        print(red(f"Packet {packet_id} already exists"))
        return False

    if not any(a["id"] == area_id for a in defn.get("work_areas", [])):
        print(red(f"Area {area_id} not found"))
        return False

    # Auto-generate wbs_ref if not provided
    if not wbs_ref:
        area_packets = [p for p in defn.get("packets", []) if p.get("area_id") == area_id]
        next_num = len(area_packets) + 1
        # Find area index for prefix
        area_idx = next((i for i, a in enumerate(defn.get("work_areas", [])) if a["id"] == area_id), 0) + 1
        wbs_ref = f"{area_idx}.{next_num}"

    preset_token = str(preset or "").strip().lower()
    if preset_token:
        if preset_token not in PACKET_PRESETS:
            print(red(f"Unknown preset: {preset_token}. Use one of: {', '.join(sorted(PACKET_PRESETS.keys()))}"))
            return False
        if not scope.strip():
            scope = PACKET_PRESETS[preset_token]["scope_template"].format(title=title)

    defn.setdefault("packets", []).append({
        "id": packet_id,
        "wbs_ref": wbs_ref,
        "area_id": area_id,
        "title": title,
        "scope": scope,
    })
    save_definition(defn)

    # Initialize state for new packet
    state = ensure_state_shape(load_state())
    if packet_id not in state["packets"]:
        state["packets"][packet_id] = {
            "status": "pending",
            "assigned_to": None,
            "started_at": None,
            "completed_at": None,
            "notes": None
        }
        save_state(state)

    print(green(f"Added packet: {packet_id} ({wbs_ref}) - {title}"))
    return True


def cmd_add_dep(packet_id: str, depends_on: str, approval_token: str = "") -> bool:
    """Add a dependency."""
    if not require_wbs_mutation_approval("add-dep", approval_token):
        return False
    if packet_id == depends_on:
        print(red("Packet cannot depend on itself"))
        return False

    defn = load_definition()
    packets = [p["id"] for p in defn.get("packets", [])]

    if packet_id not in packets:
        print(red(f"Packet {packet_id} not found"))
        return False
    if depends_on not in packets:
        print(red(f"Packet {depends_on} not found"))
        return False

    deps = defn.setdefault("dependencies", {})
    pkt_deps = deps.setdefault(packet_id, [])

    if depends_on in pkt_deps:
        print(yellow(f"Dependency already exists"))
        return True

    pkt_deps.append(depends_on)

    # Check for circular dependency
    cycle = detect_circular(deps)
    if cycle:
        pkt_deps.remove(depends_on)
        print(red(f"Would create circular dependency: {' -> '.join(cycle)}"))
        return False

    save_definition(defn)
    print(green(f"Added dependency: {packet_id} depends on {depends_on}"))
    return True


def cmd_remove(item_id: str, force: bool = False, approval_token: str = "") -> bool:
    """Remove a packet or area."""
    if not require_wbs_mutation_approval("remove", approval_token):
        return False
    defn = load_definition()

    # Check if it's a packet
    packet = next((p for p in defn.get("packets", []) if p["id"] == item_id), None)
    if packet:
        state = ensure_state_shape(load_state())
        pkt_state = state["packets"].get(item_id, {})
        packet_status = normalize_runtime_status(pkt_state.get("status"))
        if packet_status in ("in_progress", "done") and not force:
            print(red(f"Packet {item_id} is {packet_status}. Use --force to remove."))
            return False

        # Check for dependents
        deps = defn.get("dependencies", {})
        dependents = [pid for pid, dep_list in deps.items() if item_id in dep_list]
        if dependents and not force:
            print(red(f"Packet {item_id} is a dependency for: {', '.join(dependents)}"))
            print("Use --force to remove anyway (will also remove dependencies)")
            return False

        # Remove packet
        defn["packets"] = [p for p in defn["packets"] if p["id"] != item_id]

        # Remove from dependencies
        if item_id in deps:
            del deps[item_id]
        for pid in deps:
            if item_id in deps[pid]:
                deps[pid].remove(item_id)

        # Remove from state
        if item_id in state["packets"]:
            del state["packets"][item_id]
            save_state(state)

        save_definition(defn)
        print(green(f"Removed packet: {item_id}"))
        return True

    # Check if it's an area
    area = next((a for a in defn.get("work_areas", []) if a["id"] == item_id), None)
    if area:
        area_packets = [p["id"] for p in defn.get("packets", []) if p.get("area_id") == item_id]
        if area_packets and not force:
            print(red(f"Area {item_id} contains packets: {', '.join(area_packets)}"))
            print("Use --force to remove area and all its packets")
            return False

        # Remove area and its packets
        defn["work_areas"] = [a for a in defn["work_areas"] if a["id"] != item_id]

        if force and area_packets:
            defn["packets"] = [p for p in defn["packets"] if p.get("area_id") != item_id]
            deps = defn.get("dependencies", {})
            for pid in area_packets:
                if pid in deps:
                    del deps[pid]
                for d in deps:
                    if pid in deps[d]:
                        deps[d].remove(pid)

            state = ensure_state_shape(load_state())
            for pid in area_packets:
                if pid in state["packets"]:
                    del state["packets"][pid]
            save_state(state)

        save_definition(defn)
        print(green(f"Removed area: {item_id}" + (f" (and {len(area_packets)} packets)" if area_packets else "")))
        return True

    print(red(f"Not found: {item_id}"))
    return False


def cmd_packet_presets() -> bool:
    """List optional packet preset templates for add-packet."""
    payload = {"presets": PACKET_PRESETS}
    if output_json(payload):
        return True
    print("\nPacket Presets:")
    print("-" * 60)
    for name in sorted(PACKET_PRESETS.keys()):
        tmpl = PACKET_PRESETS[name].get("scope_template", "")
        print(f"- {name}: {tmpl}")
    print()
    return True


def _format_json_path(path_tokens) -> str:
    """Render validator path tokens as $.foo[0].bar for readable errors."""
    out = "$"
    for token in path_tokens:
        if isinstance(token, int):
            out += f"[{token}]"
        else:
            out += f".{token}"
    return out


def _validate_json_schema(payload: dict, schema_path: Path) -> list:
    """Validate payload against JSON schema and return readable error lines."""
    if Draft202012Validator is None:
        return []
    try:
        schema = json.loads(schema_path.read_text())
    except Exception as e:
        return [f"failed to load schema {schema_path}: {e}"]

    validator = Draft202012Validator(schema)
    errors = []
    ordered = sorted(validator.iter_errors(payload), key=lambda err: _format_json_path(err.path))
    for err in ordered:
        errors.append(f"{_format_json_path(err.path)}: {err.message}")
    return errors


def _validate_packet_strict(pkt: dict, index: int) -> list:
    """Apply strict packet contract checks with packet-specific error labels."""
    label = pkt.get("id") if isinstance(pkt, dict) and pkt.get("id") else f"packet[{index}]"
    errors = _validate_packet_object(pkt, label)
    if not isinstance(pkt, dict):
        return errors

    pkt_id = pkt.get("id")
    canonical_id = pkt.get("packet_id")
    if isinstance(pkt_id, str) and isinstance(canonical_id, str) and canonical_id != pkt_id:
        errors.append(f"{label}: packet_id must match id ({canonical_id} != {pkt_id})")

    wbs_ref = pkt.get("wbs_ref")
    wbs_refs = pkt.get("wbs_refs")
    if isinstance(wbs_ref, str) and isinstance(wbs_refs, list) and wbs_ref and wbs_ref not in wbs_refs:
        errors.append(f"{label}: wbs_refs must include wbs_ref value ({wbs_ref})")

    status = pkt.get("status")
    if status is not None:
        canonical_status = normalize_packet_status(status)
        if status != canonical_status:
            errors.append(f"{label}: status must use canonical packet value {canonical_status}")
    return errors


def cmd_validate(strict: bool = False) -> bool:
    """Validate WBS structure and, optionally, strict packet contract compliance."""
    defn = load_definition()
    errors = []

    schema_requirements = [("packet", "1.0"), ("wbs_definition", "1.0")]
    ok, msg = enforce_schema_contracts(schema_requirements)
    if not ok:
        errors.append(msg)

    wbs_schema_path = WBS_SCHEMA_PATH
    try:
        reg = SchemaRegistry.from_registry_file(SCHEMA_REGISTRY_PATH, root=GOV.parent)
        wbs_schema_path = reg.get("wbs_definition").path
    except Exception:
        pass

    if wbs_schema_path.exists():
        for err in _validate_json_schema(defn, wbs_schema_path):
            errors.append(f"schema: {err}")
    else:
        errors.append(f"WBS schema missing: {wbs_schema_path}")

    work_areas = defn.get("work_areas", []) if isinstance(defn, dict) else []
    packets_list = defn.get("packets", []) if isinstance(defn, dict) else []
    deps = defn.get("dependencies", {}) if isinstance(defn, dict) else {}

    # Check for circular dependencies
    if isinstance(deps, dict):
        cycle = detect_circular(deps)
        if cycle:
            errors.append(f"Circular dependency: {' -> '.join(cycle)}")

    # Check all packets have valid areas
    areas = {a.get("id") for a in work_areas if isinstance(a, dict)}
    for pkt in packets_list:
        if not isinstance(pkt, dict):
            continue
        if pkt.get("area_id") not in areas:
            errors.append(f"Packet {pkt.get('id', '<unknown>')} references unknown area: {pkt.get('area_id')}")

    # Check all dependencies reference valid packets
    packet_ids = {p.get("id") for p in packets_list if isinstance(p, dict)}
    for pid, dep_list in deps.items():
        if pid not in packet_ids:
            errors.append(f"Dependency references unknown packet: {pid}")
        if not isinstance(dep_list, list):
            errors.append(f"Dependency list for {pid} must be an array")
            continue
        for dep in dep_list:
            if dep not in packet_ids:
                errors.append(f"Packet {pid} depends on unknown packet: {dep}")

    # Check for duplicate IDs
    pkt_ids = [p.get("id") for p in packets_list if isinstance(p, dict)]
    if len(pkt_ids) != len(set(pkt_ids)):
        errors.append("Duplicate packet IDs found")

    area_ids = [a.get("id") for a in work_areas if isinstance(a, dict)]
    if len(area_ids) != len(set(area_ids)):
        errors.append("Duplicate area IDs found")

    if strict:
        for idx, pkt in enumerate(packets_list):
            errors.extend(_validate_packet_strict(pkt, idx))

    result = {
        "valid": len(errors) == 0,
        "strict": strict,
        "areas": len(area_ids),
        "packets": len(pkt_ids),
        "errors": errors,
    }
    if output_json(result):
        return result["valid"]

    mode = "strict" if strict else "standard"
    if errors:
        print(red(f"Validation failed ({mode}):"))
        max_errors = 120
        shown = errors[:max_errors]
        for err in shown:
            print(f"  - {err}")
        if len(errors) > max_errors:
            remaining = len(errors) - max_errors
            print(f"  - ... {remaining} additional errors omitted (use --json for full output)")
        return False

    print(green(f"Validation passed ({mode}): {len(area_ids)} areas, {len(pkt_ids)} packets"))
    return True


def cmd_template_validate() -> bool:
    """Run full template integrity checks via scaffold validation script."""
    script = GOV.parent / "scripts" / "template-integrity.sh"
    if not script.exists():
        msg = f"Template integrity script missing: {script}"
        if output_json({"ok": False, "message": msg}):
            return False
        print(red(msg))
        return False

    proc = subprocess.run(["bash", str(script)], cwd=str(GOV.parent))
    ok = proc.returncode == 0
    if output_json({"ok": ok, "script": str(script)}):
        return ok
    return ok


def _validate_packet_object(pkt: dict, index_label: str = "") -> list:
    """Validate packet object against canonical packet standard."""
    errors = []
    prefix = f"{index_label}: " if index_label else ""

    if not isinstance(pkt, dict):
        return [f"{prefix}packet is not an object"]

    # Required fields present
    for field in REQUIRED_PACKET_FIELDS:
        if field not in pkt:
            errors.append(f"{prefix}missing required field: {field}")

    # Required string fields
    for field in ("packet_id", "title", "purpose", "owner"):
        val = pkt.get(field)
        if val is not None and not isinstance(val, str):
            errors.append(f"{prefix}{field} must be a string")
        elif isinstance(val, str) and not val.strip():
            errors.append(f"{prefix}{field} must be non-empty")

    # Enum fields
    status = pkt.get("status")
    if status is not None and status not in PACKET_STATUS_VALUES:
        errors.append(f"{prefix}status must be one of: {', '.join(sorted(PACKET_STATUS_VALUES))}")

    priority = pkt.get("priority")
    if priority is not None and priority not in PACKET_PRIORITY_VALUES:
        errors.append(f"{prefix}priority must be one of: {', '.join(sorted(PACKET_PRIORITY_VALUES))}")

    # Array fields
    array_fields = (
        "wbs_refs",
        "required_capabilities",
        "preconditions",
        "required_inputs",
        "required_actions",
        "required_outputs",
        "validation_checks",
        "exit_criteria",
        "halt_conditions",
    )
    for field in array_fields:
        val = pkt.get(field)
        if val is not None and not isinstance(val, list):
            errors.append(f"{prefix}{field} must be an array")
        elif isinstance(val, list):
            for i, item in enumerate(val):
                if not isinstance(item, str):
                    errors.append(f"{prefix}{field}[{i}] must be a string")

    # Minimum cardinality for key arrays
    for field in ("wbs_refs", "required_actions", "exit_criteria"):
        val = pkt.get(field)
        if isinstance(val, list) and len(val) == 0:
            errors.append(f"{prefix}{field} must contain at least one item")

    return errors


def cmd_validate_packet(path: str = "") -> bool:
    """Validate packet JSON against canonical packet standard."""
    ok, msg = enforce_schema_contracts()
    if not ok:
        if output_json({"valid": False, "errors": [msg]}):
            return False
        print(red(msg))
        return False
    packet_source = path.strip()

    try:
        if packet_source:
            with open(packet_source) as f:
                payload = json.load(f)
        else:
            payload = load_definition()
    except FileNotFoundError:
        print(red(f"File not found: {packet_source}"))
        return False
    except json.JSONDecodeError as e:
        print(red(f"Invalid JSON: {e}"))
        return False

    # Determine packet collection source
    if isinstance(payload, dict) and isinstance(payload.get("packets"), list):
        packets = payload["packets"]
        source_label = packet_source or str(WBS_DEF)
    elif isinstance(payload, list):
        packets = payload
        source_label = packet_source
    elif isinstance(payload, dict):
        packets = [payload]
        source_label = packet_source
    else:
        msg = "Packet payload must be an object, array of objects, or WBS file with packets[]"
        if output_json({"valid": False, "errors": [msg]}):
            return False
        print(red(msg))
        return False

    all_errors = []
    for i, pkt in enumerate(packets):
        pid = pkt.get("packet_id") if isinstance(pkt, dict) else None
        label = pid or f"packet[{i}]"
        all_errors.extend(_validate_packet_object(pkt, label))

    result = {
        "valid": len(all_errors) == 0,
        "packet_count": len(packets),
        "source": source_label,
        "schema_path": str(PACKET_SCHEMA_PATH),
        "errors": all_errors,
    }
    if output_json(result):
        return result["valid"]

    if result["valid"]:
        print(green(f"Packet validation passed: {len(packets)} packets"))
        print(dim(f"Schema: {PACKET_SCHEMA_PATH}"))
        return True
    print(red(f"Packet validation failed ({len(all_errors)} issues):"))
    for err in all_errors:
        print(f"  - {err}")
    print(dim(f"Schema: {PACKET_SCHEMA_PATH}"))
    return False


def cmd_draft_create(source_path: str = "", output_path: str = "") -> bool:
    """Create a WBS draft file from active definition or explicit source."""
    source = Path(source_path).expanduser() if source_path else WBS_DEF
    if not source.is_absolute():
        source = source.resolve()
    if not source.exists():
        print(red(f"Draft source not found: {source}"))
        return False
    target = Path(output_path).expanduser() if output_path else (GOV / "wbs.draft.json")
    if not target.is_absolute():
        target = target.resolve()
    try:
        payload = json.loads(source.read_text())
    except json.JSONDecodeError as e:
        print(red(f"Draft source is invalid JSON: {e}"))
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n")
    print(green(f"Draft created: {target}"))
    return True


def cmd_draft_apply(draft_path: str, actor: str, notes: str = "", approval_token: str = "") -> bool:
    """Apply draft WBS into active definition under explicit mutation approval."""
    if not require_wbs_mutation_approval("draft-apply", approval_token):
        return False
    draft = Path(draft_path).expanduser()
    if not draft.is_absolute():
        draft = draft.resolve()
    if not draft.exists():
        print(red(f"Draft not found: {draft}"))
        return False
    try:
        definition = json.loads(draft.read_text())
    except json.JSONDecodeError as e:
        print(red(f"Draft is invalid JSON: {e}"))
        return False
    plan_errors = validate_planned_definition(definition)
    if plan_errors:
        print(red("Draft definition validation failed:"))
        for err in plan_errors:
            print(f"  - {err}")
        return False
    cycle = detect_circular(definition.get("dependencies", {}))
    if cycle:
        print(red(f"Circular dependency in draft: {' -> '.join(cycle)}"))
        return False
    if not cmd_init(str(draft), approval_token=approval_token):
        return False
    state = ensure_state_shape(load_state())
    log_event(
        state,
        "WBS-DRAFT",
        "draft_applied",
        agent=actor,
        notes=f"path={draft} notes={notes}".strip(),
    )
    save_state(state)
    print(green(f"Draft applied: {draft}"))
    return True


def cmd_graph(output_path: str = ""):
    """Show ASCII dependency graph and optionally export Graphviz DOT."""
    defn = load_definition()
    state = ensure_state_shape(load_state())
    deps = defn.get("dependencies", {})
    packets = {p["id"]: p for p in defn.get("packets", [])}

    # Find root packets (no dependencies)
    all_deps = set()
    for dep_list in deps.values():
        all_deps.update(dep_list)

    roots = [pid for pid in packets if pid not in deps or not deps[pid]]

    # Status symbols
    status_sym = {
        "pending": dim("[ ]"),
        "in_progress": yellow("[~]"),
        "done": green("[x]"),
        "failed": red("[!]"),
        "blocked": red("[#]")
    }

    def print_tree(pid, prefix="", is_last=True):
        pkt = packets.get(pid, {})
        pstate = state["packets"].get(pid, {})
        status = normalize_runtime_status(pstate.get("status", "pending"))
        sym = status_sym.get(status, "[ ]")

        connector = "`-- " if is_last else "|-- "
        print(f"{prefix}{connector}{sym} {pid}: {pkt.get('title', '')[:40]}")

        # Find children (packets that depend on this one)
        children = [p for p, d in deps.items() if pid in d]
        for i, child in enumerate(children):
            ext = "    " if is_last else "|   "
            print_tree(child, prefix + ext, i == len(children) - 1)

    print("\nDependency Graph:")
    print("-" * 60)
    print("Legend: [ ] pending  [~] in progress  [x] done  [!] failed  [#] blocked")
    print("-" * 60)

    for i, root in enumerate(sorted(roots)):
        print_tree(root, "", i == len(roots) - 1)

    # Show any orphan packets (not in tree)
    shown = set()
    def collect_shown(pid):
        shown.add(pid)
        for p, d in deps.items():
            if pid in d:
                collect_shown(p)
    for root in roots:
        collect_shown(root)

    orphans = set(packets.keys()) - shown
    if orphans:
        print(f"\nOrphan packets (no dependencies, not depended on): {', '.join(sorted(orphans))}")

    print()

    if output_path:
        out = Path(output_path).expanduser()
        if not out.is_absolute():
            out = GOV.parent / out
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            f.write("digraph wbs_dependencies {\n")
            f.write("  rankdir=LR;\n")
            for pid, pkt in packets.items():
                title = pkt.get("title", "")
                escaped_title = title.replace('"', '\\"')
                label = f"{pid}\\n{escaped_title}"
                f.write(f"  \"{pid}\" [label=\"{label}\"];\n")
            for target, sources in deps.items():
                for source in sources:
                    f.write(f"  \"{source}\" -> \"{target}\";\n")
            f.write("}\n")
        print(green(f"DOT graph exported: {out}"))


def cmd_export(kind: str, out_path: str) -> bool:
    """Export state/log data for external analysis."""
    state = ensure_state_shape(load_state())
    kind = (kind or "").strip().lower()
    out = Path(out_path).expanduser()
    if not out.is_absolute():
        out = GOV.parent / out
    out.parent.mkdir(parents=True, exist_ok=True)

    if kind == "state-json":
        payload = {
            "packets": state.get("packets", {}),
            "area_closeouts": state.get("area_closeouts", {}),
            "break_fix_summary": break_fix_summary(BREAK_FIX_STORE_PATH),
        }
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(green(f"Exported state JSON: {out}"))
        return True

    if kind == "log-json":
        payload = {"log": state.get("log", [])}
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(green(f"Exported log JSON: {out}"))
        return True

    if kind == "log-csv":
        fields = ["packet_id", "event", "agent", "timestamp", "notes"]
        with open(out, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for entry in state.get("log", []):
                writer.writerow({k: entry.get(k) for k in fields})
        print(green(f"Exported log CSV: {out}"))
        return True

    if kind == "risk-json":
        payload = load_register(RESIDUAL_RISK_REGISTER_PATH)
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(green(f"Exported residual risk JSON: {out}"))
        return True

    if kind == "break-fix-json":
        payload = {"break_fix": list_break_fixes(BREAK_FIX_STORE_PATH, limit=0), "summary": break_fix_summary(BREAK_FIX_STORE_PATH)}
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(green(f"Exported break-fix JSON: {out}"))
        return True

    print(red("Unknown export type. Use: state-json | log-json | log-csv | risk-json | break-fix-json"))
    return False


def cmd_wbs_diff(old_path: str, new_path: str) -> bool:
    """Explain structural differences between two WBS definition files."""
    old_file = _resolve_repo_path(old_path)
    new_file = _resolve_repo_path(new_path)
    if not old_file.exists():
        print(red(f"Old WBS file not found: {old_path}"))
        return False
    if not new_file.exists():
        print(red(f"New WBS file not found: {new_path}"))
        return False

    old_def = json.loads(old_file.read_text())
    new_def = json.loads(new_file.read_text())

    old_areas = {a.get("id"): a for a in old_def.get("work_areas", []) if isinstance(a, dict)}
    new_areas = {a.get("id"): a for a in new_def.get("work_areas", []) if isinstance(a, dict)}
    old_packets = {p.get("id"): p for p in old_def.get("packets", []) if isinstance(p, dict)}
    new_packets = {p.get("id"): p for p in new_def.get("packets", []) if isinstance(p, dict)}
    old_deps = old_def.get("dependencies", {}) if isinstance(old_def.get("dependencies"), dict) else {}
    new_deps = new_def.get("dependencies", {}) if isinstance(new_def.get("dependencies"), dict) else {}

    area_added = sorted([aid for aid in new_areas if aid not in old_areas])
    area_removed = sorted([aid for aid in old_areas if aid not in new_areas])
    area_changed = sorted(
        [
            aid
            for aid in (set(old_areas.keys()) & set(new_areas.keys()))
            if (old_areas[aid].get("title"), old_areas[aid].get("description", ""))
            != (new_areas[aid].get("title"), new_areas[aid].get("description", ""))
        ]
    )

    packet_added = sorted([pid for pid in new_packets if pid not in old_packets])
    packet_removed = sorted([pid for pid in old_packets if pid not in new_packets])
    packet_changed = sorted(
        [
            pid
            for pid in (set(old_packets.keys()) & set(new_packets.keys()))
            if old_packets[pid] != new_packets[pid]
        ]
    )

    dep_added = []
    dep_removed = []
    all_dep_keys = set(old_deps.keys()) | set(new_deps.keys())
    for pid in sorted(all_dep_keys):
        old_set = set(old_deps.get(pid, []) or [])
        new_set = set(new_deps.get(pid, []) or [])
        for dep in sorted(new_set - old_set):
            dep_added.append({"packet": pid, "depends_on": dep})
        for dep in sorted(old_set - new_set):
            dep_removed.append({"packet": pid, "depends_on": dep})

    payload = {
        "old": str(old_file),
        "new": str(new_file),
        "summary": {
            "areas_added": len(area_added),
            "areas_removed": len(area_removed),
            "areas_changed": len(area_changed),
            "packets_added": len(packet_added),
            "packets_removed": len(packet_removed),
            "packets_changed": len(packet_changed),
            "deps_added": len(dep_added),
            "deps_removed": len(dep_removed),
        },
        "areas": {"added": area_added, "removed": area_removed, "changed": area_changed},
        "packets": {"added": packet_added, "removed": packet_removed, "changed": packet_changed},
        "dependencies": {"added": dep_added, "removed": dep_removed},
    }
    if output_json(payload):
        return True

    print("\nWBS Diff")
    print("-" * 80)
    print(f"Old: {old_file}")
    print(f"New: {new_file}")
    print(
        "Summary: "
        + ", ".join(f"{k}={v}" for k, v in payload["summary"].items())
    )
    print("\nAreas")
    print(f"- added: {', '.join(area_added) if area_added else 'none'}")
    print(f"- removed: {', '.join(area_removed) if area_removed else 'none'}")
    print(f"- changed: {', '.join(area_changed) if area_changed else 'none'}")
    print("\nPackets")
    print(f"- added: {', '.join(packet_added) if packet_added else 'none'}")
    print(f"- removed: {', '.join(packet_removed) if packet_removed else 'none'}")
    print(f"- changed: {', '.join(packet_changed) if packet_changed else 'none'}")
    print("\nDependencies")
    if dep_added:
        print("- added:")
        for row in dep_added[:30]:
            print(f"  {row['packet']} -> {row['depends_on']}")
    else:
        print("- added: none")
    if dep_removed:
        print("- removed:")
        for row in dep_removed[:30]:
            print(f"  {row['packet']} -/-> {row['depends_on']}")
    else:
        print("- removed: none")
    print()
    return True


def print_help():
    print("Usage: wbs_cli.py [--json] <command> [args]")
    print()
    print("Commands:")
    print("  init [wbs.json]       Initialize from WBS file (defaults to .governance/wbs.json)")
    print("  init --wizard         Interactive setup")
    print("  plan                  Guided WBS planning and export")
    print("  prd                   Optional PRD ideation + PRD->WBS bridge")
    print("  git-protocol          Show/validate structured governance commit protocol")
    print("  status                Full project status")
    print("  briefing              Session bootstrap summary")
    print("  ready                 List claimable packets")
    print("  next                  Recommended next action")
    print("  scope <id>            Packet details")
    print("  context <id>          Packet context bundle (deps/history/handovers/files)")
    print("  delivery-report [scope] Full delivery report for all|<area>|<packet>")
    print("  progress              Summary counts")
    print("  graph [--output file] ASCII dependency graph (+ optional Graphviz DOT export)")
    print("  wbs-diff <old> <new>  Explain structural diff between two WBS files")
    print("  closeout-readiness <area> Score closeout readiness and blockers for L2 area")
    print("  export <type> <path>  Export state/log/risk/break-fix data (state-json|log-json|log-csv|risk-json|break-fix-json)")
    print("  validate [--strict]   Check WBS structure (strict enforces packet contract)")
    print("  template-validate     Run template integrity checks")
    print("  validate-packet [path] Validate packets against packet schema")
    print("  draft-create [source] [--output path] Create a draft WBS from active/source definition")
    print("  draft-apply <draft> <actor> [notes] Apply draft WBS to active definition (approval required)")
    print("  closeout-l2 <area> <agent> <drift-md> [notes] Close level-2 area with drift assessment")
    print()
    print("  claim <id> <agent>    Claim a packet")
    print("  done <id> <agent> [notes] --risk <none|declared> [--risk-file path|--risk-json json] [--checklist path] [--verify-evidence]")
    print("  note <id> <agent>     Update notes")
    print("  fail <id> <agent>     Mark failed")
    print("  reset <id>            Reset to pending")
    print("  handover <id> <agent> <reason> [--to agent] [--progress text] [--files a,b] [--remaining x|y]")
    print("  resume <id> <agent>   Resume active handover and assign owner")
    print("  stale <minutes> [--warn-factor n] [--critical-factor n] Find stuck packets with severity")
    print("  mode-profile [show|set <mode>] Optional operator mode profile (speed|balanced|strict)")
    print("  log [limit]           Recent activity")
    print("  risk-list [--packet id] [--status status] [--limit n] List residual risks")
    print("  risk-show <risk_id>   Show one residual risk entry")
    print("  risk-add <packet_id> <actor> <description> [--likelihood v] [--impact v] [--confidence v] [--notes text]")
    print("  risk-update-status <risk_id> <status> <actor> [notes] Update risk status")
    print("  risk-summary          Aggregate residual risk counts")
    print("  break-fix-open <actor> <title> <description> [--severity v] [--packet id] [--linked a,b] [--evidence a,b] [--findings x|y]")
    print("  break-fix-start <fix_id> <actor> [--owner id] [--notes text]")
    print("  break-fix-resolve <fix_id> <actor> <summary> --evidence a,b [--findings x|y] [--notes text]")
    print("  break-fix-reject <fix_id> <actor> <reason> [--notes text]")
    print("  break-fix-note <fix_id> <actor> <note> [--evidence a,b] [--findings x|y]")
    print("  break-fix-list [--status s] [--severity s] [--packet id] [--owner id] [--limit n]")
    print("  break-fix-show <fix_id>")
    print("  log-mode <mode>       Set log integrity mode (plain|hash-chain)")
    print("  verify-log            Verify tamper-evident log chain")
    print()
    print("  add-area <id> <title> [desc]       Add work area")
    print("  add-packet <id> <area> <title>     Add packet (scope via stdin or -s, optional --preset)")
    print("  packet-presets                     List optional packet presets")
    print("  add-dep <packet> <depends-on>      Add dependency")
    print("  remove <id> [--force]              Remove packet or area")
    print("  project-show                       Show active project context")
    print("  project-list                       List known projects")
    print("  project-set <id>                   Set active project (approval required)")
    print("  project-create <id> [source]       Create project namespace from source WBS (approval required)")
    print("  agent-list                         Show registered agent profiles and mode")
    print("  agent-mode <disabled|advisory|strict> Set capability enforcement mode")
    print("  agent-register <id> <type> <caps>  Register/update agent (caps comma-separated)")
    print("  git-governance                     Show git-native governance config")
    print("  git-governance-mode <disabled|advisory|strict> Set git-native governance mode")
    print("  git-governance-autocommit <on|off> Toggle git-native auto-commit")
    print("  git-verify-ledger [--strict]       Verify git linkage for lifecycle log entries")
    print("  git-export-ledger <path>           Export git-linked ledger entries as JSON")
    print("  git-reconstruct [--limit N] [--output path] Reconstruct governance protocol commits")
    print("  git-branch-open <packet> <agent> [--from ref] Open packet execution branch")
    print("  git-branch-close <packet> <agent> [--base main] [--keep-branch] Merge/close packet branch")
    print()
    print("Options:")
    print("  --json              Output as JSON (for scripting)")
    print(f"  {WBS_APPROVAL_FLAG} <token>  Approval token for structural WBS mutations")
    print("  --project <id>      Execute command against selected project context")
    print()
    print("Examples:")
    print("  python3 .governance/wbs_cli.py ready")
    print("  python3 .governance/wbs_cli.py plan --from-json docs/wbs-plan.json --output .governance/wbs-draft.json")
    print("  python3 .governance/wbs_cli.py plan --import-markdown docs/project-plan.md --output .governance/wbs-imported.json")
    print("  python3 .governance/wbs_cli.py plan --apply")
    print("  python3 .governance/wbs_cli.py prd --output docs/prd/my-feature-prd.md")
    print("  python3 .governance/wbs_cli.py prd --from-json docs/prd/spec.json --output docs/prd/my-feature-prd.md --to-wbs .governance/wbs-prd-draft.json")
    print("  python3 .governance/wbs_cli.py git-protocol")
    print("  python3 .governance/wbs_cli.py git-protocol --parse /tmp/commit-msg.txt")
    print("  python3 .governance/wbs_cli.py briefing --format json --recent 20")
    print("  python3 .governance/wbs_cli.py delivery-report 7.0")
    print("  python3 .governance/wbs_cli.py wbs-diff .governance/wbs-baseline.json .governance/wbs.json")
    print("  python3 .governance/wbs_cli.py closeout-readiness 7")
    print("  python3 .governance/wbs_cli.py context CDX-3-1 --format json --max-events 30 --max-notes-bytes 4000")
    print("  python3 .governance/wbs_cli.py claim CDX-3-1 codex-lead")
    print("  python3 .governance/wbs_cli.py handover CDX-3-1 codex-lead \"session timeout\" --to codex-2 --remaining \"rerun tests|update docs\"")
    print("  python3 .governance/wbs_cli.py resume CDX-3-1 codex-2")
    print("  python3 .governance/wbs_cli.py mode-profile set strict")
    print("  python3 .governance/wbs_cli.py agent-mode strict")
    print("  python3 .governance/wbs_cli.py agent-register gemini-research llm-gemini \"research,docs\"")
    print("  python3 .governance/wbs_cli.py git-governance")
    print("  python3 .governance/wbs_cli.py git-governance-mode advisory")
    print("  python3 .governance/wbs_cli.py git-governance-autocommit on")
    print("  python3 .governance/wbs_cli.py git-verify-ledger --strict")
    print("  python3 .governance/wbs_cli.py git-export-ledger reports/git-ledger.json")
    print("  python3 .governance/wbs_cli.py git-reconstruct --limit 200 --output reports/git-reconstruct.json")
    print("  python3 .governance/wbs_cli.py git-branch-open UPG-056 codex --from main")
    print("  python3 .governance/wbs_cli.py git-branch-close UPG-056 codex --base main")
    print("  python3 .governance/wbs_cli.py done CDX-3-1 codex-lead \"Implemented changes\" --risk none")
    print("  python3 .governance/wbs_cli.py done CDX-3-2 codex-lead \"Implemented changes\" --risk declared --risk-file docs/risks/rsk-3-2.json")
    print("  python3 .governance/wbs_cli.py risk-list --status open")
    print("  python3 .governance/wbs_cli.py draft-create --output .governance/wbs.draft.json")
    print("  python3 .governance/wbs_cli.py --wbs-approval WBS-APPROVED:GOV-13-4 draft-apply .governance/wbs.draft.json codex \"approved apply\"")
    print("  python3 .governance/wbs_cli.py break-fix-open codex \"Fix flaky smoke\" \"Intermittent server API timeout\" --severity high --packet E2E-6-4")
    print("  python3 .governance/wbs_cli.py break-fix-resolve BFIX-0003 codex \"Adjusted timeout + retries\" --evidence substrate/tests/test_server_api.py,substrate/.governance/wbs_server.py")
    print("  python3 .governance/wbs_cli.py note CDX-3-1 codex-lead \"Evidence: docs/path.md\"")
    print("  python3 .governance/wbs_cli.py closeout-l2 2 codex-lead docs/codex-migration/drift-wbs2.md \"ready for handoff\"")
    print("  python3 .governance/wbs_cli.py packet-presets")
    print()
    print("Notes:")
    print("  reset only applies to in_progress packets")


def main():
    global JSON_OUTPUT, WBS_APPROVAL_TOKEN

    # Parse --json flag
    args = sys.argv[1:]
    if "--json" in args:
        JSON_OUTPUT = True
        args.remove("--json")
    if "--project" in args:
        idx = args.index("--project")
        if idx + 1 >= len(args):
            print("Usage: --project <id>")
            sys.exit(1)
        selected_project = args[idx + 1]
        del args[idx:idx + 2]
        apply_runtime_project(selected_project, persist=False)
    else:
        apply_runtime_project(get_active_project_id(), persist=False)
    if WBS_APPROVAL_FLAG in args:
        idx = args.index(WBS_APPROVAL_FLAG)
        if idx + 1 >= len(args):
            print(f"Usage: {WBS_APPROVAL_FLAG} <token>")
            sys.exit(1)
        WBS_APPROVAL_TOKEN = args[idx + 1]
        del args[idx:idx + 2]

    if len(args) < 1:
        print_help()
        sys.exit(1)

    cmd = args[0]

    try:
        if cmd in ("help", "-h", "--help"):
            print_help()
        elif cmd == "init":
            if len(args) >= 2 and args[1] == "--wizard":
                success = cmd_init_wizard()
            else:
                init_source = args[1] if len(args) >= 2 else str(WBS_DEF)
                success = cmd_init(init_source, approval_token=WBS_APPROVAL_TOKEN)
            if not success:
                sys.exit(1)
        elif cmd == "plan":
            from_json = ""
            import_markdown = ""
            output_path = ""
            apply = False
            allow_ambiguous = False
            extra = args[1:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--apply":
                    apply = True
                    i += 1
                    continue
                if token == "--allow-ambiguous":
                    allow_ambiguous = True
                    i += 1
                    continue
                if token in ("--from-json", "--import-markdown", "--output"):
                    if i + 1 >= len(extra):
                        print(
                            "Usage: wbs_cli.py plan [--from-json spec.json] [--import-markdown plan.md] "
                            "[--output draft.json] [--apply] [--allow-ambiguous]"
                        )
                        sys.exit(1)
                    value = extra[i + 1]
                    if token == "--from-json":
                        from_json = value
                    elif token == "--import-markdown":
                        import_markdown = value
                    else:
                        output_path = value
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py plan [--from-json spec.json] [--import-markdown plan.md] "
                    "[--output draft.json] [--apply] [--allow-ambiguous]"
                )
                sys.exit(1)
            if not cmd_plan(
                from_json=from_json,
                import_markdown=import_markdown,
                output_path=output_path,
                apply=apply,
                allow_ambiguous=allow_ambiguous,
            ):
                sys.exit(1)
        elif cmd == "prd":
            from_json = ""
            output_path = ""
            to_wbs = ""
            apply = False
            allow_ambiguous = False
            extra = args[1:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--apply":
                    apply = True
                    i += 1
                    continue
                if token == "--allow-ambiguous":
                    allow_ambiguous = True
                    i += 1
                    continue
                if token in ("--from-json", "--output", "--to-wbs"):
                    if i + 1 >= len(extra):
                        print(
                            "Usage: wbs_cli.py prd [--from-json spec.json] [--output prd.md] "
                            "[--to-wbs wbs.json] [--apply] [--allow-ambiguous]"
                        )
                        sys.exit(1)
                    value = extra[i + 1]
                    if token == "--from-json":
                        from_json = value
                    elif token == "--output":
                        output_path = value
                    else:
                        to_wbs = value
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py prd [--from-json spec.json] [--output prd.md] "
                    "[--to-wbs wbs.json] [--apply] [--allow-ambiguous]"
                )
                sys.exit(1)
            if not cmd_prd(
                from_json=from_json,
                output_path=output_path,
                to_wbs=to_wbs,
                apply=apply,
                allow_ambiguous=allow_ambiguous,
            ):
                sys.exit(1)
        elif cmd == "git-protocol":
            parse_path = ""
            extra = args[1:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--parse":
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py git-protocol [--parse path/to/commit-msg.txt]")
                        sys.exit(1)
                    parse_path = extra[i + 1]
                    i += 2
                    continue
                print("Usage: wbs_cli.py git-protocol [--parse path/to/commit-msg.txt]")
                sys.exit(1)
            if not cmd_git_protocol(parse_path=parse_path):
                sys.exit(1)
        elif cmd == "status":
            if require_state(): cmd_status()
        elif cmd == "briefing":
            output_format = "text"
            compact = False
            recent_events = 10
            extra = args[1:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--compact":
                    compact = True
                    i += 1
                    continue
                if token == "--format":
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py briefing [--format json|text] [--compact] [--recent N]")
                        sys.exit(1)
                    output_format = extra[i + 1].strip().lower()
                    if output_format not in ("json", "text"):
                        print("briefing --format must be one of: json, text")
                        sys.exit(1)
                    i += 2
                    continue
                if token == "--recent":
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py briefing [--format json|text] [--compact] [--recent N]")
                        sys.exit(1)
                    recent_events = int(extra[i + 1])
                    i += 2
                    continue
                print("Usage: wbs_cli.py briefing [--format json|text] [--compact] [--recent N]")
                sys.exit(1)
            if require_state():
                cmd_briefing(output_format=output_format, compact=compact, recent_events=recent_events)
        elif cmd == "ready":
            if require_state(): cmd_ready()
        elif cmd == "next":
            if require_state(): cmd_next()
        elif cmd == "progress":
            if require_state(): cmd_progress()
        elif cmd == "scope":
            if len(args) < 2:
                print("Usage: wbs_cli.py scope <packet_id>")
                sys.exit(1)
            if require_state(): cmd_scope(args[1])
        elif cmd == "context":
            if len(args) < 2:
                print(
                    "Usage: wbs_cli.py context <packet_id> [--format json|text] [--compact] "
                    "[--max-events N] [--max-notes-bytes N] [--max-handovers N]"
                )
                sys.exit(1)
            packet_id = args[1]
            output_format = "text"
            compact = False
            max_events = 40
            max_notes_bytes = 4000
            max_handovers = 40
            extra = args[2:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--compact":
                    compact = True
                    i += 1
                    continue
                if token in ("--format", "--max-events", "--max-notes-bytes", "--max-handovers"):
                    if i + 1 >= len(extra):
                        print(
                            "Usage: wbs_cli.py context <packet_id> [--format json|text] [--compact] "
                            "[--max-events N] [--max-notes-bytes N] [--max-handovers N]"
                        )
                        sys.exit(1)
                    value = extra[i + 1]
                    if token == "--format":
                        output_format = value.strip().lower()
                        if output_format not in ("json", "text"):
                            print("context --format must be one of: json, text")
                            sys.exit(1)
                    elif token == "--max-events":
                        max_events = int(value)
                    elif token == "--max-notes-bytes":
                        max_notes_bytes = int(value)
                    elif token == "--max-handovers":
                        max_handovers = int(value)
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py context <packet_id> [--format json|text] [--compact] "
                    "[--max-events N] [--max-notes-bytes N] [--max-handovers N]"
                )
                sys.exit(1)
            if require_state() and not cmd_context(
                packet_id=packet_id,
                output_format=output_format,
                compact=compact,
                max_events=max_events,
                max_notes_bytes=max_notes_bytes,
                max_handovers=max_handovers,
            ):
                sys.exit(1)
        elif cmd == "delivery-report":
            scope = args[1] if len(args) > 1 else "all"
            if require_state() and not cmd_delivery_report(scope):
                sys.exit(1)
        elif cmd == "claim":
            if len(args) < 3:
                print("Usage: wbs_cli.py claim <packet_id> <agent>")
                sys.exit(1)
            if require_state() and not cmd_claim(args[1], args[2]):
                sys.exit(1)
        elif cmd == "done":
            if len(args) < 3:
                print("Usage: wbs_cli.py done <packet_id> <agent> [notes] --risk <none|declared> [--risk-file path|--risk-json json] [--checklist path] [--verify-evidence]")
                sys.exit(1)
            packet_id = args[1]
            agent = args[2]
            notes = ""
            risk_ack = ""
            risk_file = ""
            risk_json = ""
            checklist_path = ""
            verify_evidence = False
            i = 3
            while i < len(args):
                token = args[i]
                if token == "--verify-evidence":
                    verify_evidence = True
                    i += 1
                    continue
                if token in ("--risk", "--risk-file", "--risk-json", "--checklist"):
                    if i + 1 >= len(args):
                        print("Usage: wbs_cli.py done <packet_id> <agent> [notes] --risk <none|declared> [--risk-file path|--risk-json json] [--checklist path] [--verify-evidence]")
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--risk":
                        risk_ack = value
                    elif token == "--risk-file":
                        risk_file = value
                    elif token == "--risk-json":
                        risk_json = value
                    elif token == "--checklist":
                        checklist_path = value
                    i += 2
                    continue
                if notes:
                    print("Usage: wbs_cli.py done <packet_id> <agent> [notes] --risk <none|declared> [--risk-file path|--risk-json json] [--checklist path] [--verify-evidence]")
                    sys.exit(1)
                notes = token
                i += 1

            if bool(risk_file) and bool(risk_json):
                print("Use either --risk-file or --risk-json, not both.")
                sys.exit(1)

            parsed_risks = []
            if risk_file:
                try:
                    parsed_risks = _load_risk_entries_from_file(risk_file)
                except ValueError as e:
                    print(red(str(e)))
                    sys.exit(1)
            elif risk_json:
                try:
                    parsed_risks = _load_risk_entries_from_json(risk_json)
                except ValueError as e:
                    print(red(str(e)))
                    sys.exit(1)

            if require_state() and not cmd_done(
                packet_id,
                agent,
                notes,
                risk_ack=risk_ack,
                risk_entries=parsed_risks,
                checklist_path=checklist_path,
                verify_evidence=verify_evidence,
            ):
                sys.exit(1)
        elif cmd == "note":
            if len(args) < 4:
                print("Usage: wbs_cli.py note <packet_id> <agent> <notes>")
                sys.exit(1)
            notes = args[3]
            if require_state() and not cmd_note(args[1], args[2], notes):
                sys.exit(1)
        elif cmd == "fail":
            if len(args) < 3:
                print("Usage: wbs_cli.py fail <packet_id> <agent> [reason]")
                sys.exit(1)
            reason = args[3] if len(args) > 3 else ""
            if require_state() and not cmd_fail(args[1], args[2], reason):
                sys.exit(1)
        elif cmd == "reset":
            if len(args) < 2:
                print("Usage: wbs_cli.py reset <packet_id>")
                sys.exit(1)
            if require_state() and not cmd_reset(args[1]):
                sys.exit(1)
        elif cmd == "handover":
            if len(args) < 4:
                print(
                    "Usage: wbs_cli.py handover <packet_id> <agent> <reason> "
                    "[--to agent] [--progress text] [--files a,b] [--remaining x|y]"
                )
                sys.exit(1)
            packet_id = args[1]
            agent = args[2]
            reason = args[3]
            to_agent = ""
            progress_notes = ""
            files_modified = []
            remaining_work = []
            extra = args[4:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token in ("--to", "--progress", "--files", "--remaining"):
                    if i + 1 >= len(extra):
                        print(
                            "Usage: wbs_cli.py handover <packet_id> <agent> <reason> "
                            "[--to agent] [--progress text] [--files a,b] [--remaining x|y]"
                        )
                        sys.exit(1)
                    value = extra[i + 1]
                    if token == "--to":
                        to_agent = value
                    elif token == "--progress":
                        progress_notes = value
                    elif token == "--files":
                        files_modified = [item.strip() for item in value.split(",") if item.strip()]
                    elif token == "--remaining":
                        remaining_work = [item.strip() for item in value.split("|") if item.strip()]
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py handover <packet_id> <agent> <reason> "
                    "[--to agent] [--progress text] [--files a,b] [--remaining x|y]"
                )
                sys.exit(1)
            if require_state() and not cmd_handover(
                packet_id,
                agent,
                reason,
                progress_notes=progress_notes,
                files_modified=files_modified,
                remaining_work=remaining_work,
                to_agent=to_agent,
            ):
                sys.exit(1)
        elif cmd == "resume":
            if len(args) < 3:
                print("Usage: wbs_cli.py resume <packet_id> <agent>")
                sys.exit(1)
            if require_state() and not cmd_resume(args[1], args[2]):
                sys.exit(1)
        elif cmd == "stale":
            if len(args) < 2:
                print("Usage: wbs_cli.py stale <minutes> [--warn-factor n] [--critical-factor n]")
                sys.exit(1)
            minutes = int(args[1])
            warn_factor = None
            critical_factor = None
            extra = args[2:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token in ("--warn-factor", "--critical-factor"):
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py stale <minutes> [--warn-factor n] [--critical-factor n]")
                        sys.exit(1)
                    value = float(extra[i + 1])
                    if token == "--warn-factor":
                        warn_factor = value
                    else:
                        critical_factor = value
                    i += 2
                    continue
                print("Usage: wbs_cli.py stale <minutes> [--warn-factor n] [--critical-factor n]")
                sys.exit(1)
            if require_state() and not cmd_stale(minutes, warn_factor=warn_factor, critical_factor=critical_factor):
                sys.exit(1)
        elif cmd == "mode-profile":
            if len(args) == 1:
                if require_state() and not cmd_mode_profile("show"):
                    sys.exit(1)
            elif len(args) >= 2 and args[1] == "show":
                if require_state() and not cmd_mode_profile("show"):
                    sys.exit(1)
            elif len(args) >= 3 and args[1] == "set":
                if require_state() and not cmd_mode_profile("set", args[2]):
                    sys.exit(1)
            else:
                print("Usage: wbs_cli.py mode-profile [show|set <speed|balanced|strict>]")
                sys.exit(1)
        elif cmd == "log":
            limit = int(args[1]) if len(args) > 1 else 20
            if require_state(): cmd_log(limit)
        elif cmd == "risk-list":
            packet_id = ""
            status = ""
            limit = 100
            i = 1
            while i < len(args):
                token = args[i]
                if token in ("--packet", "--status", "--limit"):
                    if i + 1 >= len(args):
                        print("Usage: wbs_cli.py risk-list [--packet id] [--status status] [--limit n]")
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--packet":
                        packet_id = value
                    elif token == "--status":
                        status = value
                    else:
                        limit = int(value)
                    i += 2
                    continue
                print("Usage: wbs_cli.py risk-list [--packet id] [--status status] [--limit n]")
                sys.exit(1)
            if not cmd_risk_list(packet_id=packet_id, status=status, limit=limit):
                sys.exit(1)
        elif cmd == "risk-show":
            if len(args) < 2:
                print("Usage: wbs_cli.py risk-show <risk_id>")
                sys.exit(1)
            if not cmd_risk_show(args[1]):
                sys.exit(1)
        elif cmd == "risk-add":
            if len(args) < 4:
                print("Usage: wbs_cli.py risk-add <packet_id> <actor> <description> [--likelihood v] [--impact v] [--confidence v] [--notes text]")
                sys.exit(1)
            packet_id = args[1]
            actor = args[2]
            description = args[3]
            likelihood = "medium"
            impact = "medium"
            confidence = "medium"
            notes = ""
            i = 4
            while i < len(args):
                token = args[i]
                if token in ("--likelihood", "--impact", "--confidence", "--notes"):
                    if i + 1 >= len(args):
                        print("Usage: wbs_cli.py risk-add <packet_id> <actor> <description> [--likelihood v] [--impact v] [--confidence v] [--notes text]")
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--likelihood":
                        likelihood = value
                    elif token == "--impact":
                        impact = value
                    elif token == "--confidence":
                        confidence = value
                    else:
                        notes = value
                    i += 2
                    continue
                print("Usage: wbs_cli.py risk-add <packet_id> <actor> <description> [--likelihood v] [--impact v] [--confidence v] [--notes text]")
                sys.exit(1)
            if not cmd_risk_add(packet_id, actor, description, likelihood, impact, confidence, notes):
                sys.exit(1)
        elif cmd == "risk-update-status":
            if len(args) < 4:
                print("Usage: wbs_cli.py risk-update-status <risk_id> <status> <actor> [notes]")
                sys.exit(1)
            notes = args[4] if len(args) > 4 else ""
            if not cmd_risk_update_status(args[1], args[2], args[3], notes):
                sys.exit(1)
        elif cmd == "risk-summary":
            if not cmd_risk_summary():
                sys.exit(1)
        elif cmd == "break-fix-open":
            if len(args) < 4:
                print(
                    "Usage: wbs_cli.py break-fix-open <actor> <title> <description> "
                    "[--severity v] [--packet id] [--linked a,b] [--evidence a,b] [--findings x|y]"
                )
                sys.exit(1)
            actor = args[1]
            title = args[2]
            description = args[3]
            severity = "medium"
            packet_id = ""
            linked = []
            evidence = []
            findings = []
            i = 4
            while i < len(args):
                token = args[i]
                if token in ("--severity", "--packet", "--linked", "--evidence", "--findings"):
                    if i + 1 >= len(args):
                        print(
                            "Usage: wbs_cli.py break-fix-open <actor> <title> <description> "
                            "[--severity v] [--packet id] [--linked a,b] [--evidence a,b] [--findings x|y]"
                        )
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--severity":
                        severity = value
                    elif token == "--packet":
                        packet_id = value
                    elif token == "--linked":
                        linked = _parse_csv_items(value)
                    elif token == "--evidence":
                        evidence = _parse_csv_items(value)
                    elif token == "--findings":
                        findings = _parse_pipe_items(value)
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py break-fix-open <actor> <title> <description> "
                    "[--severity v] [--packet id] [--linked a,b] [--evidence a,b] [--findings x|y]"
                )
                sys.exit(1)
            if not cmd_break_fix_open(
                actor=actor,
                title=title,
                description=description,
                severity=severity,
                packet_id=packet_id,
                linked_packets=linked,
                evidence=evidence,
                findings=findings,
            ):
                sys.exit(1)
        elif cmd == "break-fix-start":
            if len(args) < 3:
                print("Usage: wbs_cli.py break-fix-start <fix_id> <actor> [--owner id] [--notes text]")
                sys.exit(1)
            fix_id = args[1]
            actor = args[2]
            owner = ""
            notes = ""
            i = 3
            while i < len(args):
                token = args[i]
                if token in ("--owner", "--notes"):
                    if i + 1 >= len(args):
                        print("Usage: wbs_cli.py break-fix-start <fix_id> <actor> [--owner id] [--notes text]")
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--owner":
                        owner = value
                    else:
                        notes = value
                    i += 2
                    continue
                print("Usage: wbs_cli.py break-fix-start <fix_id> <actor> [--owner id] [--notes text]")
                sys.exit(1)
            if not cmd_break_fix_start(fix_id, actor, owner=owner, notes=notes):
                sys.exit(1)
        elif cmd == "break-fix-resolve":
            if len(args) < 4:
                print(
                    "Usage: wbs_cli.py break-fix-resolve <fix_id> <actor> <summary> "
                    "--evidence a,b [--findings x|y] [--notes text]"
                )
                sys.exit(1)
            fix_id = args[1]
            actor = args[2]
            summary = args[3]
            evidence = []
            findings = []
            notes = ""
            i = 4
            while i < len(args):
                token = args[i]
                if token in ("--evidence", "--findings", "--notes"):
                    if i + 1 >= len(args):
                        print(
                            "Usage: wbs_cli.py break-fix-resolve <fix_id> <actor> <summary> "
                            "--evidence a,b [--findings x|y] [--notes text]"
                        )
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--evidence":
                        evidence = _parse_csv_items(value)
                    elif token == "--findings":
                        findings = _parse_pipe_items(value)
                    else:
                        notes = value
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py break-fix-resolve <fix_id> <actor> <summary> "
                    "--evidence a,b [--findings x|y] [--notes text]"
                )
                sys.exit(1)
            if not evidence:
                print(red("break-fix-resolve requires --evidence a,b"))
                sys.exit(1)
            if not cmd_break_fix_resolve(fix_id, actor, summary, evidence=evidence, findings=findings, notes=notes):
                sys.exit(1)
        elif cmd == "break-fix-reject":
            if len(args) < 4:
                print("Usage: wbs_cli.py break-fix-reject <fix_id> <actor> <reason> [--notes text]")
                sys.exit(1)
            fix_id = args[1]
            actor = args[2]
            reason = args[3]
            notes = ""
            i = 4
            while i < len(args):
                token = args[i]
                if token == "--notes":
                    if i + 1 >= len(args):
                        print("Usage: wbs_cli.py break-fix-reject <fix_id> <actor> <reason> [--notes text]")
                        sys.exit(1)
                    notes = args[i + 1]
                    i += 2
                    continue
                print("Usage: wbs_cli.py break-fix-reject <fix_id> <actor> <reason> [--notes text]")
                sys.exit(1)
            if not cmd_break_fix_reject(fix_id, actor, reason, notes=notes):
                sys.exit(1)
        elif cmd == "break-fix-note":
            if len(args) < 4:
                print("Usage: wbs_cli.py break-fix-note <fix_id> <actor> <note> [--evidence a,b] [--findings x|y]")
                sys.exit(1)
            fix_id = args[1]
            actor = args[2]
            notes = args[3]
            evidence = []
            findings = []
            i = 4
            while i < len(args):
                token = args[i]
                if token in ("--evidence", "--findings"):
                    if i + 1 >= len(args):
                        print("Usage: wbs_cli.py break-fix-note <fix_id> <actor> <note> [--evidence a,b] [--findings x|y]")
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--evidence":
                        evidence = _parse_csv_items(value)
                    else:
                        findings = _parse_pipe_items(value)
                    i += 2
                    continue
                print("Usage: wbs_cli.py break-fix-note <fix_id> <actor> <note> [--evidence a,b] [--findings x|y]")
                sys.exit(1)
            if not cmd_break_fix_note(fix_id, actor, notes, evidence=evidence, findings=findings):
                sys.exit(1)
        elif cmd == "break-fix-list":
            status = ""
            severity = ""
            packet_id = ""
            owner = ""
            limit = 100
            i = 1
            while i < len(args):
                token = args[i]
                if token in ("--status", "--severity", "--packet", "--owner", "--limit"):
                    if i + 1 >= len(args):
                        print(
                            "Usage: wbs_cli.py break-fix-list [--status s] [--severity s] "
                            "[--packet id] [--owner id] [--limit n]"
                        )
                        sys.exit(1)
                    value = args[i + 1]
                    if token == "--status":
                        status = value
                    elif token == "--severity":
                        severity = value
                    elif token == "--packet":
                        packet_id = value
                    elif token == "--owner":
                        owner = value
                    else:
                        limit = int(value)
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py break-fix-list [--status s] [--severity s] "
                    "[--packet id] [--owner id] [--limit n]"
                )
                sys.exit(1)
            if not cmd_break_fix_list(status=status, severity=severity, packet_id=packet_id, owner=owner, limit=limit):
                sys.exit(1)
        elif cmd == "break-fix-show":
            if len(args) < 2:
                print("Usage: wbs_cli.py break-fix-show <fix_id>")
                sys.exit(1)
            if not cmd_break_fix_show(args[1]):
                sys.exit(1)
        elif cmd == "log-mode":
            if len(args) < 2:
                print("Usage: wbs_cli.py log-mode <plain|hash-chain>")
                sys.exit(1)
            if require_state() and not cmd_log_mode(args[1]):
                sys.exit(1)
        elif cmd == "verify-log":
            if require_state() and not cmd_verify_log():
                sys.exit(1)
        elif cmd == "graph":
            output = ""
            if "--output" in args:
                idx = args.index("--output")
                if idx + 1 >= len(args):
                    print("Usage: wbs_cli.py graph [--output deps.dot]")
                    sys.exit(1)
                output = args[idx + 1]
            if require_state(): cmd_graph(output)
        elif cmd == "wbs-diff":
            if len(args) < 3:
                print("Usage: wbs_cli.py wbs-diff <old_wbs.json> <new_wbs.json>")
                sys.exit(1)
            if not cmd_wbs_diff(args[1], args[2]):
                sys.exit(1)
        elif cmd == "export":
            if len(args) < 3:
                print("Usage: wbs_cli.py export <state-json|log-json|log-csv|risk-json|break-fix-json> <path>")
                sys.exit(1)
            if require_state() and not cmd_export(args[1], args[2]):
                sys.exit(1)
        elif cmd == "validate":
            extra = [arg for arg in args[1:] if arg != "--strict"]
            if extra:
                print("Usage: wbs_cli.py validate [--strict]")
                sys.exit(1)
            strict = "--strict" in args[1:]
            if not cmd_validate(strict=strict):
                sys.exit(1)
        elif cmd == "template-validate":
            if len(args) != 1:
                print("Usage: wbs_cli.py template-validate")
                sys.exit(1)
            if not cmd_template_validate():
                sys.exit(1)
        elif cmd == "validate-packet":
            target = args[1] if len(args) > 1 else ""
            if not cmd_validate_packet(target):
                sys.exit(1)
        elif cmd == "draft-create":
            source = ""
            output = ""
            extra = args[1:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--output":
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py draft-create [source] [--output path]")
                        sys.exit(1)
                    output = extra[i + 1]
                    i += 2
                    continue
                if source:
                    print("Usage: wbs_cli.py draft-create [source] [--output path]")
                    sys.exit(1)
                source = token
                i += 1
            if not cmd_draft_create(source_path=source, output_path=output):
                sys.exit(1)
        elif cmd == "draft-apply":
            if len(args) < 3:
                print("Usage: wbs_cli.py draft-apply <draft_path> <actor> [notes]")
                sys.exit(1)
            notes = args[3] if len(args) > 3 else ""
            if not cmd_draft_apply(args[1], args[2], notes=notes, approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "closeout-l2":
            if len(args) < 4:
                print("Usage: wbs_cli.py closeout-l2 <area_id|n> <agent> <drift_assessment.md> [notes]")
                sys.exit(1)
            notes = args[4] if len(args) > 4 else ""
            if require_state() and not cmd_closeout_l2(args[1], args[2], args[3], notes):
                sys.exit(1)
        elif cmd == "closeout-readiness":
            if len(args) < 2:
                print("Usage: wbs_cli.py closeout-readiness <area_id|n>")
                sys.exit(1)
            if require_state() and not cmd_closeout_readiness(args[1]):
                sys.exit(1)
        elif cmd == "add-area":
            if len(args) < 3:
                print("Usage: wbs_cli.py add-area <id> <title> [description]")
                sys.exit(1)
            desc = args[3] if len(args) > 3 else ""
            if not cmd_add_area(args[1], args[2], desc, approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "add-packet":
            if len(args) < 4:
                print("Usage: wbs_cli.py add-packet <id> <area> <title> [-s scope | --scope scope] [--preset name]")
                print("       Or pipe scope via stdin")
                sys.exit(1)
            pid, area, title = args[1], args[2], args[3]
            scope = ""
            preset = ""
            # Check for -s or --scope flag
            if "-s" in args:
                idx = args.index("-s")
                scope = args[idx + 1] if idx + 1 < len(args) else ""
            elif "--scope" in args:
                idx = args.index("--scope")
                scope = args[idx + 1] if idx + 1 < len(args) else ""
            if "--preset" in args:
                idx = args.index("--preset")
                preset = args[idx + 1] if idx + 1 < len(args) else ""
            elif not sys.stdin.isatty():
                scope = sys.stdin.read().strip()
            if not scope:
                print("Enter scope (Ctrl+D when done):")
                try:
                    scope = sys.stdin.read().strip()
                except:
                    scope = ""
            if not cmd_add_packet(pid, area, title, scope, preset=preset, approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "packet-presets":
            if not cmd_packet_presets():
                sys.exit(1)
        elif cmd == "add-dep":
            if len(args) < 3:
                print("Usage: wbs_cli.py add-dep <packet> <depends-on>")
                sys.exit(1)
            if not cmd_add_dep(args[1], args[2], approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "remove":
            if len(args) < 2:
                print("Usage: wbs_cli.py remove <id> [--force]")
                sys.exit(1)
            force = "--force" in args
            if not cmd_remove(args[1], force, approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "project-show":
            if not cmd_project_show():
                sys.exit(1)
        elif cmd == "project-list":
            if not cmd_project_list():
                sys.exit(1)
        elif cmd == "project-set":
            if len(args) < 2:
                print("Usage: wbs_cli.py project-set <project_id>")
                sys.exit(1)
            if not cmd_project_set(args[1], approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "project-create":
            if len(args) < 2:
                print("Usage: wbs_cli.py project-create <project_id> [source_wbs_path]")
                sys.exit(1)
            source = args[2] if len(args) > 2 else ""
            if not cmd_project_create(args[1], source_path=source, approval_token=WBS_APPROVAL_TOKEN):
                sys.exit(1)
        elif cmd == "agent-list":
            if not cmd_agent_list():
                sys.exit(1)
        elif cmd == "agent-mode":
            if len(args) < 2:
                print("Usage: wbs_cli.py agent-mode <disabled|advisory|strict>")
                sys.exit(1)
            if not cmd_agent_mode(args[1]):
                sys.exit(1)
        elif cmd == "agent-register":
            if len(args) < 4:
                print("Usage: wbs_cli.py agent-register <agent_id> <agent_type> <cap1,cap2,...>")
                sys.exit(1)
            if not cmd_agent_register(args[1], args[2], args[3]):
                sys.exit(1)
        elif cmd == "git-governance":
            if not cmd_git_governance():
                sys.exit(1)
        elif cmd == "git-governance-mode":
            if len(args) < 2:
                print("Usage: wbs_cli.py git-governance-mode <disabled|advisory|strict>")
                sys.exit(1)
            if not cmd_git_governance_mode(args[1]):
                sys.exit(1)
        elif cmd == "git-governance-autocommit":
            if len(args) < 2:
                print("Usage: wbs_cli.py git-governance-autocommit <on|off>")
                sys.exit(1)
            if not cmd_git_governance_autocommit(args[1]):
                sys.exit(1)
        elif cmd == "git-verify-ledger":
            strict = "--strict" in args[1:]
            extra = [arg for arg in args[1:] if arg != "--strict"]
            if extra:
                print("Usage: wbs_cli.py git-verify-ledger [--strict]")
                sys.exit(1)
            if not cmd_git_verify_ledger(strict=strict):
                sys.exit(1)
        elif cmd == "git-export-ledger":
            if len(args) < 2:
                print("Usage: wbs_cli.py git-export-ledger <path>")
                sys.exit(1)
            if not cmd_git_export_ledger(args[1]):
                sys.exit(1)
        elif cmd == "git-reconstruct":
            limit = 500
            output_path = ""
            extra = args[1:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token in ("--limit", "--output"):
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py git-reconstruct [--limit N] [--output path]")
                        sys.exit(1)
                    value = extra[i + 1]
                    if token == "--limit":
                        limit = int(value)
                    else:
                        output_path = value
                    i += 2
                    continue
                print("Usage: wbs_cli.py git-reconstruct [--limit N] [--output path]")
                sys.exit(1)
            if not cmd_git_reconstruct(limit=limit, out_path=output_path):
                sys.exit(1)
        elif cmd == "git-branch-open":
            if len(args) < 3:
                print("Usage: wbs_cli.py git-branch-open <packet_id> <agent> [--from ref]")
                sys.exit(1)
            packet_id = args[1]
            agent = args[2]
            from_ref = ""
            extra = args[3:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--from":
                    if i + 1 >= len(extra):
                        print("Usage: wbs_cli.py git-branch-open <packet_id> <agent> [--from ref]")
                        sys.exit(1)
                    from_ref = extra[i + 1]
                    i += 2
                    continue
                print("Usage: wbs_cli.py git-branch-open <packet_id> <agent> [--from ref]")
                sys.exit(1)
            if not cmd_git_branch_open(packet_id, agent, from_ref=from_ref):
                sys.exit(1)
        elif cmd == "git-branch-close":
            if len(args) < 3:
                print(
                    "Usage: wbs_cli.py git-branch-close <packet_id> <agent> "
                    "[--base main] [--keep-branch]"
                )
                sys.exit(1)
            packet_id = args[1]
            agent = args[2]
            base_branch = "main"
            delete_branch = True
            extra = args[3:]
            i = 0
            while i < len(extra):
                token = extra[i]
                if token == "--keep-branch":
                    delete_branch = False
                    i += 1
                    continue
                if token == "--base":
                    if i + 1 >= len(extra):
                        print(
                            "Usage: wbs_cli.py git-branch-close <packet_id> <agent> "
                            "[--base main] [--keep-branch]"
                        )
                        sys.exit(1)
                    base_branch = extra[i + 1]
                    i += 2
                    continue
                print(
                    "Usage: wbs_cli.py git-branch-close <packet_id> <agent> "
                    "[--base main] [--keep-branch]"
                )
                sys.exit(1)
            if not cmd_git_branch_close(
                packet_id,
                agent,
                base_branch=base_branch,
                delete_branch=delete_branch,
            ):
                sys.exit(1)
        else:
            print(red(f"Unknown command: {cmd}"))
            sys.exit(1)
    except Exception as e:
        print(red(f"Error: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
