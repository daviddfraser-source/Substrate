import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import start  # noqa: E402


class StartValidateTests(unittest.TestCase):
    def test_validate_scaffold_data_accepts_current_shape(self):
        cfg = {
            "project_name": "proj",
            "default_agent": "codex-lead",
            "dashboard_port": 8080,
            "wbs_template": "templates/wbs-codex-full.json",
            "wbs_file": ".governance/wbs.json",
            "enable_skills": ["skill-a"],
            "ci_profile": "full",
        }
        self.assertEqual(start._validate_scaffold_data(cfg), [])

    def test_validate_scaffold_data_rejects_invalid_values(self):
        cfg = {
            "project_name": "",
            "default_agent": "",
            "dashboard_port": 70000,
            "wbs_template": "",
            "wbs_file": "",
            "enable_skills": ["", 42],
            "ci_profile": "invalid",
        }
        errs = start._validate_scaffold_data(cfg)
        self.assertTrue(any("dashboard_port" in e for e in errs))
        self.assertTrue(any("ci_profile" in e for e in errs))
        self.assertTrue(any("enable_skills" in e for e in errs))

    def test_start_validate_flag(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "start.py"), "--validate"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertIn(proc.returncode, (0, 1), msg=proc.stdout + proc.stderr)
        self.assertIn("Scaffold validation", proc.stdout)


if __name__ == "__main__":
    unittest.main()
