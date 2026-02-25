import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.analytics import AnalyticsService  # noqa: E402


class AnalyticsPhase5Tests(unittest.TestCase):
    def test_aggregation_and_exports(self):
        svc = AnalyticsService()
        svc.record("t1", "p1", "latency_ms", 100)
        svc.record("t1", "p1", "latency_ms", 200)
        svc.record("t1", "p1", "token_burn", 300)

        summary = svc.aggregate("t1", "p1")
        self.assertEqual(summary["event_count"], 3)
        names = [m["metric_name"] for m in summary["metrics"]]
        self.assertIn("latency_ms", names)

        csv_payload = svc.export_csv("t1", "p1")
        self.assertIn("metric_name,count,total,average", csv_payload)
        json_payload = svc.export_json("t1", "p1")
        self.assertIn("latency_ms", json_payload)

    def test_endpoint_contracts(self):
        svc = AnalyticsService()
        svc.record("t1", "p1", "requests", 1)
        ok = svc.endpoint_summary("t1", "p1")
        self.assertTrue(ok["ok"])
        bad = svc.endpoint_export("t1", "p1", fmt="xml")
        self.assertFalse(bad["ok"])


if __name__ == "__main__":
    unittest.main()
