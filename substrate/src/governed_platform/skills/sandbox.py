import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from governed_platform.skills.permissions import ExecutionPermissionModel


@dataclass
class SandboxResult:
    returncode: int
    stdout: str
    stderr: str
    duration_s: float = field(default=0.0)
    timed_out: bool = field(default=False)


class SandboxInterface:
    def run(
        self,
        command: List[str],
        workdir: Path,
        permission_model: ExecutionPermissionModel,
        timeout_s: Optional[int] = 60,
    ) -> Tuple[bool, SandboxResult]:
        raise NotImplementedError


class SubprocessSandbox(SandboxInterface):
    """Minimum isolation mode using constrained subprocess execution."""

    def run(
        self,
        command: List[str],
        workdir: Path,
        permission_model: ExecutionPermissionModel,
        timeout_s: Optional[int] = 60,
    ) -> Tuple[bool, SandboxResult]:
        if not command:
            return False, SandboxResult(1, "", "Empty command")

        exe = command[0]
        if not permission_model.is_command_allowed(exe):
            return False, SandboxResult(1, "", f"Command not allowed: {exe}")
        if not permission_model.is_path_allowed(workdir):
            return False, SandboxResult(1, "", f"Workdir not allowed: {workdir}")

        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                command,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            duration = time.monotonic() - t0
            result = SandboxResult(
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_s=round(duration, 3),
            )
            return (proc.returncode == 0), result
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - t0
            return False, SandboxResult(
                returncode=124,
                stdout="",
                stderr=f"Command timed out after {timeout_s}s",
                duration_s=round(duration, 3),
                timed_out=True,
            )


class ContainerSandbox(SandboxInterface):
    """Container sandbox contract placeholder for future hardened runtime."""

    def run(
        self,
        command: List[str],
        workdir: Path,
        permission_model: ExecutionPermissionModel,
        timeout_s: Optional[int] = 60,
    ) -> Tuple[bool, SandboxResult]:
        return False, SandboxResult(1, "", "Container sandbox not implemented in this baseline")
