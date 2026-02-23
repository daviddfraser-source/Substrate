import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, str(ROOT / ".governance" / "wbs_cli.py")]


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class CliPrdTests(unittest.TestCase):
    def test_prd_from_json_exports_markdown_and_wbs_draft(self):
        spec = {
            "project_name": "PRD Mode Test",
            "owner": "tester",
            "problem_statement": "Need a lightweight PRD flow.",
            "goals": ["Capture requirements", "Bridge to packet planning"],
            "users": ["Product owner", "Agent operator"],
            "functional_requirements": ["Create PRD markdown", "Optionally generate WBS draft"],
            "acceptance_criteria": ["PRD contains required sections", "WBS draft has packets"],
        }

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            spec_path = td_path / "spec.json"
            prd_path = td_path / "prd.md"
            wbs_path = td_path / "wbs-draft.json"
            spec_path.write_text(json.dumps(spec, indent=2))

            run_cli(
                [
                    "prd",
                    "--from-json",
                    str(spec_path),
                    "--output",
                    str(prd_path),
                    "--to-wbs",
                    str(wbs_path),
                ]
            )

            self.assertTrue(prd_path.exists())
            prd_text = prd_path.read_text()
            self.assertIn("# PRD Mode Test PRD", prd_text)
            self.assertIn("## Problem Statement", prd_text)
            self.assertIn("## Acceptance Criteria", prd_text)

            self.assertTrue(wbs_path.exists())
            wbs = json.loads(wbs_path.read_text())
            self.assertIn("packets", wbs)
            self.assertGreater(len(wbs["packets"]), 0)


if __name__ == "__main__":
    unittest.main()
