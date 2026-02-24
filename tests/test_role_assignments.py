import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.auth.role_assignments import (  # noqa: E402
    RoleAssignmentError,
    RoleAssignmentRequest,
    RoleAssignmentService,
)


class RoleAssignmentTests(unittest.TestCase):
    def test_assign_role_records_audit_metadata(self):
        service = RoleAssignmentService()
        req = RoleAssignmentRequest(
            subject_id="user-1",
            role="tenant_admin",
            actor="admin-1",
            tenant_id="tenant-a",
        )
        rec = service.assign_role(req)
        self.assertEqual(rec.role, "tenant_admin")

        audit = service.list_audit_entries("user-1")
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0].actor, "admin-1")
        self.assertTrue(audit[0].timestamp)
        self.assertEqual(audit[0].event_type, "role_assigned")

    def test_scope_constraints_enforced(self):
        service = RoleAssignmentService()
        with self.assertRaises(RoleAssignmentError):
            service.assign_role(
                RoleAssignmentRequest(
                    subject_id="user-1",
                    role="project_admin",
                    actor="admin-1",
                    tenant_id="tenant-a",
                )
            )

    def test_role_accumulation_tracks_before_after(self):
        service = RoleAssignmentService()
        service.assign_role(
            RoleAssignmentRequest(
                subject_id="user-1",
                role="viewer",
                actor="admin-1",
                tenant_id="tenant-a",
            )
        )
        service.assign_role(
            RoleAssignmentRequest(
                subject_id="user-1",
                role="contributor",
                actor="admin-2",
                tenant_id="tenant-a",
            )
        )
        audit = service.list_audit_entries("user-1")
        self.assertEqual(audit[-1].old_roles, ["viewer"])
        self.assertEqual(audit[-1].new_roles, ["contributor", "viewer"])

    def test_endpoint_contracts(self):
        service = RoleAssignmentService()
        status, body = service.assign_role_endpoint(
            {
                "subject_id": "user-2",
                "role": "tenant_admin",
                "tenant_id": "tenant-a",
            },
            actor="admin-1",
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["role"], "tenant_admin")

        audit_status, audit_body = service.role_audit_endpoint("user-2")
        self.assertEqual(audit_status, 200)
        self.assertEqual(len(audit_body["entries"]), 1)


if __name__ == "__main__":
    unittest.main()
