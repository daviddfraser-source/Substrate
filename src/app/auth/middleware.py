from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from .rbac import RoleBinding, require_permission, route_permission


@dataclass(frozen=True)
class RequestContext:
    method: str
    resource: str
    tenant_id: Optional[str]
    project_id: Optional[str]


def enforce_rbac(bindings: Iterable[RoleBinding], context: RequestContext) -> Dict[str, str]:
    permission = route_permission(context.method, context.resource)
    require_permission(list(bindings), permission, context.tenant_id, context.project_id)
    return {"authorized": "true", "permission": permission}
