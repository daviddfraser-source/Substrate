from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple


def register_agent_profile(
    state: Dict[str, Any],
    *,
    agent_id: str,
    owner: str,
    capabilities: List[str],
    allowed_tools: List[str],
    allowed_models: List[str],
    trust_score: float = 0.5,
) -> Tuple[bool, str]:
    token = str(agent_id or "").strip()
    if not token:
        return False, "agent_id is required"
    if not str(owner or "").strip():
        return False, "owner is required"
    registry = state.setdefault("agent_registry", {})
    profiles = registry.setdefault("profiles", {})
    profiles[token] = {
        "agent_id": token,
        "owner": owner,
        "capabilities": sorted({str(x).strip() for x in (capabilities or []) if str(x).strip()}),
        "allowed_tools": sorted({str(x).strip() for x in (allowed_tools or []) if str(x).strip()}),
        "allowed_models": sorted({str(x).strip() for x in (allowed_models or []) if str(x).strip()}),
        "trust_score": float(trust_score),
        "updated_at": datetime.now().isoformat(),
    }
    return True, "ok"


def validate_execution_guard(
    state: Dict[str, Any],
    *,
    actor_id: str,
    agent_id: str,
    model_name: str,
    requested_tools: List[str],
) -> Tuple[bool, str]:
    if not str(actor_id or "").strip():
        return False, "actor identity is required"
    registry = state.get("agent_registry", {})
    profile = registry.get("profiles", {}).get(agent_id, {})
    if not isinstance(profile, dict) or not profile:
        return False, f"Agent profile not registered: {agent_id}"
    allowed_models = set(profile.get("allowed_models", []))
    if model_name not in allowed_models:
        return False, f"Model not allowed for agent {agent_id}: {model_name}"
    allowed_tools = set(profile.get("allowed_tools", []))
    invalid_tools = [tool for tool in (requested_tools or []) if tool not in allowed_tools]
    if invalid_tools:
        return False, f"Tool access denied for agent {agent_id}: {', '.join(invalid_tools)}"
    return True, "ok"


__all__ = ["register_agent_profile", "validate_execution_guard"]
