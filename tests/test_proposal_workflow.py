import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.proposals import ProposalWorkflow  # noqa: E402


class ProposalWorkflowTests(unittest.TestCase):
    def test_manual_review_flow(self):
        flow = ProposalWorkflow()
        flow.create_proposal("P-1", "Tune risk threshold", "risk_threshold_tuning", "agent-1")
        flow.mark_in_review("P-1", "gov-officer")
        proposal = flow.review("P-1", "gov-officer", "approve", "looks safe")
        self.assertEqual(proposal.status, "approved")
        self.assertEqual(proposal.decision_by, "gov-officer")

    def test_denied_types_blocked(self):
        flow = ProposalWorkflow()
        with self.assertRaises(PermissionError):
            flow.create_proposal("P-2", "Bypass auth", "authentication_bypass", "agent-1")

    def test_auto_apply_prohibited(self):
        flow = ProposalWorkflow()
        flow.create_proposal("P-3", "Refine lifecycle", "lifecycle_rule_refinement", "agent-1")
        with self.assertRaises(PermissionError):
            flow.auto_apply("P-3")


if __name__ == "__main__":
    unittest.main()
