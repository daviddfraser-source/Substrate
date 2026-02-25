from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EntityDefinition:
    name: str
    fields: List[str]


ENTITY_REGISTRY: Dict[str, EntityDefinition] = {
    "Tenant": EntityDefinition("Tenant", ["id", "name", "created_at"]),
    "User": EntityDefinition("User", ["id", "tenant_id", "email", "display_name", "created_at"]),
    "Role": EntityDefinition("Role", ["id", "name", "scope", "created_at"]),
    "Project": EntityDefinition("Project", ["id", "tenant_id", "name", "created_at"]),
    "ProjectMembership": EntityDefinition(
        "ProjectMembership",
        ["id", "tenant_id", "project_id", "user_id", "role_id", "status", "created_at"],
    ),
    "GovernanceEntity": EntityDefinition(
        "GovernanceEntity",
        ["id", "tenant_id", "project_id", "entity_type", "external_ref", "payload", "created_at"],
    ),
    "GovernanceRelationship": EntityDefinition(
        "GovernanceRelationship",
        ["id", "tenant_id", "project_id", "from_entity_id", "to_entity_id", "relationship_type", "created_at"],
    ),
    "ExecutionRun": EntityDefinition(
        "ExecutionRun",
        ["id", "tenant_id", "project_id", "agent_id", "prompt_version", "status", "started_at", "completed_at"],
    ),
    "TokenUsageEvent": EntityDefinition(
        "TokenUsageEvent",
        ["id", "tenant_id", "project_id", "execution_id", "agent_id", "tokens_in", "tokens_out", "total_tokens", "created_at"],
    ),
    "KnowledgeDocument": EntityDefinition(
        "KnowledgeDocument",
        ["id", "tenant_id", "project_id", "title", "source_uri", "content", "content_sha256", "created_at"],
    ),
    "DocumentEmbedding": EntityDefinition(
        "DocumentEmbedding",
        ["id", "tenant_id", "document_id", "chunk_index", "embedding_model", "embedding_json", "token_count", "created_at"],
    ),
    "SearchTermIndex": EntityDefinition(
        "SearchTermIndex",
        ["id", "tenant_id", "project_id", "term", "document_id", "chunk_index", "created_at"],
    ),
    "AsyncJob": EntityDefinition(
        "AsyncJob",
        ["id", "tenant_id", "project_id", "queue_name", "job_type", "payload_json", "status", "run_after", "created_at"],
    ),
    "Packet": EntityDefinition("Packet", ["id", "project_id", "title", "status", "owner", "created_at"]),
    "Dependency": EntityDefinition("Dependency", ["id", "project_id", "from_packet_id", "to_packet_id"]),
    "Risk": EntityDefinition("Risk", ["id", "packet_id", "severity", "status", "created_at"]),
    "AuditEntry": EntityDefinition("AuditEntry", ["id", "tenant_id", "actor", "event_type", "created_at"]),
    "AgentIdentity": EntityDefinition("AgentIdentity", ["id", "tenant_id", "agent_name", "mode", "created_at"]),
    "APIKey": EntityDefinition("APIKey", ["id", "tenant_id", "agent_id", "key_hash", "created_at", "expires_at"]),
    "MetricEvent": EntityDefinition("MetricEvent", ["id", "tenant_id", "metric_name", "metric_value", "recorded_at"]),
    "OptimizationProposal": EntityDefinition("OptimizationProposal", ["id", "tenant_id", "status", "summary", "created_at"]),
    "RuleVersion": EntityDefinition("RuleVersion", ["id", "rule_name", "version", "approved_by", "created_at"]),
    "PerformanceSnapshot": EntityDefinition("PerformanceSnapshot", ["id", "tenant_id", "snapshot_name", "captured_at"]),
    "ImprovementImpactReport": EntityDefinition("ImprovementImpactReport", ["id", "proposal_id", "impact_summary", "created_at"]),
}

CORE_ENTITY_NAMES = sorted(ENTITY_REGISTRY.keys())
