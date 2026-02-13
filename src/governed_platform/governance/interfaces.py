from typing import Protocol, Dict, Any, Tuple


class GovernanceInterface(Protocol):
    def claim(self, packet_id: str, agent: str) -> Tuple[bool, str]:
        ...

    def done(self, packet_id: str, agent: str, notes: str = "") -> Tuple[bool, str]:
        ...

    def note(self, packet_id: str, agent: str, notes: str) -> Tuple[bool, str]:
        ...

    def fail(self, packet_id: str, agent: str, reason: str = "") -> Tuple[bool, str]:
        ...

    def reset(self, packet_id: str) -> Tuple[bool, str]:
        ...

    def ready(self) -> Dict[str, Any]:
        ...

    def status(self) -> Dict[str, Any]:
        ...

    def closeout_l2(self, area_id: str, agent: str, assessment_path: str, notes: str = "") -> Tuple[bool, str]:
        ...
