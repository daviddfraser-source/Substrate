from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Tuple

from governed_platform.governance.log_integrity import (
    LOG_MODE_HASH_CHAIN,
    build_log_entry,
    normalize_log_mode,
)

from substrate_core.storage import StorageInterface


def mutation_entry(
    *,
    packet_id: str,
    action: str,
    actor: Mapping[str, str],
    result: str,
    notes: str = "",
    event: str = "mutation",
    exit_state: str = "",
) -> Dict[str, Any]:
    """Create a structured mutation payload suitable for audit export/query."""
    return {
        "actor": actor.get("user_id", ""),
        "role": actor.get("role", ""),
        "source": actor.get("source", ""),
        "action": action,
        "packet": packet_id,
        "result": result,
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
        "exit_state": exit_state,
    }


def append_mutation_log(
    storage: StorageInterface,
    *,
    packet_id: str,
    lifecycle_event: str,
    action: str,
    actor: Mapping[str, str],
    result: str,
    notes: str = "",
    exit_state: str = "",
) -> Dict[str, Any]:
    """Persist immutable lifecycle + structured mutation fields into state log."""
    state = storage.read_state()
    entries = state.setdefault("log", [])
    mode = normalize_log_mode(state.get("log_integrity_mode", "plain"))

    prev_hash = ""
    hash_index = 1
    if mode == LOG_MODE_HASH_CHAIN:
        hashed = [entry for entry in entries if isinstance(entry, dict) and entry.get("hash")]
        if hashed:
            prev_hash = hashed[-1].get("hash", "") or ""
            hash_index = len(hashed) + 1

    lifecycle = build_log_entry(
        packet_id=packet_id,
        event=lifecycle_event,
        agent=actor.get("user_id") or "",
        notes=notes,
        timestamp=datetime.now().isoformat(),
        mode=mode,
        previous_hash=prev_hash,
        hash_index=hash_index,
    )

    lifecycle.update(
        mutation_entry(
            packet_id=packet_id,
            action=action,
            actor=actor,
            result=result,
            notes=notes,
            event=lifecycle_event,
            exit_state=exit_state,
        )
    )

    entries.append(lifecycle)
    storage.write_state(state)
    return lifecycle


def validate_append_only_log(previous: List[Dict[str, Any]], current: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Ensure audit log evolves append-only (prefix-preserving)."""
    if len(current) < len(previous):
        return False, "Audit log shrank; append-only invariant violated"
    for idx, entry in enumerate(previous):
        if current[idx] != entry:
            return False, f"Audit log mutated at index {idx}; append-only invariant violated"
    return True, "ok"


def provenance_chain(state: Dict[str, Any], packet_id: str) -> List[Dict[str, Any]]:
    """Return ordered lifecycle/provenance events for a packet id."""
    chain: List[Dict[str, Any]] = []
    for entry in state.get("log", []):
        if not isinstance(entry, dict):
            continue
        if str(entry.get("packet_id") or "") == packet_id:
            chain.append(entry)
    return chain


def export_provenance_snapshot(state: Dict[str, Any], packet_id: str) -> Dict[str, Any]:
    chain = provenance_chain(state, packet_id)
    return {
        "packet_id": packet_id,
        "event_count": len(chain),
        "events": chain,
    }


__all__ = [
    "mutation_entry",
    "append_mutation_log",
    "validate_append_only_log",
    "provenance_chain",
    "export_provenance_snapshot",
]
