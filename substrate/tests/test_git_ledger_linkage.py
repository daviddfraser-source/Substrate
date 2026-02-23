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


class GitLedgerLinkageTests(unittest.TestCase):
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
            "metadata": {"project_name": "git-link", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
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

    def test_advisory_claim_records_warning_link_fields(self):
        write_git_mode("advisory", True)
        run_cli(["claim", "A", "agent"])
        state = json.loads(STATE.read_text())
        linked = [e for e in state["log"] if e.get("packet_id") == "A" and e.get("git_link_status")]
        self.assertTrue(linked)
        self.assertEqual(linked[-1]["git_link_status"], "warning")
        self.assertEqual(linked[-1]["git_action"], "claim")
        self.assertEqual(linked[-1]["git_actor"], "agent")
        self.assertIn("git", linked[-1]["git_link_error"].lower())

    def test_verify_ledger_strict_fails_on_warnings(self):
        write_git_mode("advisory", True)
        run_cli(["claim", "A", "agent"])

        relaxed = json.loads(run_cli(["--json", "git-verify-ledger"]).stdout)
        self.assertTrue(relaxed["valid"])
        self.assertGreaterEqual(relaxed["warning_entries"], 1)

        strict_proc = run_cli(["--json", "git-verify-ledger", "--strict"], expect=1)
        strict = json.loads(strict_proc.stdout)
        self.assertFalse(strict["valid"])
        self.assertGreaterEqual(len(strict["warnings"]), 1)

    def test_export_ledger_writes_json_snapshot(self):
        write_git_mode("advisory", True)
        run_cli(["claim", "A", "agent"])
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "git-ledger.json"
            run_cli(["git-export-ledger", str(out_path)])
            payload = json.loads(out_path.read_text())
            self.assertIn("entries", payload)
            self.assertTrue(payload["entries"])
            self.assertIn("git_link_status", payload["entries"][0])


if __name__ == "__main__":
    unittest.main()
