import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "wbs-definition-guard.sh"


def run_guard(args=None, env=None, expect=0):
    args = args or []
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        ["bash", str(SCRIPT)] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=merged,
    )
    if proc.returncode != expect:
        raise AssertionError(
            f"guard failed\nargs={args}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class WbsDefinitionGuardTests(unittest.TestCase):
    def test_passes_when_protected_files_not_changed(self):
        run_guard(env={"WBS_DEFINITION_GUARD_CHANGED_FILES": "README.md"})

    def test_blocks_protected_change_without_trailer(self):
        proc = run_guard(
            args=["--commit-msg", "/tmp/does-not-exist-msg"],
            env={"WBS_DEFINITION_GUARD_CHANGED_FILES": ".governance/wbs.json"},
            expect=1,
        )
        self.assertIn("protected WBS/governance definition files changed", proc.stderr)
        self.assertIn("WBS-Change-Approved", proc.stderr)

    def test_allows_with_commit_trailer(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("feat: mutate wbs\n\nWBS-Change-Approved: GOV-13-3\n")
            msg_path = f.name
        try:
            run_guard(
                args=["--commit-msg", msg_path],
                env={"WBS_DEFINITION_GUARD_CHANGED_FILES": ".governance/wbs.json"},
            )
        finally:
            Path(msg_path).unlink(missing_ok=True)

    def test_allows_env_override(self):
        run_guard(
            args=["--commit-msg", "/tmp/does-not-exist-msg"],
            env={
                "WBS_DEFINITION_GUARD_CHANGED_FILES": ".governance/wbs.json",
                "ALLOW_WBS_DEFINITION_EDIT": "1",
            },
        )


if __name__ == "__main__":
    unittest.main()
