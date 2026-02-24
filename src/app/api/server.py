from typing import Any, Dict, Tuple

from app.auth.middleware import RequestContext, enforce_rbac
from app.auth.rbac import RoleBinding

from .contracts import CORE_ENDPOINTS
from .openapi import build_openapi_document


def route_request(path: str, method: str, bindings: Tuple[RoleBinding, ...], tenant_id: str = "", project_id: str = "") -> Dict[str, Any]:
    norm_method = method.strip().upper()
    for endpoint in CORE_ENDPOINTS:
        if endpoint.path == path and endpoint.method == norm_method:
            enforce_rbac(
                bindings,
                RequestContext(method=norm_method, resource=endpoint.permission.split(":", 1)[0], tenant_id=tenant_id or None, project_id=project_id or None),
            )
            return {"ok": True, "path": path, "method": norm_method}
    return {"ok": False, "error": "not_found"}


def write_openapi(path: str) -> None:
    import json

    with open(path, "w", encoding="utf-8") as f:
        json.dump(build_openapi_document(), f, indent=2)
        f.write("\n")
