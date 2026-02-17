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


class ContextBundleTests(unittest.TestCase):
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
            "metadata": {"project_name": "context-test", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A", "wbs_ref": "1.1", "area_id": "1.0", "title": "A", "scope": "See docs/PLAYBOOK.md"},
                {"id": "B", "wbs_ref": "1.2", "area_id": "1.0", "title": "B", "scope": ""},
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

        run_cli(["claim", "A", "agent-1"])
        run_cli(["note", "A", "agent-1", "Evidence path: docs/PLAYBOOK.md"])
        run_cli(
            [
                "handover",
                "A",
                "agent-1",
                "session shift",
                "--to",
                "agent-2",
                "--progress",
                "partial implementation",
                "--remaining",
                "tests|docs",
            ]
        )
        run_cli(["resume", "A", "agent-2"])

    def test_context_json_shape(self):
        data = json.loads(run_cli(["--json", "context", "A"]).stdout)
        self.assertEqual(data["schema_id"], "wbs.context_bundle")
        self.assertEqual(data["schema_version"], "1.0")
        for key in (
            "packet_definition",
            "runtime_state",
            "dependencies",
            "history",
            "handovers",
            "file_manifest",
            "truncation",
            "limits",
            "truncated",
        ):
            self.assertIn(key, data)

        downstream = data["dependencies"]["downstream"]
        self.assertTrue(any(item["packet_id"] == "B" for item in downstream))
        self.assertTrue(any(item["path"] == "docs/PLAYBOOK.md" for item in data["file_manifest"]))

    def test_context_limits_and_truncation(self):
        long_note = "x" * 4000
        run_cli(["note", "A", "agent-2", long_note])
        run_cli(["note", "A", "agent-2", long_note])

        data = json.loads(
            run_cli(
                [
                    "--json",
                    "context",
                    "A",
                    "--max-events",
                    "2",
                    "--max-notes-bytes",
                    "300",
                    "--max-handovers",
                    "1",
                    "--compact",
                ]
            ).stdout
        )
        self.assertLessEqual(len(data["history"]), 2)
        self.assertLessEqual(len(data["handovers"]), 1)
        self.assertEqual(data["mode"], "compact")
        self.assertTrue(data["truncated"])
        self.assertGreaterEqual(data["truncation"]["notes_bytes_dropped"], 0)


if __name__ == "__main__":
    unittest.main()
