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
RISK_REGISTER = ROOT / ".governance" / "residual-risk-register.json"


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class ResidualRiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None
        cls._risk_backup = RISK_REGISTER.read_bytes() if RISK_REGISTER.exists() else None

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
        if cls._risk_backup is None:
            RISK_REGISTER.unlink(missing_ok=True)
        else:
            RISK_REGISTER.write_bytes(cls._risk_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        RISK_REGISTER.unlink(missing_ok=True)
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

    def test_done_declared_risks_create_register_entries(self):
        run_cli(["claim", "A", "op"])
        risks_json = json.dumps(
            [
                {
                    "description": "Load spike fallback path untested",
                    "likelihood": "medium",
                    "impact": "high",
                    "confidence": "medium",
                }
            ]
        )
        run_cli(["done", "A", "op", "implemented", "--risk", "declared", "--risk-json", risks_json])

        register = json.loads(RISK_REGISTER.read_text())
        self.assertEqual(len(register.get("risks", [])), 1)
        risk = register["risks"][0]
        self.assertEqual(risk["packet_id"], "A")
        self.assertEqual(risk["status"], "open")

        state = json.loads(STATE.read_text())
        completed = [e for e in state.get("log", []) if e.get("packet_id") == "A" and e.get("event") == "completed"]
        self.assertTrue(completed)
        self.assertEqual(completed[-1].get("risk_ack"), "declared")
        self.assertEqual(len(completed[-1].get("risk_ids", [])), 1)

    def test_risk_cli_lifecycle_commands(self):
        add = run_cli(
            [
                "--json",
                "risk-add",
                "A",
                "op",
                "Third-party outage fallback unknown",
                "--impact",
                "critical",
                "--likelihood",
                "low",
                "--confidence",
                "high",
            ]
        )
        risk_id = json.loads(add.stdout)["risk_id"]
        self.assertTrue(risk_id.startswith("RR-"))

        listed = json.loads(run_cli(["--json", "risk-list", "--status", "open"]).stdout)
        self.assertTrue(any(r.get("risk_id") == risk_id for r in listed.get("risks", [])))

        shown = json.loads(run_cli(["--json", "risk-show", risk_id]).stdout)
        self.assertEqual(shown["risk"]["impact"], "critical")

        run_cli(["risk-update-status", risk_id, "accepted", "op", "accepted for v1 release"])

        summary = json.loads(run_cli(["--json", "risk-summary"]).stdout)
        self.assertGreaterEqual(summary.get("total", 0), 1)
        self.assertEqual(summary.get("counts", {}).get("accepted", 0), 1)


if __name__ == "__main__":
    unittest.main()
