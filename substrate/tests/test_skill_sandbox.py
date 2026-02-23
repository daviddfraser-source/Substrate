import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from governed_platform.skills.permissions import ExecutionPermissionModel  # noqa: E402
from governed_platform.skills.sandbox import SubprocessSandbox, SandboxResult  # noqa: E402
from governed_platform.skills.engine import SkillExecutionEngine, SkillExecutionRequest  # noqa: E402

# Use the current interpreter so tests pass on Windows (no `python3` alias)
_PYTHON = sys.executable


class SkillSandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sandbox = SubprocessSandbox()
        self.engine = SkillExecutionEngine(self.sandbox)

    def tearDown(self):
        self.tmp.cleanup()

    # ------------------------------------------------------------------
    # Happy-path
    # ------------------------------------------------------------------

    def test_allows_permitted_command_and_path(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[_PYTHON, "-c", "print('ok')"],
            workdir=self.root,
        )
        res = self.engine.execute(req, perms)
        self.assertTrue(res["success"])
        self.assertIn("ok", res["stdout"])

    # ------------------------------------------------------------------
    # Deny path
    # ------------------------------------------------------------------

    def test_denies_unapproved_command(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=["bash", "-lc", "echo hi"],
            workdir=self.root,
        )
        res = self.engine.execute(req, perms)
        self.assertFalse(res["success"])
        self.assertIn("Command not allowed", res["stderr"])

    def test_denies_unapproved_workdir(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root / "allowed"],
            allowed_commands=[_PYTHON],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[_PYTHON, "-c", "print('ok')"],
            workdir=self.root,
        )
        res = self.engine.execute(req, perms)
        self.assertFalse(res["success"])
        self.assertIn("Workdir not allowed", res["stderr"])

    # ------------------------------------------------------------------
    # Path traversal bypass regression (startswith prefix collision)
    # ------------------------------------------------------------------

    def test_denies_path_traversal_prefix_sibling(self):
        """Ensure /tmp/foo-evil is NOT allowed when /tmp/foo is the root."""
        import tempfile, os
        # Create two sibling directories: foo and foo-evil
        base = Path(tempfile.mkdtemp())
        allowed = base / "foo"
        sibling = base / "foo-evil"
        allowed.mkdir()
        sibling.mkdir()
        try:
            perms = ExecutionPermissionModel(
                allowed_roots=[allowed],
                allowed_commands=[_PYTHON],
            )
            # workdir is sibling — must be denied
            req = SkillExecutionRequest(
                skill_name="test",
                command=[_PYTHON, "-c", "print('traversal')"],
                workdir=sibling,
            )
            res = self.engine.execute(req, perms)
            self.assertFalse(res["success"])
            self.assertIn("Workdir not allowed", res["stderr"])
        finally:
            import shutil
            shutil.rmtree(base, ignore_errors=True)

    def test_allows_subdirectory_of_permitted_root(self):
        """Subdirectories of an allowed root must be allowed."""
        subdir = self.root / "subdir"
        subdir.mkdir()
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[_PYTHON, "-c", "print('subdir ok')"],
            workdir=subdir,
        )
        res = self.engine.execute(req, perms)
        self.assertTrue(res["success"])
        self.assertIn("subdir ok", res["stdout"])

    # ------------------------------------------------------------------
    # Timeout handling
    # ------------------------------------------------------------------

    def test_timeout_returns_clean_result(self):
        """A hanging command must return a SandboxResult, not raise."""
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[_PYTHON, "-c", "import time; time.sleep(60)"],
            workdir=self.root,
            timeout_s=1,
        )
        res = self.engine.execute(req, perms)
        self.assertFalse(res["success"])
        self.assertEqual(res["returncode"], 124)
        self.assertIn("timed out", res["stderr"])

    # ------------------------------------------------------------------
    # Audit fields on SandboxResult
    # ------------------------------------------------------------------

    def test_result_includes_duration(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[_PYTHON, "-c", "pass"],
            workdir=self.root,
        )
        ok, result = self.sandbox.run(
            command=req.command,
            workdir=req.workdir,
            permission_model=perms,
        )
        self.assertIsInstance(result, SandboxResult)
        self.assertGreaterEqual(result.duration_s, 0.0)
        self.assertFalse(result.timed_out)

    def test_timeout_result_sets_timed_out_flag(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        ok, result = self.sandbox.run(
            command=[_PYTHON, "-c", "import time; time.sleep(60)"],
            workdir=self.root,
            permission_model=perms,
            timeout_s=1,
        )
        self.assertFalse(ok)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.returncode, 124)

    # ------------------------------------------------------------------
    # Empty command guard
    # ------------------------------------------------------------------

    def test_denies_empty_command(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[_PYTHON],
        )
        ok, result = self.sandbox.run(
            command=[],
            workdir=self.root,
            permission_model=perms,
        )
        self.assertFalse(ok)
        self.assertIn("Empty command", result.stderr)


if __name__ == "__main__":
    unittest.main()
