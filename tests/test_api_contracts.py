import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.api.contracts import CORE_ENDPOINTS  # noqa: E402
from app.api.openapi import build_openapi_document  # noqa: E402
from app.api.server import route_request, write_openapi  # noqa: E402
from app.auth.rbac import RoleBinding  # noqa: E402


class ApiContractTests(unittest.TestCase):
    def test_required_endpoint_families_present(self):
        paths = {item.path for item in CORE_ENDPOINTS}
        for required in {
            "/auth/login",
            "/tenants",
            "/users",
            "/roles/assign",
            "/projects",
            "/packets",
            "/dependencies",
            "/risks",
            "/audit",
            "/agents",
            "/metrics",
            "/proposals",
            "/health",
        }:
            self.assertIn(required, paths)

    def test_openapi_document_contains_contract_paths(self):
        document = build_openapi_document()
        self.assertEqual(document["openapi"], "3.0.3")
        self.assertIn("/auth/login", document["paths"])
        self.assertIn("post", document["paths"]["/auth/login"])

    def test_route_request_enforces_rbac(self):
        result = route_request(
            "/packets",
            "GET",
            bindings=(RoleBinding(role="viewer", tenant_id="t1"),),
            tenant_id="t1",
            project_id="p1",
        )
        self.assertTrue(result["ok"])

        with self.assertRaises(PermissionError):
            route_request(
                "/packets",
                "POST",
                bindings=(RoleBinding(role="viewer", tenant_id="t1"),),
                tenant_id="t1",
                project_id="p1",
            )

    def test_openapi_is_published_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "openapi.json"
            write_openapi(str(out))
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("paths", payload)
            self.assertIn("/health", payload["paths"])


if __name__ == "__main__":
    unittest.main()
