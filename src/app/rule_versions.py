from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class RuleVersion:
    rule_name: str
    version: int
    content: str
    status: str
    rationale: str
    created_by: str
    created_at: str
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None


class RuleVersionStore:
    def __init__(self):
        self._rules: Dict[str, List[RuleVersion]] = {}

    def propose(self, rule_name: str, content: str, rationale: str, created_by: str) -> RuleVersion:
        history = self._rules.setdefault(rule_name, [])
        next_version = len(history) + 1
        version = RuleVersion(
            rule_name=rule_name,
            version=next_version,
            content=content,
            status="proposed",
            rationale=rationale,
            created_by=created_by,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        history.append(version)
        return version

    def approve(self, rule_name: str, version: int, approved_by: str) -> RuleVersion:
        candidate = self._find(rule_name, version)
        if candidate.status != "proposed":
            raise ValueError("Only proposed versions can be approved")
        candidate.status = "active"
        candidate.approved_by = approved_by
        candidate.approved_at = datetime.now(timezone.utc).isoformat()
        return candidate

    def rollback(self, rule_name: str, target_version: int, actor: str, rationale: str) -> RuleVersion:
        target = self._find(rule_name, target_version)
        if target.status != "active":
            raise ValueError("Rollback target must be active")

        new_proposal = self.propose(
            rule_name=rule_name,
            content=target.content,
            rationale=f"Rollback by {actor}: {rationale}",
            created_by=actor,
        )
        return self.approve(rule_name, new_proposal.version, approved_by=actor)

    def active(self, rule_name: str) -> Optional[RuleVersion]:
        history = self._rules.get(rule_name, [])
        active_versions = [item for item in history if item.status == "active"]
        if not active_versions:
            return None
        return active_versions[-1]

    def _find(self, rule_name: str, version: int) -> RuleVersion:
        history = self._rules.get(rule_name, [])
        for item in history:
            if item.version == version:
                return item
        raise KeyError("Rule version not found")
