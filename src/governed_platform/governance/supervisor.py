from dataclasses import dataclass
from typing import Optional, Tuple, Protocol


@dataclass
class TransitionRequest:
    packet_id: str
    action: str
    agent: Optional[str] = None
    notes: Optional[str] = None


class SupervisorInterface(Protocol):
    def approve(self, req: TransitionRequest) -> Tuple[bool, str]:
        ...


@dataclass
class SupervisorPolicy:
    require_notes_on_done: bool = True
    require_agent_for_mutation: bool = True


class DeterministicSupervisor:
    """Default deterministic authority policy for packet transitions."""

    def __init__(self, policy: SupervisorPolicy = None):
        self.policy = policy or SupervisorPolicy()

    def approve(self, req: TransitionRequest) -> Tuple[bool, str]:
        if self.policy.require_agent_for_mutation and req.action in {"claim", "done", "note", "fail", "closeout_l2"}:
            if not req.agent:
                return False, "Supervisor denied: agent required"
        if self.policy.require_notes_on_done and req.action == "done" and not (req.notes or "").strip():
            return False, "Supervisor denied: completion notes required for done"
        return True, "approved"
