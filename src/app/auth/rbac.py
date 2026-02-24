from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set


ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "system_admin": {"*"},
    "tenant_admin": {
        "tenant:read",
        "tenant:write",
        "user:read",
        "user:write",
        "project:read",
        "project:write",
        "packet:read",
        "packet:write",
        "risk:read",
        "risk:write",
        "audit:read",
    },
    "project_admin": {
        "project:read",
        "project:write",
        "packet:read",
        "packet:write",
        "risk:read",
        "risk:write",
        "audit:read",
    },
    "governance_officer": {"packet:read", "packet:write", "risk:read", "risk:write", "audit:read", "proposal:review"},
    "contributor": {"packet:read", "packet:write", "risk:read", "risk:write"},
    "viewer": {"packet:read", "risk:read", "audit:read"},
    "auditor": {"audit:read", "packet:read", "risk:read"},
    "agent": {"packet:read", "packet:write", "risk:read"},
}


@dataclass(frozen=True)
class RoleBinding:
    role: str
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None


class AuthorizationError(PermissionError):
    pass


def is_allowed(bindings: Iterable[RoleBinding], permission: str, tenant_id: Optional[str], project_id: Optional[str]) -> bool:
    token = permission.strip().lower()
    for binding in bindings:
        role = binding.role.strip().lower()
        role_permissions = ROLE_PERMISSIONS.get(role, set())
        if "*" not in role_permissions and token not in role_permissions:
            continue

        if role == "system_admin":
            return True

        # Tenant-scoped roles must match tenant.
        if binding.tenant_id and tenant_id and binding.tenant_id != tenant_id:
            continue

        # Project-scoped roles must match project.
        if binding.project_id and project_id and binding.project_id != project_id:
            continue

        if binding.project_id and not project_id:
            continue
        if binding.tenant_id and not tenant_id and role != "project_admin":
            continue

        return True
    return False


def require_permission(bindings: List[RoleBinding], permission: str, tenant_id: Optional[str], project_id: Optional[str]) -> None:
    if not is_allowed(bindings, permission, tenant_id, project_id):
        raise AuthorizationError(f"Permission denied: {permission}")


def route_permission(method: str, resource: str) -> str:
    verb = method.strip().upper()
    name = resource.strip().lower()
    action = "read" if verb in {"GET", "HEAD"} else "write"
    return f"{name}:{action}"
