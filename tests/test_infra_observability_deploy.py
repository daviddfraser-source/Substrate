import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InfraObservabilityDeployTests(unittest.TestCase):
    def test_observability_compose_profile_exists(self):
        compose = ROOT / "docker-compose.observability.yml"
        self.assertTrue(compose.exists())
        text = compose.read_text(encoding="utf-8")
        for token in [
            "api:",
            "worker:",
            "otel-collector:",
            "prometheus:",
            "grafana:",
            "db:",
            "redis:",
        ]:
            self.assertIn(token, text)

    def test_observability_configs_exist(self):
        otel = ROOT / "infra/observability/otel-collector.yaml"
        prom = ROOT / "infra/observability/prometheus.yml"
        self.assertTrue(otel.exists())
        self.assertTrue(prom.exists())
        self.assertIn("receivers:", otel.read_text(encoding="utf-8"))
        self.assertIn("scrape_configs:", prom.read_text(encoding="utf-8"))

    def test_runbook_references_startup_and_validation(self):
        runbook = ROOT / "docs/codex-migration/phase5-infra-observability-deploy-runbook.md"
        self.assertTrue(runbook.exists())
        text = runbook.read_text(encoding="utf-8")
        self.assertIn("docker compose -f docker-compose.observability.yml up --build", text)
        self.assertIn("python3 -m unittest", text)


if __name__ == "__main__":
    unittest.main()
