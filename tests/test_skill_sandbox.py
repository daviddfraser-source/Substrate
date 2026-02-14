import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from governed_platform.skills.permissions import ExecutionPermissionModel  # noqa: E402
from governed_platform.skills.sandbox import SubprocessSandbox  # noqa: E402
from governed_platform.skills.engine import SkillExecutionEngine, SkillExecutionRequest  # noqa: E402


class SkillSandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sandbox = SubprocessSandbox()
        self.engine = SkillExecutionEngine(self.sandbox)

    def tearDown(self):
        self.tmp.cleanup()

    def test_allows_permitted_command_and_path(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[sys.executable],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[sys.executable, "-c", "print('ok')"],
            workdir=self.root,
        )
        res = self.engine.execute(req, perms)
        self.assertTrue(res["success"])
        self.assertIn("ok", res["stdout"])

    def test_denies_unapproved_command(self):
        perms = ExecutionPermissionModel(
            allowed_roots=[self.root],
            allowed_commands=[sys.executable],
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
            allowed_commands=[sys.executable],
        )
        req = SkillExecutionRequest(
            skill_name="test",
            command=[sys.executable, "-c", "print('ok')"],
            workdir=self.root,
        )
        res = self.engine.execute(req, perms)
        self.assertFalse(res["success"])
        self.assertIn("Workdir not allowed", res["stderr"])


if __name__ == "__main__":
    unittest.main()
