import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from governed_platform.governance.git_ledger import (
    build_packet_branch_name,
    close_packet_branch,
    current_branch,
    open_packet_branch,
)

CLI = [sys.executable, str(ROOT / ".governance" / "wbs_cli.py")]
WBS = ROOT / ".governance" / "wbs.json"
STATE = ROOT / ".governance" / "wbs-state.json"


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def run_git(cwd: Path, args):
    proc = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(f"git failed: {' '.join(args)}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return proc.stdout.strip()


class GitBranchHelpersTests(unittest.TestCase):
    def test_branch_name_normalization(self):
        name = build_packet_branch_name("UPG 056", "Codex/Lead")
        self.assertEqual(name, "substrate/upg-056/codex-lead")

    def test_open_and_close_branch_flow_in_temp_repo(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run_git(repo, ["init"])
            run_git(repo, ["config", "user.email", "t@example.com"])
            run_git(repo, ["config", "user.name", "tester"])

            (repo / "README.md").write_text("hello\n")
            run_git(repo, ["add", "README.md"])
            run_git(repo, ["commit", "-m", "init"])
            base = run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])

            ok, branch, reason = open_packet_branch(repo, packet_id="UPG-056", agent="codex")
            self.assertTrue(ok, reason)
            self.assertEqual(branch, "substrate/upg-056/codex")
            active_ok, active = current_branch(repo)
            self.assertTrue(active_ok)
            self.assertEqual(active, branch)

            (repo / "branch.txt").write_text("branch work\n")
            run_git(repo, ["add", "branch.txt"])
            run_git(repo, ["commit", "-m", "work"])

            ok, branch, reason = close_packet_branch(
                repo,
                packet_id="UPG-056",
                agent="codex",
                base_branch=base,
                delete_branch=True,
            )
            self.assertTrue(ok, reason)
            active_ok, active = current_branch(repo)
            self.assertTrue(active_ok)
            self.assertEqual(active, base)
            branch_list = run_git(repo, ["branch", "--list", branch])
            self.assertEqual(branch_list, "")


class CliBranchGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None

    @classmethod
    def tearDownClass(cls):
        if cls._wbs_backup is None:
            WBS.unlink(missing_ok=True)
        else:
            WBS.write_bytes(cls._wbs_backup)

        if cls._state_backup is None:
            STATE.unlink(missing_ok=True)
        else:
            STATE.write_bytes(cls._state_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        payload = {
            "metadata": {"project_name": "branch-guard", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A", "wbs_ref": "1.1", "area_id": "1.0", "title": "A", "scope": "scope"},
            ],
            "dependencies": {},
        }
        fd, path = tempfile.mkstemp(suffix="-wbs.json")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        try:
            run_cli(["init", path])
        finally:
            os.unlink(path)

    def test_branch_open_requires_in_progress_packet(self):
        proc = run_cli(["git-branch-open", "A", "agent"], expect=1)
        self.assertIn("not in_progress", proc.stdout)


if __name__ == "__main__":
    unittest.main()
