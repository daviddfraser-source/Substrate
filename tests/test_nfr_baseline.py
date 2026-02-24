import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NfrBaselineTests(unittest.TestCase):
    def test_nfr_script_generates_report(self):
        subprocess.run(["bash", "scripts/nfr_baseline_check.sh"], cwd=ROOT, check=True, capture_output=True, text=True)
        report = ROOT / "reports/nfr-baseline.json"
        self.assertTrue(report.exists())
        payload = json.loads(report.read_text(encoding="utf-8"))
        self.assertTrue(payload["summary"]["passed"])


if __name__ == "__main__":
    unittest.main()
