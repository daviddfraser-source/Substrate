import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.api.operations import (  # noqa: E402
    MetricsStore,
    WebhookDispatcher,
    health_endpoint,
    log_json,
    metrics_endpoint,
)


class OperationsEndpointTests(unittest.TestCase):
    def test_health_endpoint(self):
        payload = health_endpoint()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("timestamp", payload)

    def test_metrics_endpoint_round_trip(self):
        store = MetricsStore()
        store.record("api_latency_ms", 123.4, "tenant-a")
        payload = metrics_endpoint(store)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["events"][0]["metric_name"], "api_latency_ms")

    def test_webhook_dispatch(self):
        dispatcher = WebhookDispatcher()
        event = dispatcher.publish("packet.transition", {"packet_id": "PRD-3-3"})
        self.assertEqual(event["event_type"], "packet.transition")
        self.assertEqual(len(dispatcher.events()), 1)

    def test_structured_log_fields(self):
        line = log_json("risk.created", "corr-1", "codex", {"risk_id": "RR-0001"})
        payload = json.loads(line)
        self.assertEqual(payload["event_type"], "risk.created")
        self.assertEqual(payload["correlation_id"], "corr-1")
        self.assertEqual(payload["actor"], "codex")
        self.assertIn("timestamp", payload)


if __name__ == "__main__":
    unittest.main()
