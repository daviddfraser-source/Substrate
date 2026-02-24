from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


ALLOWED_TYPES = {
    "lifecycle_rule_refinement",
    "role_permission_adjustment",
    "dependency_rule_improvement",
    "risk_threshold_tuning",
    "ux_friction_reduction",
}

DENIED_TYPES = {
    "automatic_schema_modification",
    "authentication_bypass",
    "rbac_override",
    "auto_deployment_core_logic",
}


@dataclass
class Proposal:
    proposal_id: str
    title: str
    proposal_type: str
    created_by: str
    created_at: str
    status: str
    decision_by: Optional[str] = None
    decision_at: Optional[str] = None
    decision_notes: Optional[str] = None


class ProposalWorkflow:
    def __init__(self):
        self._proposals: Dict[str, Proposal] = {}
        self._audit: List[Dict[str, str]] = []

    def create_proposal(self, proposal_id: str, title: str, proposal_type: str, created_by: str) -> Proposal:
        if proposal_type in DENIED_TYPES:
            raise PermissionError("Proposal type denied by governance policy")
        if proposal_type not in ALLOWED_TYPES:
            raise ValueError("Unknown proposal type")
        now = datetime.now(timezone.utc).isoformat()
        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            proposal_type=proposal_type,
            created_by=created_by,
            created_at=now,
            status="submitted",
        )
        self._proposals[proposal_id] = proposal
        self._log(proposal_id, "submitted", created_by, "proposal created")
        return proposal

    def review(self, proposal_id: str, officer: str, decision: str, notes: str) -> Proposal:
        proposal = self._proposals[proposal_id]
        if proposal.status not in {"submitted", "in_review"}:
            raise ValueError("Proposal is not reviewable")
        if decision not in {"approve", "reject"}:
            raise ValueError("Decision must be approve or reject")

        now = datetime.now(timezone.utc).isoformat()
        proposal.status = "approved" if decision == "approve" else "rejected"
        proposal.decision_by = officer
        proposal.decision_at = now
        proposal.decision_notes = notes
        self._log(proposal_id, proposal.status, officer, notes)
        return proposal

    def mark_in_review(self, proposal_id: str, officer: str) -> Proposal:
        proposal = self._proposals[proposal_id]
        if proposal.status != "submitted":
            raise ValueError("Only submitted proposals can enter review")
        proposal.status = "in_review"
        self._log(proposal_id, "in_review", officer, "review started")
        return proposal

    def auto_apply(self, proposal_id: str) -> None:
        # Hard guardrail: workflow never supports autonomous application.
        raise PermissionError("Automatic application is prohibited by governance policy")

    def get(self, proposal_id: str) -> Proposal:
        return self._proposals[proposal_id]

    def audit_log(self) -> List[Dict[str, str]]:
        return list(self._audit)

    def _log(self, proposal_id: str, event: str, actor: str, notes: str) -> None:
        self._audit.append(
            {
                "proposal_id": proposal_id,
                "event": event,
                "actor": actor,
                "notes": notes,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
