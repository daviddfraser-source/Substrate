from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple


def configure_agent_budget(
    state: Dict[str, Any],
    *,
    agent_id: str,
    daily_cap: int,
    run_cap: int,
    actor_id: str,
) -> Tuple[bool, str]:
    token = str(agent_id or "").strip()
    if not token:
        return False, "agent_id is required"
    if daily_cap <= 0 or run_cap <= 0:
        return False, "daily_cap and run_cap must be positive integers"

    registry = state.setdefault("budget_registry", {})
    agent_budgets = registry.setdefault("agent_budgets", {})
    agent_budgets[token] = {
        "agent_id": token,
        "daily_cap": int(daily_cap),
        "run_cap": int(run_cap),
        "used_today": int(agent_budgets.get(token, {}).get("used_today", 0)),
        "updated_by": actor_id,
        "updated_at": datetime.now().isoformat(),
    }
    return True, "ok"


def check_budget(
    state: Dict[str, Any],
    *,
    agent_id: str,
    estimated_tokens: int,
) -> Tuple[bool, str, Dict[str, Any]]:
    registry = state.setdefault("budget_registry", {})
    agent_budgets = registry.setdefault("agent_budgets", {})
    budget = agent_budgets.get(agent_id)
    if not isinstance(budget, dict):
        return False, f"Budget not configured for agent: {agent_id}", {}
    run_cap = int(budget.get("run_cap", 0))
    daily_cap = int(budget.get("daily_cap", 0))
    used_today = int(budget.get("used_today", 0))
    if estimated_tokens > run_cap:
        return False, "Estimated tokens exceed run cap", {"run_cap": run_cap, "estimated_tokens": estimated_tokens}
    if used_today + estimated_tokens > daily_cap:
        return False, "Estimated tokens exceed daily cap", {"daily_cap": daily_cap, "used_today": used_today}
    return True, "ok", {"remaining_after_estimate": daily_cap - (used_today + estimated_tokens)}


def consume_budget(
    state: Dict[str, Any],
    *,
    agent_id: str,
    actual_tokens: int,
    execution_id: str,
) -> Tuple[bool, str]:
    registry = state.setdefault("budget_registry", {})
    agent_budgets = registry.setdefault("agent_budgets", {})
    budget = agent_budgets.get(agent_id)
    if not isinstance(budget, dict):
        return False, f"Budget not configured for agent: {agent_id}"
    budget["used_today"] = int(budget.get("used_today", 0)) + int(actual_tokens)
    ledger = state.setdefault("token_ledger", [])
    ledger.append(
        {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "tokens": int(actual_tokens),
            "timestamp": datetime.now().isoformat(),
        }
    )
    return True, "ok"


def budget_remaining(state: Dict[str, Any], *, agent_id: str) -> Dict[str, Any]:
    registry = state.get("budget_registry", {})
    budget = registry.get("agent_budgets", {}).get(agent_id, {})
    daily_cap = int(budget.get("daily_cap", 0))
    used_today = int(budget.get("used_today", 0))
    return {
        "agent_id": agent_id,
        "daily_cap": daily_cap,
        "used_today": used_today,
        "remaining": max(0, daily_cap - used_today),
    }


__all__ = [
    "configure_agent_budget",
    "check_budget",
    "consume_budget",
    "budget_remaining",
]
