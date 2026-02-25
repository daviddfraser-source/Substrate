CREATE UNIQUE INDEX IF NOT EXISTS uq_users_tenant_id_id ON users(tenant_id, id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_tenant_email ON users(tenant_id, email);
CREATE UNIQUE INDEX IF NOT EXISTS uq_projects_tenant_id_id ON projects(tenant_id, id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_projects_tenant_name ON projects(tenant_id, name);

CREATE TABLE IF NOT EXISTS project_memberships (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (role_id) REFERENCES roles(id),
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  FOREIGN KEY (tenant_id, user_id) REFERENCES users(tenant_id, id),
  UNIQUE (tenant_id, project_id, user_id, role_id)
);

CREATE TABLE IF NOT EXISTS governance_entities (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  external_ref TEXT,
  payload TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  UNIQUE (tenant_id, id),
  UNIQUE (tenant_id, project_id, entity_type, external_ref)
);

CREATE TABLE IF NOT EXISTS governance_relationships (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  from_entity_id TEXT NOT NULL,
  to_entity_id TEXT NOT NULL,
  relationship_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id),
  FOREIGN KEY (tenant_id, from_entity_id) REFERENCES governance_entities(tenant_id, id),
  FOREIGN KEY (tenant_id, to_entity_id) REFERENCES governance_entities(tenant_id, id),
  CHECK (from_entity_id <> to_entity_id),
  UNIQUE (tenant_id, project_id, from_entity_id, to_entity_id, relationship_type)
);
