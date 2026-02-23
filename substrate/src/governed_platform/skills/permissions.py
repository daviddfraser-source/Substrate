from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ExecutionPermissionModel:
    allowed_roots: List[Path] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)

    def is_command_allowed(self, command: str) -> bool:
        return command in self.allowed_commands

    def is_path_allowed(self, target: Path) -> bool:
        resolved = target.resolve()
        for root in self.allowed_roots:
            resolved_root = root.resolve()
            # Use parent-chain membership to avoid startswith prefix collisions
            # e.g. allowed=/tmp/foo must NOT match /tmp/foo-evil
            if resolved == resolved_root or resolved_root in resolved.parents:
                return True
        return False
