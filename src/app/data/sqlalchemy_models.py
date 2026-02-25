"""SQLAlchemy model definitions for PRD-required entities.

This module is import-safe when SQLAlchemy is unavailable in minimal environments.
"""

try:
    from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()

    class Tenant(Base):
        __tablename__ = "tenants"
        id = Column(String, primary_key=True)
        name = Column(String, nullable=False)
        created_at = Column(String, nullable=False)

    class User(Base):
        __tablename__ = "users"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
        email = Column(String, nullable=False)
        display_name = Column(String)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id_id"),
            UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        )

    class Role(Base):
        __tablename__ = "roles"
        id = Column(String, primary_key=True)
        name = Column(String, nullable=False)
        scope = Column(String, nullable=False)
        created_at = Column(String, nullable=False)

    class Project(Base):
        __tablename__ = "projects"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "id", name="uq_projects_tenant_id_id"),
            UniqueConstraint("tenant_id", "name", name="uq_projects_tenant_name"),
        )

    class ProjectMembership(Base):
        __tablename__ = "project_memberships"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
        project_id = Column(String, nullable=False)
        user_id = Column(String, nullable=False)
        role_id = Column(String, ForeignKey("roles.id"), nullable=False)
        status = Column(String, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "project_id", "user_id", "role_id", name="uq_membership_role"),
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
            ForeignKeyConstraint(["tenant_id", "user_id"], ["users.tenant_id", "users.id"]),
        )

    class GovernanceEntity(Base):
        __tablename__ = "governance_entities"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
        project_id = Column(String, nullable=False)
        entity_type = Column(String, nullable=False)
        external_ref = Column(String)
        payload = Column(Text)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "id", name="uq_governance_entities_tenant_id_id"),
            UniqueConstraint("tenant_id", "project_id", "entity_type", "external_ref", name="uq_governance_entity_ref"),
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
        )

    class GovernanceRelationship(Base):
        __tablename__ = "governance_relationships"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
        project_id = Column(String, nullable=False)
        from_entity_id = Column(String, nullable=False)
        to_entity_id = Column(String, nullable=False)
        relationship_type = Column(String, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint(
                "tenant_id",
                "project_id",
                "from_entity_id",
                "to_entity_id",
                "relationship_type",
                name="uq_governance_relationship",
            ),
            CheckConstraint("from_entity_id <> to_entity_id", name="ck_governance_relationship_no_self_ref"),
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
            ForeignKeyConstraint(["tenant_id", "from_entity_id"], ["governance_entities.tenant_id", "governance_entities.id"]),
            ForeignKeyConstraint(["tenant_id", "to_entity_id"], ["governance_entities.tenant_id", "governance_entities.id"]),
        )

    class ExecutionRun(Base):
        __tablename__ = "execution_runs"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
        project_id = Column(String, nullable=False)
        agent_id = Column(String, nullable=False)
        prompt_version = Column(String)
        status = Column(String, nullable=False)
        started_at = Column(String, nullable=False)
        completed_at = Column(String)
        output_summary = Column(Text)
        __table_args__ = (
            UniqueConstraint("tenant_id", "id", name="uq_execution_runs_tenant_id_id"),
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
        )

    class TokenUsageEvent(Base):
        __tablename__ = "token_usage_events"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, nullable=False)
        project_id = Column(String, nullable=False)
        execution_id = Column(String, nullable=False)
        agent_id = Column(String, nullable=False)
        tokens_in = Column(Integer, nullable=False)
        tokens_out = Column(Integer, nullable=False)
        total_tokens = Column(Integer, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
            ForeignKeyConstraint(["tenant_id", "execution_id"], ["execution_runs.tenant_id", "execution_runs.id"]),
        )

    class KnowledgeDocument(Base):
        __tablename__ = "knowledge_documents"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, nullable=False)
        project_id = Column(String, nullable=False)
        title = Column(String, nullable=False)
        source_uri = Column(String)
        content = Column(Text, nullable=False)
        content_sha256 = Column(String, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "id", name="uq_knowledge_documents_tenant_id_id"),
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
        )

    class DocumentEmbedding(Base):
        __tablename__ = "document_embeddings"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, nullable=False)
        document_id = Column(String, nullable=False)
        chunk_index = Column(Integer, nullable=False)
        embedding_model = Column(String, nullable=False)
        embedding_json = Column(Text, nullable=False)
        token_count = Column(Integer, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "document_id", "chunk_index", "embedding_model", name="uq_document_embedding"),
            ForeignKeyConstraint(["tenant_id", "document_id"], ["knowledge_documents.tenant_id", "knowledge_documents.id"]),
        )

    class SearchTermIndex(Base):
        __tablename__ = "search_term_index"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, nullable=False)
        project_id = Column(String, nullable=False)
        term = Column(String, nullable=False)
        document_id = Column(String, nullable=False)
        chunk_index = Column(Integer, nullable=False)
        created_at = Column(String, nullable=False)
        __table_args__ = (
            UniqueConstraint("tenant_id", "project_id", "term", "document_id", "chunk_index", name="uq_search_term_index"),
            ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),
            ForeignKeyConstraint(["tenant_id", "document_id"], ["knowledge_documents.tenant_id", "knowledge_documents.id"]),
        )

    class AsyncJob(Base):
        __tablename__ = "async_jobs"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, nullable=False)
        project_id = Column(String, nullable=False)
        queue_name = Column(String, nullable=False)
        job_type = Column(String, nullable=False)
        payload_json = Column(Text, nullable=False)
        status = Column(String, nullable=False)
        attempt_count = Column(Integer, nullable=False)
        run_after = Column(String)
        claimed_by = Column(String)
        claimed_at = Column(String)
        last_error = Column(Text)
        result_json = Column(Text)
        created_at = Column(String, nullable=False)
        updated_at = Column(String, nullable=False)
        __table_args__ = (ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.id"]),)

    class Packet(Base):
        __tablename__ = "packets"
        id = Column(String, primary_key=True)
        project_id = Column(String, ForeignKey("projects.id"), nullable=False)
        title = Column(String, nullable=False)
        status = Column(String, nullable=False)
        owner = Column(String)
        created_at = Column(String, nullable=False)

    class Dependency(Base):
        __tablename__ = "dependencies"
        id = Column(String, primary_key=True)
        project_id = Column(String, ForeignKey("projects.id"), nullable=False)
        from_packet_id = Column(String, ForeignKey("packets.id"), nullable=False)
        to_packet_id = Column(String, ForeignKey("packets.id"), nullable=False)

    class Risk(Base):
        __tablename__ = "risks"
        id = Column(String, primary_key=True)
        packet_id = Column(String, ForeignKey("packets.id"), nullable=False)
        severity = Column(String, nullable=False)
        status = Column(String, nullable=False)
        created_at = Column(String, nullable=False)

    class AuditEntry(Base):
        __tablename__ = "audit_entries"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"))
        actor = Column(String, nullable=False)
        event_type = Column(String, nullable=False)
        created_at = Column(String, nullable=False)

    class AgentIdentity(Base):
        __tablename__ = "agent_identities"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"))
        agent_name = Column(String, nullable=False)
        mode = Column(String, nullable=False)
        created_at = Column(String, nullable=False)

    class APIKey(Base):
        __tablename__ = "api_keys"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"))
        agent_id = Column(String, ForeignKey("agent_identities.id"))
        key_hash = Column(String, nullable=False)
        created_at = Column(String, nullable=False)
        expires_at = Column(String)

    class MetricEvent(Base):
        __tablename__ = "metric_events"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"))
        metric_name = Column(String, nullable=False)
        metric_value = Column(Float, nullable=False)
        recorded_at = Column(String, nullable=False)

    class OptimizationProposal(Base):
        __tablename__ = "optimization_proposals"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"))
        status = Column(String, nullable=False)
        summary = Column(Text, nullable=False)
        created_at = Column(String, nullable=False)

    class RuleVersion(Base):
        __tablename__ = "rule_versions"
        id = Column(String, primary_key=True)
        rule_name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        approved_by = Column(String)
        created_at = Column(String, nullable=False)

    class PerformanceSnapshot(Base):
        __tablename__ = "performance_snapshots"
        id = Column(String, primary_key=True)
        tenant_id = Column(String, ForeignKey("tenants.id"))
        snapshot_name = Column(String, nullable=False)
        captured_at = Column(String, nullable=False)

    class ImprovementImpactReport(Base):
        __tablename__ = "improvement_impact_reports"
        id = Column(String, primary_key=True)
        proposal_id = Column(String, ForeignKey("optimization_proposals.id"))
        impact_summary = Column(Text, nullable=False)
        created_at = Column(String, nullable=False)

except Exception:  # pragma: no cover
    Base = object
