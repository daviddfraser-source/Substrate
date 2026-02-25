from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ActorContext:
    user_id: str
    role: str
    source: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "user_id": self.user_id,
            "role": self.role,
            "source": self.source,
        }


@dataclass(frozen=True)
class EngineResult:
    ok: bool
    message: str
    payload: Dict[str, Any]


__all__ = ["ActorContext", "EngineResult"]
