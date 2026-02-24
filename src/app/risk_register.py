from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class RiskRecord:
    risk_id: str
    packet_id: str
    severity: int
    likelihood: int
    impact: int
    status: str
    escalation_level: str
    created_at: str


class RiskRegister:
    def __init__(self, risks: List[RiskRecord]):
        self.risks = list(risks)

    def grid_rows(self) -> List[Dict[str, str]]:
        return [
            {
                "risk_id": risk.risk_id,
                "packet_id": risk.packet_id,
                "status": risk.status,
                "severity": str(risk.severity),
                "escalation_level": risk.escalation_level,
            }
            for risk in self.risks
        ]

    def heatmap(self) -> Dict[str, int]:
        buckets: Dict[str, int] = {}
        for risk in self.risks:
            key = f"L{risk.likelihood}-I{risk.impact}"
            buckets[key] = buckets.get(key, 0) + 1
        return buckets

    def aging_view(self, now: str) -> List[Dict[str, str]]:
        now_dt = datetime.fromisoformat(now)
        out = []
        for risk in self.risks:
            age_days = (now_dt - datetime.fromisoformat(risk.created_at)).days
            out.append(
                {
                    "risk_id": risk.risk_id,
                    "packet_id": risk.packet_id,
                    "age_days": str(age_days),
                    "status": risk.status,
                }
            )
        return out
