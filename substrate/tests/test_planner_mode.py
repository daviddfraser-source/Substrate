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


def write_json_temp(payload):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(payload, f)
    return Path(path)


class PlannerModeTests(unittest.TestCase):
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

    def test_plan_from_json_exports_valid_wbs(self):
        spec = {
            "project_name": "Planner Smoke",
            "approved_by": "tester",
            "work_areas": [
                {
                    "id": "1.0",
                    "title": "Discovery",
                    "packets": [
                        {
                            "id": "PLN-001",
                            "title": "Draft scope",
                            "scope": "Draft initial scope. Output: docs/scope.md",
                        }
                    ],
                },
                {
                    "id": "2.0",
                    "title": "Build",
                    "packets": [
                        {
                            "id": "PLN-002",
                            "title": "Implement change",
                            "scope": "Implement work. Output: src/",
                            "depends_on": ["PLN-001"],
                        },
                        {
                            "id": "PLN-003",
                            "title": "Validate behavior",
                            "scope": "Run tests and checks. Output: test report.",
                            "depends_on": ["PLN-002"],
                        },
                    ],
                },
            ],
        }
        spec_path = write_json_temp(spec)
        try:
            with tempfile.TemporaryDirectory() as td:
                out_path = Path(td) / "planned-wbs.json"
                run_cli(["plan", "--from-json", str(spec_path), "--output", str(out_path)])

                planned = json.loads(out_path.read_text())
                self.assertEqual(planned["metadata"]["project_name"], "Planner Smoke")
                self.assertIn("PLN-002", planned["dependencies"])
                self.assertEqual(planned["dependencies"]["PLN-002"], ["PLN-001"])

                run_cli(["init", str(out_path)])
                run_cli(["validate"])
        finally:
            spec_path.unlink(missing_ok=True)

    def test_plan_surfaces_cycle_detection_guidance(self):
        spec = {
            "project_name": "Cycle Test",
            "approved_by": "tester",
            "work_areas": [
                {
                    "id": "1.0",
                    "title": "Area",
                    "packets": [
                        {"id": "A", "title": "A", "scope": "A"},
                        {"id": "B", "title": "B", "scope": "B"},
                    ],
                }
            ],
            "dependencies": {
                "A": ["B"],
                "B": ["A"],
            },
        }
        spec_path = write_json_temp(spec)
        try:
            proc = run_cli(["plan", "--from-json", str(spec_path)], expect=1)
            self.assertIn("Dependency cycle detected", proc.stdout)
            self.assertIn("Action:", proc.stdout)
        finally:
            spec_path.unlink(missing_ok=True)

    def test_plan_normalizes_ids_and_dependency_aliases(self):
        spec = {
            "project_name": "Normalize Test",
            "approved_by": "tester",
            "work_areas": [
                {
                    "id": "Discovery & Scope",
                    "title": "Discovery",
                    "packets": [
                        {"id": "task one", "title": "Task One", "scope": "Define scope."},
                        {
                            "id": "task two",
                            "title": "Task Two",
                            "scope": "Review scope.",
                            "depends_on": ["task one"],
                        },
                    ],
                }
            ],
        }
        spec_path = write_json_temp(spec)
        try:
            with tempfile.TemporaryDirectory() as td:
                out_path = Path(td) / "planned-wbs.json"
                run_cli(["plan", "--from-json", str(spec_path), "--output", str(out_path)])
                planned = json.loads(out_path.read_text())

                self.assertEqual(planned["work_areas"][0]["id"], "DISCOVERY-SCOPE")
                packet_ids = [pkt["id"] for pkt in planned["packets"]]
                self.assertIn("TASK-ONE", packet_ids)
                self.assertIn("TASK-TWO", packet_ids)
                self.assertEqual(planned["dependencies"]["TASK-TWO"], ["TASK-ONE"])
        finally:
            spec_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
