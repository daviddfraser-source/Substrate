from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any, Dict


def append_ai_event(
    state: Dict[str, Any],
    *,
    actor_id: str,
    agent_id: str,
    prompt_version: str,
    model_version: str,
    tokens_in: int,
    tokens_out: int,
    policy_result: str,
    constraint_result: str,
    cost_estimate: float,
    execution_id: str,
) -> Dict[str, Any]:
    event = {
        "event_type": "execution.run",
        "timestamp": datetime.now().isoformat(),
        "actor_id": actor_id,
        "agent_id": agent_id,
        "prompt_version": prompt_version,
        "model_version": model_version,
        "tokens_in": int(tokens_in),
        "tokens_out": int(tokens_out),
        "policy_result": policy_result,
        "constraint_result": constraint_result,
        "cost_estimate": float(cost_estimate),
        "execution_id": execution_id,
    }
    state.setdefault("ai_events", []).append(event)
    return event


def metrics_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    events = [e for e in state.get("ai_events", []) if isinstance(e, dict)]
    if not events:
        return {
            "event_count": 0,
            "token_burn_per_agent": {},
            "cost_per_project": 0.0,
            "policy_rejection_count": 0,
            "average_execution_latency_ms": 0.0,
        }

    token_burn_per_agent: Dict[str, int] = {}
    total_cost = 0.0
    policy_rejects = 0
    # Latency field reserved for future; default synthetic 0 where absent.
    latencies = []
    for event in events:
        agent = str(event.get("agent_id") or "")
        token_total = int(event.get("tokens_in", 0)) + int(event.get("tokens_out", 0))
        token_burn_per_agent[agent] = token_burn_per_agent.get(agent, 0) + token_total
        total_cost += float(event.get("cost_estimate", 0.0))
        if str(event.get("policy_result") or "").lower() == "deny":
            policy_rejects += 1
        latencies.append(float(event.get("latency_ms", 0.0)))

    return {
        "event_count": len(events),
        "token_burn_per_agent": token_burn_per_agent,
        "cost_per_project": round(total_cost, 8),
        "policy_rejection_count": policy_rejects,
        "average_execution_latency_ms": round(mean(latencies), 3) if latencies else 0.0,
    }


__all__ = ["append_ai_event", "metrics_snapshot"]
