import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.risk_register import RiskRecord, RiskRegister  # noqa: E402


class RiskRegisterTests(unittest.TestCase):
    def _sample(self):
        return [
            RiskRecord("R1", "P1", 8, 3, 3, "open", "high", "2026-02-20T00:00:00"),
            RiskRecord("R2", "P2", 4, 2, 2, "mitigated", "medium", "2026-02-23T00:00:00"),
        ]

    def test_grid_and_heatmap(self):
        register = RiskRegister(self._sample())
        rows = register.grid_rows()
        self.assertEqual(len(rows), 2)
        heatmap = register.heatmap()
        self.assertEqual(heatmap["L3-I3"], 1)

    def test_aging_view(self):
        register = RiskRegister(self._sample())
        aging = register.aging_view("2026-02-24T00:00:00")
        self.assertEqual(aging[0]["age_days"], "4")


if __name__ == "__main__":
    unittest.main()
