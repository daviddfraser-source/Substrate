from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Dict, List, Optional, Set, Tuple

from governed_platform.skills.permissions import ExecutionPermissionModel
from governed_platform.skills.sandbox import SubprocessSandbox


@dataclass(frozen=True)
class MutationAttempt:
    actor: str
    packet_id: str
    action: str
    via_policy_pipeline: bool


class ProtectionError(PermissionError):
    pass


class MutationProtector:
    def __init__(self):
        self.allowed_actions: Set[str] = {"claim", "done", "fail", "note", "reset", "closeout-l2"}

    def enforce(self, attempt: MutationAttempt) -> None:
        if attempt.action not in self.allowed_actions:
            raise ProtectionError(f"Action not allowed: {attempt.action}")
        if not attempt.via_policy_pipeline:
            raise ProtectionError("Mutation bypass detected: policy pipeline required")


class BudgetStopper:
    def __init__(self):
        self.daily_caps: Dict[str, int] = {}
        self.used: Dict[str, int] = {}

    def configure(self, actor: str, daily_cap: int) -> None:
        self.daily_caps[actor] = int(daily_cap)
        self.used.setdefault(actor, 0)

    def consume(self, actor: str, tokens: int) -> None:
        cap = self.daily_caps.get(actor)
        if cap is None:
            raise ProtectionError(f"No budget configured for {actor}")
        new_total = self.used.get(actor, 0) + int(tokens)
        if new_total > cap:
            raise ProtectionError("Hard budget stop triggered")
        self.used[actor] = new_total


class RateLimiter:
    def __init__(self, per_minute: int):
        self.per_minute = int(per_minute)
        self._events: Dict[str, List[float]] = {}

    def allow(self, key: str, now: Optional[float] = None) -> bool:
        ts = now if now is not None else time()
        floor = ts - 60.0
        events = [t for t in self._events.get(key, []) if t >= floor]
        if len(events) >= self.per_minute:
            self._events[key] = events
            return False
        events.append(ts)
        self._events[key] = events
        return True


class ExecutionSandboxController:
    def __init__(self, allowed_commands: Optional[List[str]] = None):
        self.sandbox = SubprocessSandbox()
        self.allowed_commands = allowed_commands or ["echo", "python3"]

    def run(self, command: List[str], workdir: Path) -> Tuple[bool, str]:
        model = ExecutionPermissionModel(
            allowed_commands=self.allowed_commands,
            allowed_roots=[workdir],
        )
        ok, result = self.sandbox.run(command=command, workdir=workdir, permission_model=model, timeout_s=10)
        if not ok:
            return False, result.stderr
        return True, result.stdout
