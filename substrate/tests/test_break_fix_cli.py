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
BREAK_FIX_LOG = ROOT / ".governance" / "break-fix-log.json"


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class BreakFixCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None
        cls._break_fix_backup = BREAK_FIX_LOG.read_bytes() if BREAK_FIX_LOG.exists() else None

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
        if cls._break_fix_backup is None:
            BREAK_FIX_LOG.unlink(missing_ok=True)
        else:
            BREAK_FIX_LOG.write_bytes(cls._break_fix_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        BREAK_FIX_LOG.unlink(missing_ok=True)
        payload = {
            "metadata": {"project_name": "break-fix-cli", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
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

    def test_break_fix_cli_lifecycle_requires_resolve_evidence(self):
        opened = json.loads(
            run_cli(
                [
                    "--json",
                    "break-fix-open",
                    "op",
                    "Regression fix",
                    "Intermittent parser error",
                    "--severity",
                    "high",
                    "--packet",
                    "A",
                ]
            ).stdout
        )
        fix_id = opened["fix_id"]
        run_cli(["break-fix-start", fix_id, "op"])

        failed = run_cli(["break-fix-resolve", fix_id, "op", "patched parser", "--findings", "edge path"], expect=1)
        self.assertIn("requires --evidence", failed.stdout)

        run_cli(
            [
                "break-fix-resolve",
                fix_id,
                "op",
                "patched parser",
                "--evidence",
                "src/app/main.py,tests/test_main.py",
            ]
        )
        shown = json.loads(run_cli(["--json", "break-fix-show", fix_id]).stdout)["break_fix"]
        self.assertEqual(shown["status"], "resolved")
        self.assertGreaterEqual(len(shown.get("history", [])), 3)

    def test_break_fix_reporting_integrates_into_status_briefing_and_export(self):
        fix_id = json.loads(
            run_cli(
                [
                    "--json",
                    "break-fix-open",
                    "op",
                    "Open issue",
                    "Needs follow-up",
                    "--packet",
                    "A",
                ]
            ).stdout
        )["fix_id"]
        run_cli(["break-fix-start", fix_id, "op"])

        status = json.loads(run_cli(["--json", "status"]).stdout)
        self.assertIn("break_fix_summary", status)
        packet = status["areas"][0]["packets"][0]
        self.assertGreaterEqual(packet.get("break_fix_active", 0), 1)

        briefing = json.loads(run_cli(["--json", "briefing"]).stdout)
        self.assertIn("break_fix", briefing)
        self.assertGreaterEqual(briefing["break_fix"].get("active", 0), 1)

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "break-fix.json"
            run_cli(["export", "break-fix-json", str(out)])
            exported = json.loads(out.read_text())
            self.assertIn("break_fix", exported)
            self.assertIn("summary", exported)
            self.assertTrue(any(item.get("fix_id") == fix_id for item in exported["break_fix"]))


if __name__ == "__main__":
    unittest.main()
