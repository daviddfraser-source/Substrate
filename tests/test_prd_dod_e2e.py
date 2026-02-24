import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PrdDodE2ETests(unittest.TestCase):
    def test_dod_script_passes(self):
        subprocess.run(["python3", "scripts/prd_dod_e2e.py"], cwd=ROOT, check=True)
        report = ROOT / "reports/dod-e2e-report.json"
        self.assertTrue(report.exists())
        payload = json.loads(report.read_text(encoding="utf-8"))
        self.assertTrue(payload["passed"])


if __name__ == "__main__":
    unittest.main()
