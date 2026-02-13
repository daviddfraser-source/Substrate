from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

from governed_platform.governance.interfaces import GovernanceInterface
from governed_platform.governance.state_manager import StateManager
from governed_platform.governance.supervisor import (
    DeterministicSupervisor,
    TransitionRequest,
    SupervisorInterface,
)


class GovernanceEngine(GovernanceInterface):
    """Governance lifecycle engine detached from CLI concerns."""

    def __init__(self, definition: Dict[str, Any], state_manager: StateManager, supervisor: SupervisorInterface = None):
        self.definition = definition
        self.state_manager = state_manager
        self.supervisor = supervisor or DeterministicSupervisor()

    def _load(self) -> Dict[str, Any]:
        return self.state_manager.load()

    def _save(self, state: Dict[str, Any]) -> None:
        self.state_manager.save(state)

    def _deps_met(self, state: Dict[str, Any], packet_id: str) -> Tuple[bool, str]:
        deps = self.definition.get("dependencies", {}).get(packet_id, [])
        for dep_id in deps:
            dep_state = state.get("packets", {}).get(dep_id, {})
            if dep_state.get("status") != "done":
                return False, dep_id
        return True, ""

    def _log(self, state: Dict[str, Any], packet_id: str, event: str, agent: str = None, notes: str = None):
        state.setdefault("log", []).append(
            {
                "packet_id": packet_id,
                "event": event,
                "agent": agent,
                "timestamp": datetime.now().isoformat(),
                "notes": notes,
            }
        )

    def _approve(self, action: str, packet_id: str, agent: str = None, notes: str = None) -> Tuple[bool, str]:
        req = TransitionRequest(packet_id=packet_id, action=action, agent=agent, notes=notes)
        return self.supervisor.approve(req)

    def claim(self, packet_id: str, agent: str) -> Tuple[bool, str]:
        allowed, reason = self._approve("claim", packet_id, agent=agent)
        if not allowed:
            return False, reason
        state = self._load()
        if packet_id not in state.get("packets", {}):
            return False, f"Packet {packet_id} not found"
        pkt = state["packets"][packet_id]
        if pkt.get("status") != "pending":
            return False, f"Packet {packet_id} is {pkt.get('status')}, not pending"
        ok, blocking = self._deps_met(state, packet_id)
        if not ok:
            return False, f"Blocked by {blocking} (not done yet)"
        pkt["status"] = "in_progress"
        pkt["assigned_to"] = agent
        pkt["started_at"] = datetime.now().isoformat()
        self._log(state, packet_id, "started", agent, f"Claimed by {agent}")
        self._save(state)
        return True, f"{packet_id} claimed by {agent}"

    def done(self, packet_id: str, agent: str, notes: str = "") -> Tuple[bool, str]:
        allowed, reason = self._approve("done", packet_id, agent=agent, notes=notes)
        if not allowed:
            return False, reason
        state = self._load()
        if packet_id not in state.get("packets", {}):
            return False, f"Packet {packet_id} not found"
        pkt = state["packets"][packet_id]
        if pkt.get("status") != "in_progress":
            return False, f"Packet {packet_id} is {pkt.get('status')}, not in_progress"
        pkt["status"] = "done"
        pkt["completed_at"] = datetime.now().isoformat()
        pkt["notes"] = notes
        self._log(state, packet_id, "completed", agent, notes)
        self._save(state)
        return True, f"{packet_id} marked done"

    def note(self, packet_id: str, agent: str, notes: str) -> Tuple[bool, str]:
        allowed, reason = self._approve("note", packet_id, agent=agent, notes=notes)
        if not allowed:
            return False, reason
        state = self._load()
        if packet_id not in state.get("packets", {}):
            return False, f"Packet {packet_id} not found"
        state["packets"][packet_id]["notes"] = notes
        self._log(state, packet_id, "noted", agent, notes)
        self._save(state)
        return True, f"{packet_id} notes updated"

    def fail(self, packet_id: str, agent: str, reason: str = "") -> Tuple[bool, str]:
        allowed, sup_reason = self._approve("fail", packet_id, agent=agent, notes=reason)
        if not allowed:
            return False, sup_reason
        state = self._load()
        if packet_id not in state.get("packets", {}):
            return False, f"Packet {packet_id} not found"
        pkt = state["packets"][packet_id]
        if pkt.get("status") not in ("pending", "in_progress"):
            return False, f"Packet {packet_id} is {pkt.get('status')}, cannot fail"
        pkt["status"] = "failed"
        pkt["completed_at"] = datetime.now().isoformat()
        pkt["notes"] = reason
        self._log(state, packet_id, "failed", agent, reason)
        deps = self.definition.get("dependencies", {})
        to_block = [pid for pid, dep_list in deps.items() if packet_id in dep_list]
        blocked = []
        while to_block:
            pid = to_block.pop(0)
            cur = state.get("packets", {}).get(pid, {})
            if cur.get("status") in ("pending", "in_progress"):
                cur["status"] = "blocked"
                self._log(state, pid, "blocked", None, f"Blocked by {packet_id}")
                blocked.append(pid)
                to_block.extend(p for p, d in deps.items() if pid in d)
        self._save(state)
        suffix = f"; blocked: {', '.join(blocked)}" if blocked else ""
        return True, f"{packet_id} failed{suffix}"

    def reset(self, packet_id: str) -> Tuple[bool, str]:
        state = self._load()
        if packet_id not in state.get("packets", {}):
            return False, f"Packet {packet_id} not found"
        pkt = state["packets"][packet_id]
        if pkt.get("status") != "in_progress":
            return False, f"Packet {packet_id} is {pkt.get('status')}, not in_progress"
        pkt["status"] = "pending"
        pkt["assigned_to"] = None
        pkt["started_at"] = None
        self._log(state, packet_id, "reset", None, None)
        self._save(state)
        return True, f"{packet_id} reset to pending"

    def ready(self) -> Dict[str, Any]:
        state = self._load()
        ready: List[Dict[str, str]] = []
        for pkt in self.definition.get("packets", []):
            pid = pkt["id"]
            if state.get("packets", {}).get(pid, {}).get("status") == "pending":
                ok, _ = self._deps_met(state, pid)
                if ok:
                    ready.append({"id": pid, "wbs_ref": pkt.get("wbs_ref"), "title": pkt.get("title")})
        return {"ready": ready}

    def status(self) -> Dict[str, Any]:
        state = self._load()
        return state

    def closeout_l2(self, area_id: str, agent: str, assessment_path: str, notes: str = "") -> Tuple[bool, str]:
        allowed, reason = self._approve("closeout_l2", f"AREA-{area_id}", agent=agent, notes=notes)
        if not allowed:
            return False, reason
        state = self._load()
        area_id = (area_id or "").strip()
        area_ids = {a["id"] for a in self.definition.get("work_areas", [])}
        if area_id not in area_ids and area_id.isdigit():
            area_id = f"{area_id}.0"
        area = next((a for a in self.definition.get("work_areas", []) if a["id"] == area_id), None)
        if not area:
            return False, f"Level-2 area not found: {area_id}"

        area_packets = [p for p in self.definition.get("packets", []) if p.get("area_id") == area_id]
        incomplete = []
        for packet in area_packets:
            pid = packet["id"]
            status = state.get("packets", {}).get(pid, {}).get("status", "pending")
            if status != "done":
                incomplete.append(f"{pid}({status})")
        if incomplete:
            return False, f"Cannot close out {area_id}: incomplete packets: {', '.join(incomplete)}"

        raw = Path(assessment_path.strip())
        if not raw.exists():
            return False, f"assessment file not found: {assessment_path}"
        text = raw.read_text(errors="replace").lower()
        missing = [s for s in self.REQUIRED_DRIFT_SECTIONS if s.lower() not in text]
        if missing:
            return False, "Drift assessment validation failed: " + "; ".join(f"missing required section: {m}" for m in missing)

        state.setdefault("area_closeouts", {})[area_id] = {
            "status": "closed",
            "area_title": area.get("title"),
            "closed_by": agent,
            "closed_at": datetime.now().isoformat(),
            "drift_assessment_path": assessment_path,
            "notes": notes or None,
            "integrity_method": "review-based (no cryptographic hashing required)",
        }
        self._log(state, f"AREA-{area_id}", "area_closed", agent, f"Drift assessment: {assessment_path}" + (f" | {notes}" if notes else ""))
        self._save(state)
        return True, f"Level-2 area {area_id} closed"
    REQUIRED_DRIFT_SECTIONS = [
        "## Scope Reviewed",
        "## Expected vs Delivered",
        "## Drift Assessment",
        "## Evidence Reviewed",
        "## Residual Risks",
        "## Immediate Next Actions",
    ]
