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


class OptionalFeatureTests(unittest.TestCase):
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
            "metadata": {"project_name": "optional-features", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A", "wbs_ref": "1.1", "area_id": "1.0", "title": "A", "scope": ""},
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

    def test_done_checklist_and_evidence_verify(self):
        run_cli(["claim", "A", "op"])
        checklist = Path(tempfile.mkstemp(suffix="-check.md")[1])
        checklist.write_text("- [x] validated\n")
        try:
            fail = run_cli(["done", "A", "op", "no evidence paths", "--risk", "none", "--verify-evidence"], expect=1)
            self.assertIn("no file paths", fail.stdout.lower())
            run_cli(
                [
                    "done",
                    "A",
                    "op",
                    "Evidence: .governance/wbs_cli.py",
                    "--risk",
                    "none",
                    "--checklist",
                    str(checklist),
                    "--verify-evidence",
                ]
            )
        finally:
            checklist.unlink(missing_ok=True)

    def test_delivery_report_mode_profile_stale_and_closeout_readiness(self):
        run_cli(["claim", "A", "op"])
        run_cli(["done", "A", "op", "Evidence: .governance/wbs_cli.py", "--risk", "none"])

        report = json.loads(run_cli(["--json", "delivery-report", "1.0"]).stdout)
        self.assertEqual(report["scope_type"], "area")
        self.assertGreaterEqual(len(report["packet_lines"]), 1)

        run_cli(["mode-profile", "set", "strict"])
        mode = json.loads(run_cli(["--json", "mode-profile", "show"]).stdout)
        self.assertEqual(mode["mode"], "strict")

        stale = json.loads(run_cli(["--json", "stale", "5"]).stdout)
        self.assertIn("warn_factor", stale)
        self.assertIn("critical_factor", stale)

        readiness = json.loads(run_cli(["--json", "closeout-readiness", "1"]).stdout)
        self.assertEqual(readiness["area_id"], "1.0")
        self.assertIn("score", readiness)

        run_cli(["mode-profile", "set", "balanced"])

    def test_packet_presets_and_wbs_diff(self):
        presets = json.loads(run_cli(["--json", "packet-presets"]).stdout)
        self.assertIn("break-fix", presets["presets"])

        run_cli(
            [
                "add-packet",
                "C",
                "1.0",
                "Preset Packet",
                "--preset",
                "doc-only",
                "--wbs-approval",
                "WBS-APPROVED:TEST-ADD-PACKET",
            ]
        )
        current = json.loads(WBS.read_text())
        pkt = next(p for p in current["packets"] if p["id"] == "C")
        self.assertIn("documentation-only update", pkt.get("scope", "").lower())

        with tempfile.TemporaryDirectory() as td:
            old_path = Path(td) / "old.json"
            new_path = Path(td) / "new.json"
            old_payload = {"metadata": {}, "work_areas": [{"id": "1.0", "title": "A"}], "packets": [], "dependencies": {}}
            new_payload = {
                "metadata": {},
                "work_areas": [{"id": "1.0", "title": "A"}, {"id": "2.0", "title": "B"}],
                "packets": [{"id": "P1", "wbs_ref": "2.1", "area_id": "2.0", "title": "P1", "scope": "s"}],
                "dependencies": {},
            }
            old_path.write_text(json.dumps(old_payload))
            new_path.write_text(json.dumps(new_payload))
            diff = json.loads(run_cli(["--json", "wbs-diff", str(old_path), str(new_path)]).stdout)
            self.assertEqual(diff["summary"]["areas_added"], 1)
            self.assertEqual(diff["summary"]["packets_added"], 1)


if __name__ == "__main__":
    unittest.main()
