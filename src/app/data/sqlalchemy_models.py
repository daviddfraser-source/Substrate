"""SQLAlchemy model definitions for PRD-required entities.

This module is import-safe when SQLAlchemy is unavailable in minimal environments.
"""

try:
    from sqlalchemy import Column, Float, ForeignKey, String, Text
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
