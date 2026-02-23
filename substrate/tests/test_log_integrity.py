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


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class LogIntegrityTests(unittest.TestCase):
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
            "metadata": {"project_name": "t", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [{"id": "A", "wbs_ref": "1.1", "area_id": "1.0", "title": "A", "scope": ""}],
            "dependencies": {},
        }
        fd, path = tempfile.mkstemp(suffix="-wbs.json")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        try:
            run_cli(["init", path])
        finally:
            os.unlink(path)

    def test_plain_mode_verification_passes(self):
        run_cli(["claim", "A", "op"])
        result = json.loads(run_cli(["--json", "verify-log"]).stdout)
        self.assertTrue(result["valid"])
        self.assertEqual(result["mode"], "plain")
        self.assertEqual(result["hashed_events"], 0)

    def test_hash_chain_mode_records_hash_fields(self):
        run_cli(["log-mode", "hash-chain"])
        run_cli(["claim", "A", "op"])
        run_cli(["done", "A", "op", "done", "--risk", "none"])

        state = json.loads(STATE.read_text())
        self.assertEqual(state.get("log_integrity_mode"), "hash_chain")
        self.assertTrue(all("hash" in e for e in state["log"]))
        self.assertTrue(all("prev_hash" in e for e in state["log"]))
        self.assertTrue(all("event_id" in e for e in state["log"]))

        result = json.loads(run_cli(["--json", "verify-log"]).stdout)
        self.assertTrue(result["valid"])
        self.assertEqual(result["hashed_events"], 2)

    def test_verify_log_detects_tampering(self):
        run_cli(["log-mode", "hash-chain"])
        run_cli(["claim", "A", "op"])
        run_cli(["done", "A", "op", "done", "--risk", "none"])

        state = json.loads(STATE.read_text())
        state["log"][0]["notes"] = "tampered"
        STATE.write_text(json.dumps(state, indent=2) + "\n")

        proc = run_cli(["--json", "verify-log"], expect=1)
        result = json.loads(proc.stdout)
        self.assertFalse(result["valid"])
        self.assertTrue(any("hash mismatch" in issue for issue in result["issues"]))


if __name__ == "__main__":
    unittest.main()
