import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional
from uuid import uuid4

from app.data.migrate import apply_sqlite_migrations

_TERM_RE = re.compile(r"[a-z0-9_]+")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokenize(text: str) -> List[str]:
    tokens = _TERM_RE.findall((text or "").lower())
    return [token for token in tokens if len(token) > 1]


class ExecutionDataStore:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path))

    def setup(self) -> None:
        apply_sqlite_migrations(self.db_path)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def create_execution_run(
        self,
        tenant_id: str,
        project_id: str,
        agent_id: str,
        prompt_version: str,
        status: str = "running",
    ) -> str:
        run_id = f"run-{uuid4()}"
        now = _now_iso()
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO execution_runs(
                  id, tenant_id, project_id, agent_id, prompt_version, status, started_at, completed_at, output_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)
                """,
                (run_id, tenant_id, project_id, agent_id, prompt_version, status, now),
            )
        return run_id

    def complete_execution_run(self, run_id: str, output_summary: str, status: str = "success") -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE execution_runs
                SET status = ?, completed_at = ?, output_summary = ?
                WHERE id = ?
                """,
                (status, _now_iso(), output_summary, run_id),
            )

    def record_token_usage(
        self,
        tenant_id: str,
        project_id: str,
        execution_id: str,
        agent_id: str,
        tokens_in: int,
        tokens_out: int,
    ) -> str:
        event_id = f"tok-{uuid4()}"
        total = int(tokens_in) + int(tokens_out)
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO token_usage_events(
                  id, tenant_id, project_id, execution_id, agent_id, tokens_in, tokens_out, total_tokens, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, tenant_id, project_id, execution_id, agent_id, int(tokens_in), int(tokens_out), total, _now_iso()),
            )
        return event_id

    def add_document(self, tenant_id: str, project_id: str, title: str, source_uri: str, content: str) -> str:
        document_id = f"doc-{uuid4()}"
        digest = sha256(content.encode("utf-8")).hexdigest()
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO knowledge_documents(
                  id, tenant_id, project_id, title, source_uri, content, content_sha256, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (document_id, tenant_id, project_id, title, source_uri, content, digest, _now_iso()),
            )
        return document_id

    def add_embedding(
        self,
        tenant_id: str,
        document_id: str,
        chunk_index: int,
        embedding_model: str,
        embedding: Iterable[float],
        token_count: int,
    ) -> str:
        embedding_id = f"emb-{uuid4()}"
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO document_embeddings(
                  id, tenant_id, document_id, chunk_index, embedding_model, embedding_json, token_count, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    embedding_id,
                    tenant_id,
                    document_id,
                    int(chunk_index),
                    embedding_model,
                    json.dumps(list(embedding)),
                    int(token_count),
                    _now_iso(),
                ),
            )
        return embedding_id

    def index_document_chunk(
        self,
        tenant_id: str,
        project_id: str,
        document_id: str,
        chunk_index: int,
        text: str,
    ) -> int:
        terms = sorted(set(_tokenize(text)))
        now = _now_iso()
        with self.connection() as conn:
            for term in terms:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO search_term_index(
                      id, tenant_id, project_id, term, document_id, chunk_index, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"idx-{uuid4()}", tenant_id, project_id, term, document_id, int(chunk_index), now),
                )
        return len(terms)

    def search_documents(self, tenant_id: str, project_id: str, query: str, limit: int = 10) -> List[Dict[str, object]]:
        terms = sorted(set(_tokenize(query)))
        if not terms:
            return []
        placeholders = ",".join("?" for _ in terms)
        params = [tenant_id, project_id, *terms, int(limit)]
        with self.connection() as conn:
            rows = conn.execute(
                f"""
                SELECT
                  s.document_id,
                  COUNT(*) AS score,
                  GROUP_CONCAT(DISTINCT s.term) AS matched_terms,
                  MIN(d.title) AS title
                FROM search_term_index s
                JOIN knowledge_documents d
                  ON d.id = s.document_id
                 AND d.tenant_id = s.tenant_id
                WHERE s.tenant_id = ?
                  AND s.project_id = ?
                  AND s.term IN ({placeholders})
                GROUP BY s.document_id
                ORDER BY score DESC, s.document_id ASC
                LIMIT ?
                """,
                params,
            ).fetchall()

        out: List[Dict[str, object]] = []
        for row in rows:
            matched = sorted([t for t in str(row["matched_terms"] or "").split(",") if t])
            out.append(
                {
                    "document_id": str(row["document_id"]),
                    "title": str(row["title"]),
                    "score": int(row["score"]),
                    "matched_terms": matched,
                }
            )
        return out

    def enqueue_job(
        self,
        tenant_id: str,
        project_id: str,
        job_type: str,
        payload: Dict[str, object],
        queue_name: str = "default",
        run_after: Optional[str] = None,
    ) -> str:
        job_id = f"job-{uuid4()}"
        now = _now_iso()
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO async_jobs(
                  id, tenant_id, project_id, queue_name, job_type, payload_json, status, attempt_count,
                  run_after, claimed_by, claimed_at, last_error, result_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'queued', 0, ?, NULL, NULL, NULL, NULL, ?, ?)
                """,
                (job_id, tenant_id, project_id, queue_name, job_type, json.dumps(payload), run_after, now, now),
            )
        return job_id

    def claim_next_job(self, worker_id: str, queue_name: str = "default") -> Optional[Dict[str, object]]:
        now = _now_iso()
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT id, tenant_id, project_id, queue_name, job_type, payload_json, attempt_count
                FROM async_jobs
                WHERE status = 'queued'
                  AND queue_name = ?
                  AND (run_after IS NULL OR run_after <= ?)
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (queue_name, now),
            ).fetchone()
            if row is None:
                return None

            conn.execute(
                """
                UPDATE async_jobs
                SET status = 'running',
                    attempt_count = attempt_count + 1,
                    claimed_by = ?,
                    claimed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (worker_id, now, now, str(row["id"])),
            )
            return {
                "id": str(row["id"]),
                "tenant_id": str(row["tenant_id"]),
                "project_id": str(row["project_id"]),
                "queue_name": str(row["queue_name"]),
                "job_type": str(row["job_type"]),
                "payload": json.loads(str(row["payload_json"])),
                "attempt_count": int(row["attempt_count"]) + 1,
            }

    def complete_job(self, job_id: str, result: Dict[str, object]) -> None:
        now = _now_iso()
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE async_jobs
                SET status = 'done', result_json = ?, last_error = NULL, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(result), now, job_id),
            )

    def fail_job(self, job_id: str, error: str) -> None:
        now = _now_iso()
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE async_jobs
                SET status = 'failed', last_error = ?, updated_at = ?
                WHERE id = ?
                """,
                (error, now, job_id),
            )

    def list_jobs(self, status: Optional[str] = None) -> List[Dict[str, object]]:
        with self.connection() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT id, job_type, status, attempt_count, last_error, result_json
                    FROM async_jobs
                    WHERE status = ?
                    ORDER BY created_at ASC
                    """,
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, job_type, status, attempt_count, last_error, result_json
                    FROM async_jobs
                    ORDER BY created_at ASC
                    """
                ).fetchall()

        out: List[Dict[str, object]] = []
        for row in rows:
            out.append(
                {
                    "id": str(row["id"]),
                    "job_type": str(row["job_type"]),
                    "status": str(row["status"]),
                    "attempt_count": int(row["attempt_count"]),
                    "last_error": row["last_error"],
                    "result": json.loads(str(row["result_json"])) if row["result_json"] else None,
                }
            )
        return out


JobHandler = Callable[[Dict[str, object], Dict[str, object]], Dict[str, object]]


class AsyncJobWorker:
    def __init__(self, store: ExecutionDataStore):
        self.store = store
        self.handlers: Dict[str, JobHandler] = {}

    def register(self, job_type: str, handler: JobHandler) -> None:
        self.handlers[job_type] = handler

    def process_next(self, worker_id: str, queue_name: str = "default") -> Optional[str]:
        job = self.store.claim_next_job(worker_id=worker_id, queue_name=queue_name)
        if job is None:
            return None

        job_type = str(job["job_type"])
        handler = self.handlers.get(job_type)
        if handler is None:
            self.store.fail_job(str(job["id"]), f"No handler registered for {job_type}")
            return str(job["id"])

        try:
            result = handler(dict(job["payload"]), job)
            self.store.complete_job(str(job["id"]), result)
        except Exception as exc:  # pragma: no cover
            self.store.fail_job(str(job["id"]), str(exc))
        return str(job["id"])
