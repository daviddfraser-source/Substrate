import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.data.entities import CORE_ENTITY_NAMES  # noqa: E402
from app.data.migrate import apply_sqlite_migrations, migration_files, migration_sql_has_postgres_compatible_types  # noqa: E402


class DataMigrationTests(unittest.TestCase):
    def test_entity_registry_covers_required_prd_entities(self):
        expected = {
            "Tenant",
            "User",
            "Role",
            "Project",
            "Packet",
            "Dependency",
            "Risk",
            "AuditEntry",
            "AgentIdentity",
            "APIKey",
            "MetricEvent",
            "OptimizationProposal",
            "RuleVersion",
            "PerformanceSnapshot",
            "ImprovementImpactReport",
        }
        self.assertEqual(set(CORE_ENTITY_NAMES), expected)

    def test_sql_migrations_apply_to_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "test.db")
            apply_sqlite_migrations(db_path)
            conn = sqlite3.connect(db_path)
            try:
                tables = {
                    row[0]
                    for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                }
            finally:
                conn.close()

        required_tables = {
            "tenants",
            "users",
            "roles",
            "projects",
            "packets",
            "dependencies",
            "risks",
            "audit_entries",
            "agent_identities",
            "api_keys",
            "metric_events",
            "optimization_proposals",
            "rule_versions",
            "performance_snapshots",
            "improvement_impact_reports",
        }
        self.assertTrue(required_tables.issubset(tables))

    def test_migration_sql_is_postgres_portable_enough(self):
        for path in migration_files():
            self.assertTrue(migration_sql_has_postgres_compatible_types(path.read_text().splitlines()))


if __name__ == "__main__":
    unittest.main()
