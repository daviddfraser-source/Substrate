import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.graph_core import (  # noqa: E402
    critical_path,
    downstream_nodes,
    impact_analysis,
    postgres_recursive_cte_queries,
    upstream_nodes,
)


class GraphCoreTests(unittest.TestCase):
    def setUp(self):
        # C depends on B depends on A; D depends on A.
        self.dependencies = {
            "B": ["A"],
            "C": ["B"],
            "D": ["A"],
        }

    def test_upstream_nodes(self):
        self.assertEqual(upstream_nodes("C", self.dependencies), ["B", "A"])

    def test_downstream_nodes(self):
        out = downstream_nodes("A", self.dependencies)
        self.assertEqual(sorted(out), ["B", "C", "D"])

    def test_impact_analysis_aliases_downstream(self):
        self.assertEqual(sorted(impact_analysis("A", self.dependencies)), ["B", "C", "D"])

    def test_critical_path_on_dag(self):
        path = critical_path(self.dependencies, ["A", "B", "C", "D"])
        self.assertEqual(path, ["A", "B", "C"])

    def test_postgres_recursive_templates_available(self):
        queries = postgres_recursive_cte_queries()
        self.assertIn("upstream", queries)
        self.assertIn("downstream", queries)
        self.assertIn("cycle_check", queries)
        self.assertIn("WITH RECURSIVE", queries["upstream"])


if __name__ == "__main__":
    unittest.main()
