import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.auth.middleware import RequestContext, enforce_rbac  # noqa: E402
from app.auth.rbac import AuthorizationError, RoleBinding, route_permission  # noqa: E402


class RbacTests(unittest.TestCase):
    def test_route_permission_mapping(self):
        self.assertEqual(route_permission("GET", "packet"), "packet:read")
        self.assertEqual(route_permission("POST", "packet"), "packet:write")

    def test_project_scope_enforced(self):
        bindings = [RoleBinding(role="project_admin", tenant_id="t1", project_id="p1")]
        context = RequestContext(method="POST", resource="packet", tenant_id="t1", project_id="p1")
        result = enforce_rbac(bindings, context)
        self.assertEqual(result["authorized"], "true")

        bad_context = RequestContext(method="POST", resource="packet", tenant_id="t1", project_id="p2")
        with self.assertRaises(AuthorizationError):
            enforce_rbac(bindings, bad_context)

    def test_unauthorized_is_denied(self):
        bindings = [RoleBinding(role="viewer", tenant_id="t1")]
        context = RequestContext(method="POST", resource="packet", tenant_id="t1", project_id="p1")
        with self.assertRaises(AuthorizationError):
            enforce_rbac(bindings, context)

    def test_system_admin_overrides_scope(self):
        bindings = [RoleBinding(role="system_admin")]
        context = RequestContext(method="DELETE", resource="project", tenant_id="any", project_id="any")
        result = enforce_rbac(bindings, context)
        self.assertEqual(result["authorized"], "true")


if __name__ == "__main__":
    unittest.main()
