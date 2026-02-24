import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.rule_versions import RuleVersionStore  # noqa: E402


class RuleVersionTests(unittest.TestCase):
    def test_explicit_approval_required(self):
        store = RuleVersionStore()
        proposal = store.propose("claim_policy", "allow_if_ready", "initial rule", "lead")
        self.assertEqual(proposal.status, "proposed")
        approved = store.approve("claim_policy", proposal.version, "gov-officer")
        self.assertEqual(approved.status, "active")

    def test_deterministic_rollback(self):
        store = RuleVersionStore()
        v1 = store.propose("claim_policy", "allow_if_ready", "initial", "lead")
        store.approve("claim_policy", v1.version, "gov-officer")
        v2 = store.propose("claim_policy", "allow_if_ready_and_capacity", "tighten", "lead")
        store.approve("claim_policy", v2.version, "gov-officer")

        rolled = store.rollback("claim_policy", 2, "gov-officer", "regression detected")
        self.assertEqual(rolled.status, "active")
        self.assertEqual(rolled.content, "allow_if_ready_and_capacity")


if __name__ == "__main__":
    unittest.main()
