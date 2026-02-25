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
            "ProjectMembership",
            "GovernanceEntity",
            "GovernanceRelationship",
            "ExecutionRun",
            "TokenUsageEvent",
            "KnowledgeDocument",
            "DocumentEmbedding",
            "SearchTermIndex",
            "AsyncJob",
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
            "project_memberships",
            "governance_entities",
            "governance_relationships",
            "execution_runs",
            "token_usage_events",
            "knowledge_documents",
            "document_embeddings",
            "search_term_index",
            "async_jobs",
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

    def test_multiuser_isolation_constraints_reject_cross_tenant_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "test.db")
            apply_sqlite_migrations(db_path)
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                conn.executescript(
                    """
                    INSERT INTO tenants(id, name, created_at) VALUES
                      ('t1', 'Tenant One', '2026-01-01T00:00:00Z'),
                      ('t2', 'Tenant Two', '2026-01-01T00:00:00Z');
                    INSERT INTO users(id, tenant_id, email, display_name, created_at) VALUES
                      ('u1', 't1', 'u1@t1.example', 'U1', '2026-01-01T00:00:00Z'),
                      ('u2', 't2', 'u2@t2.example', 'U2', '2026-01-01T00:00:00Z');
                    INSERT INTO roles(id, name, scope, created_at) VALUES
                      ('r1', 'contributor', 'project', '2026-01-01T00:00:00Z');
                    INSERT INTO projects(id, tenant_id, name, created_at) VALUES
                      ('p1', 't1', 'Project One', '2026-01-01T00:00:00Z'),
                      ('p2', 't2', 'Project Two', '2026-01-01T00:00:00Z');
                    """
                )
                conn.execute(
                    """
                    INSERT INTO project_memberships(id, tenant_id, project_id, user_id, role_id, status, created_at)
                    VALUES ('m1', 't1', 'p1', 'u1', 'r1', 'active', '2026-01-01T00:00:00Z')
                    """
                )

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO project_memberships(id, tenant_id, project_id, user_id, role_id, status, created_at)
                        VALUES ('m2', 't1', 'p2', 'u1', 'r1', 'active', '2026-01-01T00:00:00Z')
                        """
                    )

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO project_memberships(id, tenant_id, project_id, user_id, role_id, status, created_at)
                        VALUES ('m3', 't1', 'p1', 'u2', 'r1', 'active', '2026-01-01T00:00:00Z')
                        """
                    )

                conn.execute(
                    """
                    INSERT INTO governance_entities(id, tenant_id, project_id, entity_type, external_ref, payload, created_at)
                    VALUES ('e1', 't1', 'p1', 'packet', 'pkt-1', '{}', '2026-01-01T00:00:00Z')
                    """
                )
                conn.execute(
                    """
                    INSERT INTO governance_entities(id, tenant_id, project_id, entity_type, external_ref, payload, created_at)
                    VALUES ('e2', 't2', 'p2', 'packet', 'pkt-2', '{}', '2026-01-01T00:00:00Z')
                    """
                )

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO governance_relationships(
                          id, tenant_id, project_id, from_entity_id, to_entity_id, relationship_type, created_at
                        ) VALUES ('rel-1', 't1', 'p1', 'e1', 'e2', 'depends_on', '2026-01-01T00:00:00Z')
                        """
                    )
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
