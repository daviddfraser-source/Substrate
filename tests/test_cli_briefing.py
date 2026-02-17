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


class CliBriefingTests(unittest.TestCase):
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
            "metadata": {"project_name": "briefing-test", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A", "wbs_ref": "1.1", "area_id": "1.0", "title": "A", "scope": ""},
                {"id": "B", "wbs_ref": "1.2", "area_id": "1.0", "title": "B", "scope": ""},
                {"id": "C", "wbs_ref": "1.3", "area_id": "1.0", "title": "C", "scope": ""},
            ],
            "dependencies": {"B": ["A"]},
        }
        fd, path = tempfile.mkstemp(suffix="-wbs.json")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        try:
            run_cli(["init", path])
        finally:
            os.unlink(path)
        run_cli(["claim", "A", "op"])

    def test_briefing_json_shape(self):
        data = json.loads(run_cli(["--json", "briefing"]).stdout)
        self.assertEqual(data["schema_id"], "wbs.briefing")
        self.assertEqual(data["schema_version"], "1.0")
        for key in (
            "project",
            "counts",
            "ready_packets",
            "blocked_packets",
            "active_assignments",
            "recent_events",
            "limits",
            "truncated",
        ):
            self.assertIn(key, data)

        ready_ids = [p["id"] for p in data["ready_packets"]]
        self.assertIn("C", ready_ids)

        blocked = next((p for p in data["blocked_packets"] if p["id"] == "B"), None)
        self.assertIsNotNone(blocked)
        self.assertTrue(any(b["packet_id"] == "A" for b in blocked["blockers"]))

        active = next((a for a in data["active_assignments"] if a["packet_id"] == "A"), None)
        self.assertIsNotNone(active)
        self.assertEqual(active["agent"], "op")

    def test_briefing_recent_limit_and_compact(self):
        run_cli(["note", "A", "op", "progress"])
        run_cli(["reset", "A"])
        run_cli(["claim", "A", "op"])
        data = json.loads(run_cli(["--json", "briefing", "--recent", "2", "--compact"]).stdout)
        self.assertLessEqual(len(data["recent_events"]), 2)
        self.assertEqual(data["mode"], "compact")
        self.assertTrue(data["truncated"])

    def test_briefing_text_sections(self):
        out = run_cli(["briefing"]).stdout
        self.assertIn("Summary", out)
        self.assertIn("Ready Packets", out)
        self.assertIn("Blocked Packets", out)
        self.assertIn("Active Assignments", out)
        self.assertIn("Recent Events", out)

    def test_briefing_is_read_only(self):
        before = STATE.read_text()
        run_cli(["--json", "briefing", "--recent", "5"])
        run_cli(["briefing", "--compact"])
        after = STATE.read_text()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
