from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Tuple

from governed_platform.governance.status import normalize_runtime_status

from substrate_core.audit import append_mutation_log, validate_append_only_log
from substrate_core.graph_core import (
    critical_path as graph_critical_path,
    downstream_nodes,
    impact_analysis as graph_impact_analysis,
    postgres_recursive_cte_queries,
    upstream_nodes,
)
from substrate_core.ontology import validate_packet_dependency_ontology
from substrate_core.policy import (
    activate_policy_version,
    evaluate_policy_with_opa,
    register_policy_version,
)
from substrate_core.state import ActorContext, EngineResult
from substrate_core.storage import StorageInterface
from substrate_core.trust import register_trust_model, score_with_active_model
from substrate_core.validation import (
    detect_dependency_cycle,
    dependency_blocker,
    validate_claim_pipeline,
    validate_done,
    validate_fail,
    validate_note,
    validate_reset,
    validate_state_shape,
)


class PacketEngine:
    """Reusable packet lifecycle engine for CLI/API/terminal callers."""

    def __init__(self, storage: StorageInterface, definition: Dict[str, Any]):
        self.storage = storage
        self.definition = definition
        self.dependencies = definition.get("dependencies", {})

    def _load(self) -> Dict[str, Any]:
        return self.storage.read_state()

    def _save(self, state: Dict[str, Any]) -> None:
        self.storage.write_state(state)

    def _save_with_log_guard(self, state: Dict[str, Any], before_log: List[Dict[str, Any]]) -> Tuple[bool, str]:
        ok, msg = validate_append_only_log(before_log, state.get("log", []))
        if not ok:
            return False, msg
        self._save(state)
        return True, "ok"

    def _log(
        self,
        *,
        packet_id: str,
        actor: ActorContext,
        lifecycle_event: str,
        action: str,
        result: str,
        notes: str = "",
        exit_state: str = "",
    ) -> None:
        append_mutation_log(
            self.storage,
            packet_id=packet_id,
            lifecycle_event=lifecycle_event,
            action=action,
            actor=actor.as_dict(),
            result=result,
            notes=notes,
            exit_state=exit_state,
        )

    def _log_with_state(
        self,
        state: Dict[str, Any],
        *,
        packet_id: str,
        actor: ActorContext,
        lifecycle_event: str,
        action: str,
        result: str,
        notes: str = "",
        exit_state: str = "",
    ) -> Dict[str, Any]:
        from governed_platform.governance.log_integrity import (
            LOG_MODE_HASH_CHAIN,
            build_log_entry,
            normalize_log_mode,
        )

        entries = state.setdefault("log", [])
        mode = normalize_log_mode(state.get("log_integrity_mode", "plain"))
        prev_hash = ""
        hash_index = 1
        if mode == LOG_MODE_HASH_CHAIN:
            hashed = [entry for entry in entries if isinstance(entry, dict) and entry.get("hash")]
            if hashed:
                prev_hash = hashed[-1].get("hash", "") or ""
                hash_index = len(hashed) + 1

        entry = build_log_entry(
            packet_id=packet_id,
            event=lifecycle_event,
            agent=actor.user_id,
            notes=notes,
            timestamp=datetime.now().isoformat(),
            mode=mode,
            previous_hash=prev_hash,
            hash_index=hash_index,
        )
        entry.update(
            {
                "actor": actor.user_id,
                "role": actor.role,
                "source": actor.source,
                "action": action,
                "packet": packet_id,
                "result": result,
                "exit_state": exit_state,
            }
        )
        entries.append(entry)
        return state

    def _ensure_packet_runtime(self, state: Dict[str, Any]) -> Dict[str, Any]:
        packets = state.setdefault("packets", {})
        for packet in self.definition.get("packets", []):
            pid = packet["id"]
            packets.setdefault(
                pid,
                {
                    "status": "pending",
                    "assigned_to": None,
                    "started_at": None,
                    "completed_at": None,
                    "notes": None,
                },
            )
        return state

    def _active_handover(self, packet_state: Dict[str, Any]) -> Dict[str, Any]:
        for item in reversed(packet_state.get("handovers", [])):
            if isinstance(item, dict) and item.get("active"):
                return item
        return {}

    def claim(self, packet_id: str, actor: ActorContext) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        policy = evaluate_policy_with_opa(
            self.definition,
            packet_id=packet_id,
            actor=actor,
            transition="claim",
            state=state,
        )
        if not policy.allow:
            return EngineResult(
                False,
                policy.message,
                {
                    "packet_id": packet_id,
                    "policy_version": policy.policy_version,
                    "policy_trace": policy.trace,
                },
            )
        ok, msg = validate_packet_dependency_ontology(packet_id, self.definition, self.dependencies)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        ok, msg, trace = validate_claim_pipeline(packet_id, self.dependencies, state)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id, "trace": trace})

        pkt = state["packets"][packet_id]
        pkt["status"] = "in_progress"
        pkt["assigned_to"] = actor.user_id
        pkt["started_at"] = datetime.now().isoformat()
        self._log_with_state(
            state,
            packet_id=packet_id,
            actor=actor,
            lifecycle_event="started",
            action="claim",
            result="success",
            notes=f"Claimed by {actor.user_id}",
            exit_state="in_progress",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        return EngineResult(
            True,
            f"{packet_id} claimed by {actor.user_id}",
            {
                "packet_id": packet_id,
                "policy_version": policy.policy_version,
                "policy_trace": policy.trace,
            },
        )

    def done(self, packet_id: str, actor: ActorContext, notes: str = "") -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        policy = evaluate_policy_with_opa(
            self.definition,
            packet_id=packet_id,
            actor=actor,
            transition="done",
            state=state,
        )
        if not policy.allow:
            return EngineResult(
                False,
                policy.message,
                {
                    "packet_id": packet_id,
                    "policy_version": policy.policy_version,
                    "policy_trace": policy.trace,
                },
            )
        ok, msg = validate_done(packet_id, state)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        if self._active_handover(state["packets"][packet_id]):
            return EngineResult(
                False,
                f"Packet {packet_id} has active handover; resume before done",
                {"packet_id": packet_id},
            )

        pkt = state["packets"][packet_id]
        pkt["status"] = "done"
        pkt["completed_at"] = datetime.now().isoformat()
        pkt["notes"] = notes
        self._log_with_state(
            state,
            packet_id=packet_id,
            actor=actor,
            lifecycle_event="completed",
            action="done",
            result="success",
            notes=notes,
            exit_state="done",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        return EngineResult(
            True,
            f"{packet_id} marked done",
            {
                "packet_id": packet_id,
                "policy_version": policy.policy_version,
                "policy_trace": policy.trace,
            },
        )

    def note(self, packet_id: str, message: str, actor: ActorContext) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        ok, msg = validate_note(packet_id, state)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})

        state["packets"][packet_id]["notes"] = message
        self._log_with_state(
            state,
            packet_id=packet_id,
            actor=actor,
            lifecycle_event="noted",
            action="note",
            result="success",
            notes=message,
            exit_state=normalize_runtime_status(state["packets"][packet_id].get("status", "pending")),
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        return EngineResult(True, f"{packet_id} notes updated", {"packet_id": packet_id})

    def fail(self, packet_id: str, actor: ActorContext, reason: str = "") -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        ok, msg = validate_fail(packet_id, state)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        if self._active_handover(state["packets"][packet_id]):
            return EngineResult(
                False,
                f"Packet {packet_id} has active handover; resume before fail",
                {"packet_id": packet_id},
            )

        pkt = state["packets"][packet_id]
        pkt["status"] = "failed"
        pkt["completed_at"] = datetime.now().isoformat()
        pkt["notes"] = reason
        self._log_with_state(
            state,
            packet_id=packet_id,
            actor=actor,
            lifecycle_event="failed",
            action="fail",
            result="success",
            notes=reason,
            exit_state="failed",
        )

        blocked = self._cascade_block(state, packet_id, actor)
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        suffix = f"; blocked: {', '.join(blocked)}" if blocked else ""
        return EngineResult(True, f"{packet_id} failed{suffix}", {"packet_id": packet_id, "blocked": blocked})

    def _cascade_block(self, state: Dict[str, Any], failed_id: str, actor: ActorContext) -> List[str]:
        deps = self.dependencies
        to_block = [pid for pid, sources in deps.items() if failed_id in sources]
        blocked: List[str] = []
        while to_block:
            pid = to_block.pop(0)
            cur = state.get("packets", {}).get(pid, {})
            status = normalize_runtime_status(cur.get("status", "pending"))
            if status in ("pending", "in_progress"):
                cur["status"] = "blocked"
                self._log_with_state(
                    state,
                    packet_id=pid,
                    actor=actor,
                    lifecycle_event="blocked",
                    action="block",
                    result="success",
                    notes=f"Blocked by {failed_id}",
                    exit_state="blocked",
                )
                blocked.append(pid)
                to_block.extend(target for target, sources in deps.items() if pid in sources)
        return blocked

    def block(self, packet_id: str, actor: ActorContext, reason: str = "") -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        if packet_id not in state.get("packets", {}):
            return EngineResult(False, f"Packet {packet_id} not found", {"packet_id": packet_id})
        pkt = state["packets"][packet_id]
        pkt["status"] = "blocked"
        pkt["notes"] = reason
        self._log_with_state(
            state,
            packet_id=packet_id,
            actor=actor,
            lifecycle_event="blocked",
            action="block",
            result="success",
            notes=reason,
            exit_state="blocked",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        return EngineResult(True, f"{packet_id} marked blocked", {"packet_id": packet_id})

    def reset(self, packet_id: str, actor: ActorContext) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        ok, msg = validate_reset(packet_id, state)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})

        pkt = state["packets"][packet_id]
        pkt["status"] = "pending"
        pkt["assigned_to"] = None
        pkt["started_at"] = None
        self._log_with_state(
            state,
            packet_id=packet_id,
            actor=actor,
            lifecycle_event="reset",
            action="reset",
            result="success",
            notes="",
            exit_state="pending",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"packet_id": packet_id})
        return EngineResult(True, f"{packet_id} reset to pending", {"packet_id": packet_id})

    def get_status(self, packet_id: str) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        packet = state.get("packets", {}).get(packet_id)
        if packet is None:
            return EngineResult(False, f"Packet {packet_id} not found", {"packet_id": packet_id})
        return EngineResult(True, "ok", {"packet_id": packet_id, "status": packet})

    def upstream(self, packet_id: str) -> EngineResult:
        if packet_id not in {p.get("id") for p in self.definition.get("packets", [])}:
            return EngineResult(False, f"Packet {packet_id} not found", {"packet_id": packet_id})
        return EngineResult(True, "ok", {"packet_id": packet_id, "upstream": upstream_nodes(packet_id, self.dependencies)})

    def downstream(self, packet_id: str) -> EngineResult:
        if packet_id not in {p.get("id") for p in self.definition.get("packets", [])}:
            return EngineResult(False, f"Packet {packet_id} not found", {"packet_id": packet_id})
        return EngineResult(True, "ok", {"packet_id": packet_id, "downstream": downstream_nodes(packet_id, self.dependencies)})

    def impact_analysis(self, packet_id: str) -> EngineResult:
        if packet_id not in {p.get("id") for p in self.definition.get("packets", [])}:
            return EngineResult(False, f"Packet {packet_id} not found", {"packet_id": packet_id})
        return EngineResult(
            True,
            "ok",
            {"packet_id": packet_id, "impacted": graph_impact_analysis(packet_id, self.dependencies)},
        )

    def critical_path(self) -> EngineResult:
        packet_ids = [p.get("id") for p in self.definition.get("packets", []) if p.get("id")]
        return EngineResult(True, "ok", {"critical_path": graph_critical_path(self.dependencies, packet_ids)})

    def postgres_query_templates(self) -> EngineResult:
        return EngineResult(True, "ok", {"queries": postgres_recursive_cte_queries()})

    def register_policy_version(
        self,
        version_id: str,
        policy: Dict[str, Any],
        actor: ActorContext,
        rationale: str,
    ) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        ok, msg = register_policy_version(state, version_id=version_id, policy=policy, actor=actor, rationale=rationale)
        if not ok:
            return EngineResult(False, msg, {"version_id": version_id})
        self._log_with_state(
            state,
            packet_id=f"POLICY:{version_id}",
            actor=actor,
            lifecycle_event="policy_version_registered",
            action="policy-register",
            result="success",
            notes=rationale,
            exit_state="draft",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"version_id": version_id})
        return EngineResult(True, "ok", {"version_id": version_id})

    def activate_policy_version(
        self,
        version_id: str,
        actor: ActorContext,
        approvals: List[str],
        rationale: str,
    ) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        ok, msg = activate_policy_version(
            state,
            version_id=version_id,
            actor=actor,
            approvals=approvals,
            rationale=rationale,
        )
        if not ok:
            return EngineResult(False, msg, {"version_id": version_id})
        self._log_with_state(
            state,
            packet_id=f"POLICY:{version_id}",
            actor=actor,
            lifecycle_event="policy_version_activated",
            action="policy-activate",
            result="success",
            notes=rationale,
            exit_state="active",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"version_id": version_id})
        return EngineResult(True, "ok", {"version_id": version_id})

    def register_trust_model(
        self,
        version_id: str,
        weights: Dict[str, float],
        actor: ActorContext,
        rationale: str,
        approvals: List[str],
    ) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        ok, msg = register_trust_model(
            state,
            version_id=version_id,
            weights=weights,
            actor=actor,
            rationale=rationale,
            approvals=approvals,
        )
        if not ok:
            return EngineResult(False, msg, {"version_id": version_id})
        self._log_with_state(
            state,
            packet_id=f"TRUST:{version_id}",
            actor=actor,
            lifecycle_event="trust_model_registered",
            action="trust-register",
            result="success",
            notes=rationale,
            exit_state="active",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"version_id": version_id})
        return EngineResult(True, "ok", {"version_id": version_id})

    def score_trust(self, signals: Dict[str, float]) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        ok, msg, payload = score_with_active_model(state, signals)
        if not ok:
            return EngineResult(False, msg, {})
        return EngineResult(True, "ok", payload)

    def snapshot(self, label: str, actor: ActorContext | None = None) -> EngineResult:
        token = str(label or "").strip()
        if not token:
            return EngineResult(False, "Snapshot label is required", {"label": label})
        state = self._ensure_packet_runtime(self._load())
        before_log = list(state.get("log", []))
        snapshots = state.setdefault("snapshots", {})
        if token in snapshots:
            return EngineResult(False, f"Snapshot already exists: {token}", {"label": token})
        snapshots[token] = {
            "label": token,
            "created_at": datetime.now().isoformat(),
            "packets": deepcopy(state.get("packets", {})),
        }
        snap_actor = actor or ActorContext(user_id="system", role="system", source="engine")
        self._log_with_state(
            state,
            packet_id=f"SNAPSHOT:{token}",
            actor=snap_actor,
            lifecycle_event="snapshot",
            action="snapshot",
            result="success",
            notes=f"Snapshot {token} created",
            exit_state="n/a",
        )
        ok, msg = self._save_with_log_guard(state, before_log)
        if not ok:
            return EngineResult(False, msg, {"label": token})
        return EngineResult(True, "ok", {"label": token, "snapshot": snapshots[token]})

    def diff(self, snapshot_a: str, snapshot_b: str) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        snaps = state.get("snapshots", {})
        a = snaps.get(snapshot_a)
        b = snaps.get(snapshot_b)
        if not a:
            return EngineResult(False, f"Snapshot not found: {snapshot_a}", {"snapshot": snapshot_a})
        if not b:
            return EngineResult(False, f"Snapshot not found: {snapshot_b}", {"snapshot": snapshot_b})

        a_packets = a.get("packets", {})
        b_packets = b.get("packets", {})
        packet_ids = sorted(set(a_packets.keys()) | set(b_packets.keys()))
        changes: List[Dict[str, Any]] = []
        for pid in packet_ids:
            left = a_packets.get(pid, {})
            right = b_packets.get(pid, {})
            if left != right:
                changes.append({"packet_id": pid, "from": left, "to": right})
        return EngineResult(
            True,
            "ok",
            {
                "snapshot_a": snapshot_a,
                "snapshot_b": snapshot_b,
                "change_count": len(changes),
                "changes": changes,
            },
        )

    def validate(self) -> EngineResult:
        state = self._ensure_packet_runtime(self._load())
        ok, msg = validate_state_shape(state)
        if not ok:
            return EngineResult(False, msg, {})

        cycle = detect_dependency_cycle(self.dependencies)
        if cycle:
            return EngineResult(False, f"Dependency cycle detected: {' -> '.join(cycle)}", {"cycle": cycle})

        for packet in self.definition.get("packets", []):
            packet_id = packet.get("id")
            if not packet_id:
                continue
            ok, msg = validate_packet_dependency_ontology(str(packet_id), self.definition, self.dependencies)
            if not ok:
                return EngineResult(False, msg, {"packet_id": packet_id})

        for packet_id, deps in self.dependencies.items():
            for dep in deps:
                if dep not in state.get("packets", {}):
                    return EngineResult(False, f"Dependency missing: {packet_id} -> {dep}", {})

        for packet_id in state.get("packets", {}):
            blocker = dependency_blocker(packet_id, self.dependencies, state)
            status = normalize_runtime_status(state["packets"][packet_id].get("status", "pending"))
            if blocker and status == "pending":
                continue
        return EngineResult(True, "ok", {})


__all__ = ["PacketEngine"]
