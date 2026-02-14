#!/usr/bin/env python3
"""
WBS Orchestration CLI — JSON-based state management.
Simple, readable, git-friendly.
"""

import json
import sys
import csv
from pathlib import Path
try:
    import fcntl
except ImportError:
    fcntl = None
from datetime import datetime
from typing import Optional

from wbs_common import (
    GOV, WBS_DEF, WBS_STATE,
    green, red, yellow, bold, dim,
    load_definition, load_state, get_counts
)

SRC_PATH = GOV.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from governed_platform.governance.engine import GovernanceEngine
from governed_platform.governance.state_manager import StateManager
from governed_platform.governance.schema_registry import SchemaRegistry

# Global flags
JSON_OUTPUT = False
PACKET_SCHEMA_PATH = GOV / "packet-schema.json"
SCHEMA_REGISTRY_PATH = GOV / "schema-registry.json"

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

PACKET_STATUS_VALUES = {"DRAFT", "PENDING", "IN_PROGRESS", "BLOCKED", "DONE", "FAILED"}
PACKET_PRIORITY_VALUES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
REQUIRED_DRIFT_SECTIONS = [
    "## Scope Reviewed",
    "## Expected vs Delivered",
    "## Drift Assessment",
    "## Evidence Reviewed",
    "## Residual Risks",
    "## Immediate Next Actions",
]

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


def _format_error(message: str) -> str:
    """Attach stable error code and action guidance to known failure patterns."""
    text = (message or "").strip()
    lower = text.lower()
    for pattern, code, hint in ERROR_HINTS:
        if pattern in lower:
            return f"[{code}] {text}\nAction: {hint}"
    return text


def enforce_schema_contracts() -> tuple:
    """Enforce schema registry contract at runtime boundaries."""
    if not SCHEMA_REGISTRY_PATH.exists():
        return False, f"Schema registry missing: {SCHEMA_REGISTRY_PATH}"
    try:
        reg = SchemaRegistry.from_registry_file(SCHEMA_REGISTRY_PATH, root=GOV.parent)
    except Exception as e:
        return False, f"Schema registry load failed: {e}"
    try:
        packet_ok = reg.validate_version("packet", "1.0")
        packet_schema = reg.get("packet")
    except Exception as e:
        return False, f"Schema registry invalid: {e}"
    if not packet_ok:
        return False, "Schema registry version mismatch for packet"
    if not packet_schema.path.exists():
        return False, f"Registered packet schema not found: {packet_schema.path}"
    return True, "ok"


def ensure_state_shape(state: dict) -> dict:
    """Ensure optional top-level state keys exist."""
    state.setdefault("packets", {})
    state.setdefault("log", [])
    state.setdefault("area_closeouts", {})
    return state


def save_state(state: dict):
    """Save state with file locking."""
    tmp = WBS_STATE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        if fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(state, f, indent=2)
        f.write("\n")
    tmp.replace(WBS_STATE)


def governance_engine() -> GovernanceEngine:
    """Build governance engine from current definition and state path."""
    definition = load_definition()
    sm = StateManager(WBS_STATE)
    state = sm.load()
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


def cmd_init(wbs_path: str) -> bool:
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
    if Path(wbs_path).resolve() != WBS_DEF.resolve():
        with open(WBS_DEF, "w") as f:
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

    with open(WBS_DEF, "w") as f:
        json.dump(definition, f, indent=2)
        f.write("\n")

    print(green(f"\nCreated {WBS_DEF}"))
    return cmd_init(str(WBS_DEF))


def check_deps_met(packet_id: str, definition: dict, state: dict) -> tuple:
    """Check if all dependencies are done. Returns (ready, blocking_id)."""
    deps = definition.get("dependencies", {}).get(packet_id, [])
    for dep_id in deps:
        dep_state = state["packets"].get(dep_id, {})
        if dep_state.get("status") != "done":
            return False, dep_id
    return True, None


def cmd_claim(packet_id: str, agent: str) -> bool:
    """Claim a packet."""
    ok, msg = governance_engine().claim(packet_id, agent)
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_done(packet_id: str, agent: str, notes: str = "") -> bool:
    """Mark packet done."""
    ok, msg = governance_engine().done(packet_id, agent, notes)
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_note(packet_id: str, agent: str, notes: str) -> bool:
    """Update notes for any existing packet state."""
    ok, msg = governance_engine().note(packet_id, agent, notes)
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_fail(packet_id: str, agent: str, reason: str = "") -> bool:
    """Mark packet failed and block downstream."""
    ok, msg = governance_engine().fail(packet_id, agent, reason)
    if ok:
        print(yellow(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_reset(packet_id: str) -> bool:
    """Reset packet to pending."""
    ok, msg = governance_engine().reset(packet_id)
    if ok:
        print(green(msg))
    else:
        print(red(_format_error(msg)))
    return ok


def cmd_ready():
    """List packets ready to claim."""
    definition = load_definition()
    state = ensure_state_shape(load_state())

    packets = definition.get("packets", [])
    ready = []
    for pkt in packets:
        pid = pkt["id"]
        if state["packets"].get(pid, {}).get("status") == "pending":
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
                        "status": ps.get("status", "pending"), "assigned_to": ps.get("assigned_to"),
                        "notes": ps.get("notes")
                    })
            areas.append({
                "id": area["id"],
                "title": area["title"],
                "packets": pkts,
                "closeout": state.get("area_closeouts", {}).get(area["id"])
            })
        output_json({"metadata": definition.get("metadata", {}), "areas": areas, "counts": get_counts(state)})
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
                status = pstate.get("status", "pending").upper()
                assigned = pstate.get("assigned_to") or "-"

                status_color = {"DONE": green, "FAILED": red, "BLOCKED": red, "IN_PROGRESS": yellow}.get(status, dim)
                print(f"  {pid:<10} {pkt['wbs_ref']:<6} {status_color(status):<14} {assigned:<12} {pkt['title'][:30]}")
        print()

    # Summary
    counts = get_counts(state)
    print(f"{'=' * 70}")
    print("Summary:", ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
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
    print(f"Status: {pstate.get('status', 'pending')}")
    if pstate.get("assigned_to"):
        print(f"Assigned: {pstate['assigned_to']}")
    if deps:
        print(f"Depends on: {', '.join(deps)}")
    print(f"\nScope:\n{pkt['scope']}")
    print()


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


def cmd_next():
    """Show recommended next action."""
    definition = load_definition()
    state = ensure_state_shape(load_state())

    # Check for in-progress
    for pkt in definition.get("packets", []):
        pid = pkt["id"]
        if state["packets"].get(pid, {}).get("status") == "in_progress":
            agent = state["packets"][pid].get("assigned_to", "your-name")
            print("Next action:")
            print(f"  python3 .governance/wbs_cli.py done {pid} {agent} \"notes\"")
            print(f"Reason: {pid} is in progress")
            return

    # Check for ready
    for pkt in definition.get("packets", []):
        pid = pkt["id"]
        if state["packets"].get(pid, {}).get("status") == "pending":
            ok, _ = check_deps_met(pid, definition, state)
            if ok:
                print("Next action:")
                print(f"  python3 .governance/wbs_cli.py claim {pid} your-name")
                print(f"Reason: {pid} is ready ({pkt['title']})")
                return

    # Check completion
    done = sum(1 for p in state["packets"].values() if p.get("status") == "done")
    total = len(state["packets"])

    if done == total and total > 0:
        print("Next action: None — all packets complete!")
    else:
        print("Next action:")
        print("  python3 .governance/wbs_cli.py status")
        print("Reason: Check for blocked/failed packets")


def cmd_stale(minutes: int):
    """Find stale in-progress packets."""
    state = ensure_state_shape(load_state())


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
    ok, msg = governance_engine().closeout_l2(area_id, agent, assessment_path, notes)
    if ok:
        print(green(msg))
        print(dim(f"Drift assessment: {assessment_path}"))
    else:
        print(red(_format_error(msg)))
    return ok
    now = datetime.now()
    found = False

    for pid, pstate in state["packets"].items():
        if pstate.get("status") == "in_progress" and pstate.get("started_at"):
            started = datetime.fromisoformat(pstate["started_at"])
            elapsed = (now - started).total_seconds() / 60
            if elapsed > minutes:
                print(yellow(f"Warning: {pid} in progress for {int(elapsed)} minutes"))
                found = True

    if not found:
        print(green("No stale packets"))


def require_state():
    """Check state file exists."""
    if not WBS_STATE.exists():
        print(red("Not initialized. Run: python3 .governance/wbs_cli.py init .governance/wbs.json"))
        return False
    return True


def save_definition(defn: dict):
    """Save WBS definition with atomic write."""
    tmp = WBS_DEF.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(defn, f, indent=2)
        f.write("\n")
    tmp.replace(WBS_DEF)


def cmd_add_area(area_id: str, title: str, description: str = "") -> bool:
    """Add a work area."""
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


def cmd_add_packet(packet_id: str, area_id: str, title: str, scope: str, wbs_ref: str = None) -> bool:
    """Add a packet."""
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

    defn.setdefault("packets", []).append({
        "id": packet_id,
        "wbs_ref": wbs_ref,
        "area_id": area_id,
        "title": title,
        "scope": scope
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


def cmd_add_dep(packet_id: str, depends_on: str) -> bool:
    """Add a dependency."""
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


def cmd_remove(item_id: str, force: bool = False) -> bool:
    """Remove a packet or area."""
    defn = load_definition()

    # Check if it's a packet
    packet = next((p for p in defn.get("packets", []) if p["id"] == item_id), None)
    if packet:
        state = ensure_state_shape(load_state())
        pkt_state = state["packets"].get(item_id, {})
        if pkt_state.get("status") in ("in_progress", "done") and not force:
            print(red(f"Packet {item_id} is {pkt_state['status']}. Use --force to remove."))
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


def cmd_validate() -> bool:
    """Validate WBS structure."""
    defn = load_definition()
    errors = []

    # Check for circular dependencies
    deps = defn.get("dependencies", {})
    cycle = detect_circular(deps)
    if cycle:
        errors.append(f"Circular dependency: {' -> '.join(cycle)}")

    # Check all packets have valid areas
    areas = {a["id"] for a in defn.get("work_areas", [])}
    for pkt in defn.get("packets", []):
        if pkt.get("area_id") not in areas:
            errors.append(f"Packet {pkt['id']} references unknown area: {pkt.get('area_id')}")

    # Check all dependencies reference valid packets
    packets = {p["id"] for p in defn.get("packets", [])}
    for pid, dep_list in deps.items():
        if pid not in packets:
            errors.append(f"Dependency references unknown packet: {pid}")
        for dep in dep_list:
            if dep not in packets:
                errors.append(f"Packet {pid} depends on unknown packet: {dep}")

    # Check for duplicate IDs
    pkt_ids = [p["id"] for p in defn.get("packets", [])]
    if len(pkt_ids) != len(set(pkt_ids)):
        errors.append("Duplicate packet IDs found")

    area_ids = [a["id"] for a in defn.get("work_areas", [])]
    if len(area_ids) != len(set(area_ids)):
        errors.append("Duplicate area IDs found")

    if errors:
        print(red("Validation failed:"))
        for err in errors:
            print(f"  - {err}")
        return False

    print(green(f"Validation passed: {len(areas)} areas, {len(packets)} packets"))
    return True


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
        status = pstate.get("status", "pending")
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
                title = pkt.get('title', '').replace('"', '\\"')
                label = f"{pid}\\n{title}"
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
        payload = {"packets": state.get("packets", {}), "area_closeouts": state.get("area_closeouts", {})}
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

    print(red("Unknown export type. Use: state-json | log-json | log-csv"))
    return False


def print_help():
    print("Usage: wbs_cli.py [--json] <command> [args]")
    print()
    print("Commands:")
    print("  init <wbs.json>       Initialize from WBS file")
    print("  init --wizard         Interactive setup")
    print("  status                Full project status")
    print("  ready                 List claimable packets")
    print("  next                  Recommended next action")
    print("  scope <id>            Packet details")
    print("  progress              Summary counts")
    print("  graph [--output file] ASCII dependency graph (+ optional Graphviz DOT export)")
    print("  export <type> <path>  Export state/log data (state-json|log-json|log-csv)")
    print("  validate              Check WBS structure")
    print("  validate-packet [path] Validate packets against packet schema")
    print("  closeout-l2 <area> <agent> <drift-md> [notes] Close level-2 area with drift assessment")
    print()
    print("  claim <id> <agent>    Claim a packet")
    print("  done <id> <agent>     Mark done")
    print("  note <id> <agent>     Update notes")
    print("  fail <id> <agent>     Mark failed")
    print("  reset <id>            Reset to pending")
    print("  stale <minutes>       Find stuck packets")
    print("  log [limit]           Recent activity")
    print()
    print("  add-area <id> <title> [desc]       Add work area")
    print("  add-packet <id> <area> <title>     Add packet (scope via stdin or -s)")
    print("  add-dep <packet> <depends-on>      Add dependency")
    print("  remove <id> [--force]              Remove packet or area")
    print()
    print("Options:")
    print("  --json              Output as JSON (for scripting)")
    print()
    print("Examples:")
    print("  python3 .governance/wbs_cli.py ready")
    print("  python3 .governance/wbs_cli.py claim CDX-3-1 codex-lead")
    print("  python3 .governance/wbs_cli.py done CDX-3-1 codex-lead \"Implemented changes\"")
    print("  python3 .governance/wbs_cli.py note CDX-3-1 codex-lead \"Evidence: docs/path.md\"")
    print("  python3 .governance/wbs_cli.py closeout-l2 2 codex-lead docs/codex-migration/drift-wbs2.md \"ready for handoff\"")
    print()
    print("Notes:")
    print("  reset only applies to in_progress packets")


def main():
    global JSON_OUTPUT

    # Parse --json flag
    args = sys.argv[1:]
    if "--json" in args:
        JSON_OUTPUT = True
        args.remove("--json")

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
            elif len(args) < 2:
                print("Usage: wbs_cli.py init <wbs.json>")
                sys.exit(1)
            else:
                success = cmd_init(args[1])
            if not success:
                sys.exit(1)
        elif cmd == "status":
            if require_state(): cmd_status()
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
        elif cmd == "claim":
            if len(args) < 3:
                print("Usage: wbs_cli.py claim <packet_id> <agent>")
                sys.exit(1)
            if require_state() and not cmd_claim(args[1], args[2]):
                sys.exit(1)
        elif cmd == "done":
            if len(args) < 3:
                print("Usage: wbs_cli.py done <packet_id> <agent> [notes]")
                sys.exit(1)
            notes = args[3] if len(args) > 3 else ""
            if require_state() and not cmd_done(args[1], args[2], notes):
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
        elif cmd == "stale":
            if len(args) < 2:
                print("Usage: wbs_cli.py stale <minutes>")
                sys.exit(1)
            if require_state(): cmd_stale(int(args[1]))
        elif cmd == "log":
            limit = int(args[1]) if len(args) > 1 else 20
            if require_state(): cmd_log(limit)
        elif cmd == "graph":
            output = ""
            if "--output" in args:
                idx = args.index("--output")
                if idx + 1 >= len(args):
                    print("Usage: wbs_cli.py graph [--output deps.dot]")
                    sys.exit(1)
                output = args[idx + 1]
            if require_state(): cmd_graph(output)
        elif cmd == "export":
            if len(args) < 3:
                print("Usage: wbs_cli.py export <state-json|log-json|log-csv> <path>")
                sys.exit(1)
            if require_state() and not cmd_export(args[1], args[2]):
                sys.exit(1)
        elif cmd == "validate":
            if not cmd_validate():
                sys.exit(1)
        elif cmd == "validate-packet":
            target = args[1] if len(args) > 1 else ""
            if not cmd_validate_packet(target):
                sys.exit(1)
        elif cmd == "closeout-l2":
            if len(args) < 4:
                print("Usage: wbs_cli.py closeout-l2 <area_id|n> <agent> <drift_assessment.md> [notes]")
                sys.exit(1)
            notes = args[4] if len(args) > 4 else ""
            if require_state() and not cmd_closeout_l2(args[1], args[2], args[3], notes):
                sys.exit(1)
        elif cmd == "add-area":
            if len(args) < 3:
                print("Usage: wbs_cli.py add-area <id> <title> [description]")
                sys.exit(1)
            desc = args[3] if len(args) > 3 else ""
            if not cmd_add_area(args[1], args[2], desc):
                sys.exit(1)
        elif cmd == "add-packet":
            if len(args) < 4:
                print("Usage: wbs_cli.py add-packet <id> <area> <title> [-s scope | --scope scope]")
                print("       Or pipe scope via stdin")
                sys.exit(1)
            pid, area, title = args[1], args[2], args[3]
            scope = ""
            # Check for -s or --scope flag
            if "-s" in args:
                idx = args.index("-s")
                scope = args[idx + 1] if idx + 1 < len(args) else ""
            elif "--scope" in args:
                idx = args.index("--scope")
                scope = args[idx + 1] if idx + 1 < len(args) else ""
            elif not sys.stdin.isatty():
                scope = sys.stdin.read().strip()
            if not scope:
                print("Enter scope (Ctrl+D when done):")
                try:
                    scope = sys.stdin.read().strip()
                except:
                    scope = ""
            if not cmd_add_packet(pid, area, title, scope):
                sys.exit(1)
        elif cmd == "add-dep":
            if len(args) < 3:
                print("Usage: wbs_cli.py add-dep <packet> <depends-on>")
                sys.exit(1)
            if not cmd_add_dep(args[1], args[2]):
                sys.exit(1)
        elif cmd == "remove":
            if len(args) < 2:
                print("Usage: wbs_cli.py remove <id> [--force]")
                sys.exit(1)
            force = "--force" in args
            if not cmd_remove(args[1], force):
                sys.exit(1)
        else:
            print(red(f"Unknown command: {cmd}"))
            sys.exit(1)
    except Exception as e:
        print(red(f"Error: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
