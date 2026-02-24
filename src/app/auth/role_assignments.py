from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from .rbac import ROLE_PERMISSIONS


@dataclass(frozen=True)
class RoleAssignmentRequest:
    subject_id: str
    role: str
    actor: str
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None


@dataclass(frozen=True)
class RoleAssignmentRecord:
    subject_id: str
    role: str
    tenant_id: Optional[str]
    project_id: Optional[str]
    assigned_by: str
    assigned_at: str


@dataclass(frozen=True)
class RoleAuditEntry:
    event_id: str
    event_type: str
    actor: str
    timestamp: str
    subject_id: str
    role: str
    tenant_id: Optional[str]
    project_id: Optional[str]
    old_roles: List[str]
    new_roles: List[str]


class RoleAssignmentError(ValueError):
    pass


class RoleAssignmentService:
    def __init__(self):
        self._assignments: Dict[Tuple[str, Optional[str], Optional[str]], Set[str]] = {}
        self._audit_log: List[RoleAuditEntry] = []

    def assign_role(self, request: RoleAssignmentRequest) -> RoleAssignmentRecord:
        subject = request.subject_id.strip()
        role = request.role.strip().lower()
        actor = request.actor.strip()
        tenant_id = request.tenant_id
        project_id = request.project_id

        if not subject or not actor:
            raise RoleAssignmentError("subject_id and actor are required")
        if role not in ROLE_PERMISSIONS:
            raise RoleAssignmentError("Unknown role")

        self._validate_scope(role, tenant_id, project_id)

        key = (subject, tenant_id, project_id)
        previous = sorted(self._assignments.get(key, set()))
        roles = set(self._assignments.get(key, set()))
        roles.add(role)
        self._assignments[key] = roles

        now = datetime.now(timezone.utc).isoformat()
        record = RoleAssignmentRecord(
            subject_id=subject,
            role=role,
            tenant_id=tenant_id,
            project_id=project_id,
            assigned_by=actor,
            assigned_at=now,
        )

        self._audit_log.append(
            RoleAuditEntry(
                event_id=f"role-change-{len(self._audit_log) + 1:06d}",
                event_type="role_assigned",
                actor=actor,
                timestamp=now,
                subject_id=subject,
                role=role,
                tenant_id=tenant_id,
                project_id=project_id,
                old_roles=previous,
                new_roles=sorted(roles),
            )
        )
        return record

    def list_assignments(self, subject_id: Optional[str] = None) -> List[RoleAssignmentRecord]:
        out: List[RoleAssignmentRecord] = []
        for (subject, tenant_id, project_id), roles in sorted(self._assignments.items()):
            if subject_id and subject != subject_id:
                continue
            for role in sorted(roles):
                out.append(
                    RoleAssignmentRecord(
                        subject_id=subject,
                        role=role,
                        tenant_id=tenant_id,
                        project_id=project_id,
                        assigned_by="system",
                        assigned_at="snapshot",
                    )
                )
        return out

    def list_audit_entries(self, subject_id: Optional[str] = None) -> List[RoleAuditEntry]:
        if subject_id:
            return [entry for entry in self._audit_log if entry.subject_id == subject_id]
        return list(self._audit_log)

    def assign_role_endpoint(self, payload: Dict[str, Optional[str]], actor: str) -> Tuple[int, Dict[str, object]]:
        try:
            req = RoleAssignmentRequest(
                subject_id=str(payload.get("subject_id") or ""),
                role=str(payload.get("role") or ""),
                actor=actor,
                tenant_id=payload.get("tenant_id"),
                project_id=payload.get("project_id"),
            )
            rec = self.assign_role(req)
            return 200, {
                "subject_id": rec.subject_id,
                "role": rec.role,
                "tenant_id": rec.tenant_id,
                "project_id": rec.project_id,
                "assigned_by": rec.assigned_by,
                "assigned_at": rec.assigned_at,
            }
        except RoleAssignmentError as exc:
            return 400, {"error": str(exc)}

    def role_audit_endpoint(self, subject_id: Optional[str] = None) -> Tuple[int, Dict[str, object]]:
        entries = self.list_audit_entries(subject_id)
        return 200, {
            "entries": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "actor": e.actor,
                    "timestamp": e.timestamp,
                    "subject_id": e.subject_id,
                    "role": e.role,
                    "tenant_id": e.tenant_id,
                    "project_id": e.project_id,
                    "old_roles": e.old_roles,
                    "new_roles": e.new_roles,
                }
                for e in entries
            ]
        }

    @staticmethod
    def _validate_scope(role: str, tenant_id: Optional[str], project_id: Optional[str]) -> None:
        if role == "system_admin":
            return
        if role in {"tenant_admin", "governance_officer", "viewer", "auditor", "agent", "contributor"} and not tenant_id:
            raise RoleAssignmentError(f"Role {role} requires tenant scope")
        if role == "project_admin" and not (tenant_id and project_id):
            raise RoleAssignmentError("project_admin requires tenant_id and project_id")
