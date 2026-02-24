import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DependencyGraphUiTests(unittest.TestCase):
    def test_dependency_graph_module_exists(self):
        target = ROOT / "app/src/ui/dependencyGraph.ts"
        self.assertTrue(target.exists())

    def test_cycle_and_navigation_contracts_present(self):
        content = (ROOT / "app/src/ui/dependencyGraph.ts").read_text(encoding="utf-8")
        self.assertIn("detectCycles", content)
        self.assertIn("resolvePacketNavigation", content)
        self.assertIn("blocked", content)
        self.assertIn("cyclic", content)


if __name__ == "__main__":
    unittest.main()
