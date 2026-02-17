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


def write_wbs(payload):
    fd, path = tempfile.mkstemp(suffix="-wbs.json")
    with os.fdopen(fd, "w") as f:
        json.dump(payload, f)
    return path


class ValidateStrictTests(unittest.TestCase):
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

    def _init_with_payload(self, payload):
        path = write_wbs(payload)
        try:
            run_cli(["init", path])
        finally:
            os.unlink(path)

    def test_validate_standard_allows_base_packet_shape(self):
        payload = {
            "metadata": {"project_name": "t", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A-1", "wbs_ref": "1.1", "area_id": "1.0", "title": "A1", "scope": "scope"}
            ],
            "dependencies": {},
        }
        self._init_with_payload(payload)

        proc = run_cli(["validate"])
        self.assertIn("Validation passed", proc.stdout)

    def test_validate_strict_reports_actionable_packet_errors(self):
        payload = {
            "metadata": {"project_name": "t", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A-1", "wbs_ref": "1.1", "area_id": "1.0", "title": "A1", "scope": "scope"}
            ],
            "dependencies": {},
        }
        self._init_with_payload(payload)

        proc = run_cli(["validate", "--strict"], expect=1)
        self.assertIn("A-1: missing required field: packet_id", proc.stdout)
        self.assertIn("Validation failed (strict)", proc.stdout)

    def test_validate_strict_passes_for_canonical_packet_shape(self):
        payload = {
            "metadata": {"project_name": "t", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {
                    "id": "A-1",
                    "wbs_ref": "1.1",
                    "area_id": "1.0",
                    "title": "A1",
                    "scope": "scope",
                    "packet_id": "A-1",
                    "wbs_refs": ["1.1"],
                    "purpose": "Validate strict packet schema for canonical packets.",
                    "status": "PENDING",
                    "owner": "codex",
                    "priority": "MEDIUM",
                    "preconditions": [],
                    "required_inputs": ["README.md"],
                    "required_actions": ["Run strict validation"],
                    "required_outputs": ["Validation report"],
                    "validation_checks": ["validate --strict exits 0"],
                    "exit_criteria": ["Validation passes"],
                    "halt_conditions": ["Schema registry missing"],
                }
            ],
            "dependencies": {},
        }
        self._init_with_payload(payload)

        proc = run_cli(["validate", "--strict"])
        self.assertIn("Validation passed (strict)", proc.stdout)


if __name__ == "__main__":
    unittest.main()
