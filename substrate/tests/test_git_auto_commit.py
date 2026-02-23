import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, str(ROOT / ".governance" / "wbs_cli.py")]
WBS = ROOT / ".governance" / "wbs.json"
STATE = ROOT / ".governance" / "wbs-state.json"
GIT_GOV = ROOT / ".governance" / "git-governance.json"


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def write_git_mode(mode: str, auto_commit: bool):
    payload = {
        "version": "1.0",
        "mode": mode,
        "auto_commit": auto_commit,
        "commit_protocol_version": "1",
        "stage_files": [".governance/wbs-state.json"],
    }
    GIT_GOV.write_text(json.dumps(payload, indent=2) + "\n")


class GitAutoCommitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None
        cls._git_backup = GIT_GOV.read_bytes() if GIT_GOV.exists() else None

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

        if cls._git_backup is None:
            GIT_GOV.unlink(missing_ok=True)
        else:
            GIT_GOV.write_bytes(cls._git_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        payload = {
            "metadata": {"project_name": "git-auto", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
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

    def test_disabled_mode_preserves_claim_behavior(self):
        write_git_mode("disabled", True)
        proc = run_cli(["claim", "A", "agent"])
        self.assertIn("claimed by agent", proc.stdout)
        self.assertNotIn("warning", proc.stdout.lower())

    def test_advisory_mode_warns_but_allows_claim(self):
        write_git_mode("advisory", True)
        proc = run_cli(["claim", "A", "agent"])
        self.assertIn("claimed by agent", proc.stdout)
        self.assertIn("advisory warning", proc.stdout.lower())
        state = json.loads(STATE.read_text())
        self.assertEqual(state["packets"]["A"]["status"], "in_progress")

    def test_strict_mode_fails_when_commit_unavailable_and_rolls_back(self):
        write_git_mode("strict", True)
        proc = run_cli(["claim", "A", "agent"], expect=1)
        self.assertIn("strict mode", proc.stdout.lower())
        self.assertIn("rolled back", proc.stdout.lower())
        state = json.loads(STATE.read_text())
        self.assertEqual(state["packets"]["A"]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
