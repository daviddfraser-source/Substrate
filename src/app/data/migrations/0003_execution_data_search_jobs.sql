CREATE TABLE IF NOT EXISTS execution_runs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  prompt_version TEXT,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  output_summary TEXT,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  UNIQUE (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS token_usage_events (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  execution_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  tokens_in INTEGER NOT NULL,
  tokens_out INTEGER NOT NULL,
  total_tokens INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  FOREIGN KEY (tenant_id, execution_id) REFERENCES execution_runs(tenant_id, id)
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  title TEXT NOT NULL,
  source_uri TEXT,
  content TEXT NOT NULL,
  content_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  UNIQUE (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS document_embeddings (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  document_id TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  embedding_model TEXT NOT NULL,
  embedding_json TEXT NOT NULL,
  token_count INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id, document_id) REFERENCES knowledge_documents(tenant_id, id),
  UNIQUE (tenant_id, document_id, chunk_index, embedding_model)
);

CREATE TABLE IF NOT EXISTS search_term_index (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  term TEXT NOT NULL,
  document_id TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  FOREIGN KEY (tenant_id, document_id) REFERENCES knowledge_documents(tenant_id, id),
  UNIQUE (tenant_id, project_id, term, document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS async_jobs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  queue_name TEXT NOT NULL,
  job_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL,
  attempt_count INTEGER NOT NULL,
  run_after TEXT,
  claimed_by TEXT,
  claimed_at TEXT,
  last_error TEXT,
  result_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id)
);

CREATE INDEX IF NOT EXISTS idx_execution_runs_scope_status
  ON execution_runs(tenant_id, project_id, status, started_at);

CREATE INDEX IF NOT EXISTS idx_token_usage_execution
  ON token_usage_events(tenant_id, execution_id, created_at);

CREATE INDEX IF NOT EXISTS idx_search_term_lookup
  ON search_term_index(tenant_id, project_id, term);

CREATE INDEX IF NOT EXISTS idx_async_jobs_claim
  ON async_jobs(status, queue_name, run_after, created_at);
