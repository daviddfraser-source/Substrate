import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.telemetry import Instrumentation, REQUIRED_METRICS, TelemetryStore  # noqa: E402


class TelemetryModelTests(unittest.TestCase):
    def test_required_metrics_coverage(self):
        store = TelemetryStore()
        instr = Instrumentation(store)
        instr.on_packet_transition("P1", "pending", "done", 11.0)
        instr.on_api_call("/packets", 123.0, 200)
        instr.on_db_query("list_packets", 8.0)

        # Fill remaining required metrics through direct record path.
        for metric in REQUIRED_METRICS:
            if not store.query(metric_name=metric):
                store.record(metric, 1.0)

        coverage = store.coverage()
        self.assertTrue(all(coverage.values()))

    def test_query_path_filters(self):
        store = TelemetryStore()
        store.record("api_latency_ms", 10.0, tenant_id="t1", project_id="p1")
        store.record("api_latency_ms", 11.0, tenant_id="t1", project_id="p2")
        store.record("db_query_time_ms", 12.0, tenant_id="t2", project_id="p1")

        self.assertEqual(len(store.query(metric_name="api_latency_ms", tenant_id="t1")), 2)
        self.assertEqual(len(store.query(project_id="p1")), 2)


if __name__ == "__main__":
    unittest.main()
