import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class K8sProfileTests(unittest.TestCase):
    def test_k8s_assets_exist(self):
        for rel in [
            "infra/k8s/deployment.yaml",
            "infra/k8s/service.yaml",
            "infra/k8s/servicemonitor.yaml",
        ]:
            self.assertTrue((ROOT / rel).exists())

    def test_probe_and_metrics_paths_present(self):
        deployment = (ROOT / "infra/k8s/deployment.yaml").read_text(encoding="utf-8")
        self.assertIn("/health", deployment)
        monitor = (ROOT / "infra/k8s/servicemonitor.yaml").read_text(encoding="utf-8")
        self.assertIn("/metrics", monitor)


if __name__ == "__main__":
    unittest.main()
