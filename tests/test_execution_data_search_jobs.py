import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.execution_store import AsyncJobWorker, ExecutionDataStore  # noqa: E402


class ExecutionDataSearchJobsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "integration.db")
        self.store = ExecutionDataStore(self.db_path)
        self.store.setup()

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(
                """
                INSERT INTO tenants(id, name, created_at)
                VALUES ('t1', 'Tenant One', '2026-01-01T00:00:00Z');

                INSERT INTO users(id, tenant_id, email, display_name, created_at)
                VALUES ('u1', 't1', 'user@t1.example', 'User One', '2026-01-01T00:00:00Z');

                INSERT INTO roles(id, name, scope, created_at)
                VALUES ('role1', 'contributor', 'project', '2026-01-01T00:00:00Z');

                INSERT INTO projects(id, tenant_id, name, created_at)
                VALUES ('p1', 't1', 'Project One', '2026-01-01T00:00:00Z');
                """
            )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_execution_token_document_search_and_worker_flow(self):
        run_id = self.store.create_execution_run(
            tenant_id="t1",
            project_id="p1",
            agent_id="agent-1",
            prompt_version="v1",
        )
        self.store.record_token_usage(
            tenant_id="t1",
            project_id="p1",
            execution_id=run_id,
            agent_id="agent-1",
            tokens_in=120,
            tokens_out=30,
        )
        self.store.complete_execution_run(run_id, output_summary="completed")

        doc1 = self.store.add_document(
            tenant_id="t1",
            project_id="p1",
            title="Runbook",
            source_uri="memory://runbook",
            content="governance packet workflow with execution tracing",
        )
        doc2 = self.store.add_document(
            tenant_id="t1",
            project_id="p1",
            title="API Notes",
            source_uri="memory://api",
            content="budget and token controls for governed runtime",
        )

        self.store.add_embedding("t1", doc1, 0, "deterministic-v1", [0.1, 0.2, 0.3], 12)
        self.store.add_embedding("t1", doc2, 0, "deterministic-v1", [0.4, 0.5, 0.6], 10)
        self.store.index_document_chunk("t1", "p1", doc1, 0, "governance packet workflow tracing")
        self.store.index_document_chunk("t1", "p1", doc2, 0, "token budget runtime controls")

        hits = self.store.search_documents("t1", "p1", "governance token workflow", limit=5)
        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0]["document_id"], doc1)
        self.assertGreaterEqual(hits[0]["score"], hits[1]["score"])

        worker = AsyncJobWorker(self.store)
        worker.register(
            "index_refresh",
            lambda payload, job: {
                "indexed_document": payload["document_id"],
                "job_id": job["id"],
            },
        )

        job_id = self.store.enqueue_job(
            tenant_id="t1",
            project_id="p1",
            job_type="index_refresh",
            payload={"document_id": doc1},
        )
        processed_id = worker.process_next(worker_id="worker-1")
        self.assertEqual(processed_id, job_id)

        jobs = self.store.list_jobs(status="done")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], job_id)
        self.assertEqual(jobs[0]["result"]["indexed_document"], doc1)

        conn = sqlite3.connect(self.db_path)
        try:
            token_total = conn.execute(
                "SELECT total_tokens FROM token_usage_events WHERE execution_id = ?",
                (run_id,),
            ).fetchone()[0]
            self.assertEqual(token_total, 150)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
