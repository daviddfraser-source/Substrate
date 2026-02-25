from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EndpointContract:
    path: str
    method: str
    permission: str
    summary: str


CORE_ENDPOINTS: List[EndpointContract] = [
    EndpointContract("/auth/login", "POST", "auth:write", "Login endpoint"),
    EndpointContract("/auth/logout", "POST", "auth:write", "Logout endpoint"),
    EndpointContract("/auth/session", "GET", "auth:read", "Session status"),
    EndpointContract("/tenants", "GET", "tenant:read", "List tenants"),
    EndpointContract("/tenants", "POST", "tenant:write", "Create tenant"),
    EndpointContract("/users", "GET", "user:read", "List users"),
    EndpointContract("/users", "POST", "user:write", "Create user"),
    EndpointContract("/roles", "GET", "role:read", "List roles"),
    EndpointContract("/roles/assign", "POST", "role:write", "Assign role"),
    EndpointContract("/projects", "GET", "project:read", "List projects"),
    EndpointContract("/projects", "POST", "project:write", "Create project"),
    EndpointContract("/packets", "GET", "packet:read", "List packets"),
    EndpointContract("/packets", "POST", "packet:write", "Create packet"),
    EndpointContract("/dependencies", "GET", "dependency:read", "List dependencies"),
    EndpointContract("/dependencies", "POST", "dependency:write", "Create dependency"),
    EndpointContract("/risks", "GET", "risk:read", "List risks"),
    EndpointContract("/risks", "POST", "risk:write", "Create risk"),
    EndpointContract("/audit", "GET", "audit:read", "Query audit entries"),
    EndpointContract("/agents", "GET", "agent:read", "List agents"),
    EndpointContract("/agents", "POST", "agent:write", "Register agent"),
    EndpointContract("/metrics", "GET", "metrics:read", "Read metrics"),
    EndpointContract("/metrics", "POST", "metrics:write", "Write metrics"),
    EndpointContract("/analytics/summary", "GET", "metrics:read", "Read aggregated analytics"),
    EndpointContract("/analytics/token-usage", "GET", "metrics:read", "Read token usage analytics"),
    EndpointContract("/analytics/export", "GET", "metrics:read", "Export analytics payload"),
    EndpointContract("/proposals", "GET", "proposal:read", "List proposals"),
    EndpointContract("/proposals", "POST", "proposal:write", "Create proposal"),
    EndpointContract("/health", "GET", "health:read", "Health check"),
    EndpointContract("/readyz", "GET", "health:read", "Readiness check"),
    EndpointContract("/livez", "GET", "health:read", "Liveness check"),
    EndpointContract("/traces", "GET", "metrics:read", "Trace events"),
]
