from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from governed_platform.governance.status import normalize_runtime_status

_MUTATION_STATUSES = {"pending", "in_progress", "done", "failed", "blocked"}


def detect_dependency_cycle(dependencies: Dict[str, List[str]]) -> List[str]:
    visited: Set[str] = set()
    stack: List[str] = []
    in_stack: Set[str] = set()

    def walk(node: str) -> List[str]:
        visited.add(node)
        stack.append(node)
        in_stack.add(node)
        for nxt in dependencies.get(node, []):
            if nxt not in visited:
                found = walk(nxt)
                if found:
                    return found
            elif nxt in in_stack:
                idx = stack.index(nxt)
                return stack[idx:] + [nxt]
        stack.pop()
        in_stack.remove(node)
        return []

    for node in dependencies:
        if node not in visited:
            found = walk(node)
            if found:
                return found
    return []


def dependency_blocker(packet_id: str, dependencies: Dict[str, List[str]], state: Dict[str, Any]) -> Optional[str]:
    """Return the first incomplete dependency id, else None."""
    for dep_id in dependencies.get(packet_id, []):
        dep_state = state.get("packets", {}).get(dep_id, {})
        if normalize_runtime_status(dep_state.get("status", "pending")) != "done":
            return dep_id
    return None


def validate_claim(packet_id: str, dependencies: Dict[str, List[str]], state: Dict[str, Any]) -> Tuple[bool, str]:
    packets = state.get("packets", {})
    if packet_id not in packets:
        return False, f"Packet {packet_id} not found"
    status = normalize_runtime_status(packets.get(packet_id, {}).get("status", "pending"))
    if status != "pending":
        return False, f"Packet {packet_id} is {status}, not pending"
    blocker = dependency_blocker(packet_id, dependencies, state)
    if blocker:
        return False, f"Blocked by {blocker} (not done yet)"
    return True, "ok"


def validate_claim_pipeline(
    packet_id: str,
    dependencies: Dict[str, List[str]],
    state: Dict[str, Any],
) -> Tuple[bool, str, List[str]]:
    """Deterministic gate ordering for claim transitions."""
    trace: List[str] = []

    # 1) Referential integrity
    ok, msg = assert_packets_exist([packet_id], state)
    trace.append("referential_integrity")
    if not ok:
        return False, msg, trace

    for dep_id in dependencies.get(packet_id, []):
        ok, msg = assert_packets_exist([dep_id], state)
        if not ok:
            return False, f"Dependency missing: {packet_id} -> {dep_id}", trace

    # 2) Invariant enforcement
    cycle = detect_dependency_cycle(dependencies)
    trace.append("invariant_cycle_check")
    if cycle:
        return False, f"Dependency cycle detected: {' -> '.join(cycle)}", trace

    # 3) Dependency gate + state checks
    ok, msg = validate_claim(packet_id, dependencies, state)
    trace.append("dependency_gate")
    if not ok:
        return False, msg, trace
    return True, "ok", trace


def validate_done(packet_id: str, state: Dict[str, Any]) -> Tuple[bool, str]:
    packets = state.get("packets", {})
    if packet_id not in packets:
        return False, f"Packet {packet_id} not found"
    status = normalize_runtime_status(packets.get(packet_id, {}).get("status", "pending"))
    if status != "in_progress":
        return False, f"Packet {packet_id} is {status}, not in_progress"
    return True, "ok"


def validate_note(packet_id: str, state: Dict[str, Any]) -> Tuple[bool, str]:
    if packet_id not in state.get("packets", {}):
        return False, f"Packet {packet_id} not found"
    return True, "ok"


def validate_fail(packet_id: str, state: Dict[str, Any]) -> Tuple[bool, str]:
    packets = state.get("packets", {})
    if packet_id not in packets:
        return False, f"Packet {packet_id} not found"
    status = normalize_runtime_status(packets.get(packet_id, {}).get("status", "pending"))
    if status not in ("pending", "in_progress"):
        return False, f"Packet {packet_id} is {status}, cannot fail"
    return True, "ok"


def validate_reset(packet_id: str, state: Dict[str, Any]) -> Tuple[bool, str]:
    packets = state.get("packets", {})
    if packet_id not in packets:
        return False, f"Packet {packet_id} not found"
    status = normalize_runtime_status(packets.get(packet_id, {}).get("status", "pending"))
    if status != "in_progress":
        return False, f"Packet {packet_id} is {status}, not in_progress"
    return True, "ok"


def validate_state_shape(state: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(state, dict):
        return False, "State must be an object"
    if not isinstance(state.get("packets", {}), dict):
        return False, "State packets must be a map"

    for packet_id, payload in state.get("packets", {}).items():
        if not isinstance(payload, dict):
            return False, f"Packet {packet_id} runtime state must be an object"
        status = normalize_runtime_status(payload.get("status", "pending"))
        if status not in _MUTATION_STATUSES:
            return False, f"Packet {packet_id} has unsupported status {status}"

    log = state.get("log", [])
    if not isinstance(log, list):
        return False, "State log must be a list"
    return True, "ok"


def assert_packets_exist(packet_ids: Iterable[str], state: Dict[str, Any]) -> Tuple[bool, str]:
    packets = state.get("packets", {})
    for packet_id in packet_ids:
        if packet_id not in packets:
            return False, f"Packet {packet_id} not found"
    return True, "ok"


__all__ = [
    "detect_dependency_cycle",
    "dependency_blocker",
    "validate_claim",
    "validate_claim_pipeline",
    "validate_done",
    "validate_note",
    "validate_fail",
    "validate_reset",
    "validate_state_shape",
    "assert_packets_exist",
]
