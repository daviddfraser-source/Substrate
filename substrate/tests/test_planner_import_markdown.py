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


def write_temp(content: str, suffix: str) -> Path:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return Path(path)


class PlannerImportMarkdownTests(unittest.TestCase):
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

    def test_import_adds_low_confidence_markers_for_ambiguous_bullets(self):
        markdown = """# Import Pilot
## Discovery
- [ ] Define acceptance criteria. Output: docs/acceptance.md
- Explore API hotspots for possible bottlenecks
## Build
- [ ] Implement optimization after Define acceptance criteria. Output: src/
"""
        md_path = write_temp(markdown, ".md")
        try:
            with tempfile.TemporaryDirectory() as td:
                out_path = Path(td) / "draft.json"
                run_cli(["plan", "--import-markdown", str(md_path), "--output", str(out_path)])
                draft = json.loads(out_path.read_text())

                self.assertTrue(draft.get("import_experimental"))
                self.assertTrue(isinstance(draft.get("import_warnings"), list))
                low_packets = [
                    pkt
                    for pkt in draft.get("packets", [])
                    if pkt.get("import_confidence") == "low" or pkt.get("import_requires_review")
                ]
                self.assertTrue(low_packets)
        finally:
            md_path.unlink(missing_ok=True)

    def test_import_apply_blocked_when_ambiguous_without_override(self):
        markdown = """# Import Pilot
## Discovery
- Explore API hotspots for possible bottlenecks
"""
        md_path = write_temp(markdown, ".md")
        try:
            proc = run_cli(["plan", "--import-markdown", str(md_path), "--apply"], expect=1)
            self.assertIn("manual review", proc.stdout.lower())
            self.assertIn("allow-ambiguous", proc.stdout)
        finally:
            md_path.unlink(missing_ok=True)

    def test_imported_draft_can_be_corrected_and_reexported_via_plan(self):
        markdown = """# Import Pilot
## Discovery
- Explore API hotspots for possible bottlenecks
"""
        md_path = write_temp(markdown, ".md")
        try:
            with tempfile.TemporaryDirectory() as td:
                draft_path = Path(td) / "draft.json"
                corrected_path = Path(td) / "corrected.json"
                final_path = Path(td) / "final.json"

                run_cli(["plan", "--import-markdown", str(md_path), "--output", str(draft_path)])
                draft = json.loads(draft_path.read_text())
                for pkt in draft.get("packets", []):
                    pkt["scope"] = "Analyze API hotspots. Output: docs/hotspots.md"
                    pkt["import_confidence"] = "medium"
                    pkt["import_requires_review"] = False
                draft["import_warnings"] = []
                corrected_path.write_text(json.dumps(draft, indent=2) + "\n")

                run_cli(["plan", "--from-json", str(corrected_path), "--output", str(final_path)])
                run_cli(["init", str(final_path)])
                run_cli(["validate"])
        finally:
            md_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
