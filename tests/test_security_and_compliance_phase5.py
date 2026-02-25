import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.compliance_recovery import BackupRecoveryManager, ImmutableAuditLog  # noqa: E402
from app.security_controls import (  # noqa: E402
    BudgetStopper,
    ExecutionSandboxController,
    MutationAttempt,
    MutationProtector,
    RateLimiter,
)


class SecurityCompliancePhase5Tests(unittest.TestCase):
    def test_mutation_protection_budget_and_rate_limit(self):
        protector = MutationProtector()
        protector.enforce(MutationAttempt(actor="codex", packet_id="P", action="claim", via_policy_pipeline=True))

        budget = BudgetStopper()
        budget.configure("codex", 10)
        budget.consume("codex", 5)
        with self.assertRaises(PermissionError):
            budget.consume("codex", 6)

        limiter = RateLimiter(per_minute=2)
        self.assertTrue(limiter.allow("api", now=1.0))
        self.assertTrue(limiter.allow("api", now=2.0))
        self.assertFalse(limiter.allow("api", now=3.0))

    def test_sandbox_and_compliance_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            sandbox = ExecutionSandboxController(allowed_commands=["echo"])
            ok, output = sandbox.run(["echo", "safe"], workdir)
            self.assertTrue(ok)
            self.assertIn("safe", output)

            log = ImmutableAuditLog()
            rec = log.append("auditor", "export", {"scope": "tenant"})
            self.assertTrue(rec.event_id.startswith("evt-"))
            payload = json.loads(log.export())
            self.assertEqual(payload[0]["action"], "export")

            src_file = workdir / "state.json"
            src_file.write_text('{"ok":true}\n', encoding="utf-8")
            mgr = BackupRecoveryManager()
            backup_dir = mgr.backup([src_file], workdir / "backup")

            restore_root = workdir / "restore"
            restore_root.mkdir()
            mgr.restore(backup_dir, restore_root)
            restored = restore_root / "state.json"
            self.assertTrue(restored.exists())
            self.assertIn('"ok":true', restored.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
