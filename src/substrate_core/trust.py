from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from substrate_core.state import ActorContext


def compute_trust_score(signals: Dict[str, float], weights: Dict[str, float]) -> Dict[str, Any]:
    total_weight = 0.0
    weighted_sum = 0.0
    contributions: List[Dict[str, Any]] = []

    for key, weight in weights.items():
        w = float(weight)
        s = float(signals.get(key, 0.0))
        if s < 0:
            s = 0.0
        if s > 1:
            s = 1.0
        total_weight += max(w, 0.0)
        contrib = max(w, 0.0) * s
        weighted_sum += contrib
        contributions.append({"signal": key, "weight": w, "value": s, "contribution": round(contrib, 6)})

    score = 0.0 if total_weight == 0 else weighted_sum / total_weight
    return {
        "score": round(score, 6),
        "total_weight": round(total_weight, 6),
        "contributions": contributions,
    }


def register_trust_model(
    state: Dict[str, Any],
    *,
    version_id: str,
    weights: Dict[str, float],
    actor: ActorContext,
    rationale: str,
    approvals: List[str],
) -> Tuple[bool, str]:
    token = str(version_id or "").strip()
    if not token:
        return False, "version_id is required"
    if not rationale.strip():
        return False, "rationale is required"
    if not approvals:
        return False, "at least one approval is required"
    if not isinstance(weights, dict) or not weights:
        return False, "weights must be a non-empty object"

    registry = state.setdefault("trust_registry", {})
    models = registry.setdefault("models", {})
    if token in models:
        return False, f"Trust model already exists: {token}"

    models[token] = {
        "version_id": token,
        "weights": {k: float(v) for k, v in weights.items()},
        "rationale": rationale,
        "approved_by": approvals,
        "approved_by_actor": actor.user_id,
        "approved_at": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
    }
    registry["active_model"] = token
    return True, "ok"


def score_with_active_model(state: Dict[str, Any], signals: Dict[str, float]) -> Tuple[bool, str, Dict[str, Any]]:
    registry = state.get("trust_registry", {})
    if not isinstance(registry, dict):
        return False, "Trust registry missing", {}
    active = str(registry.get("active_model") or "").strip()
    models = registry.get("models", {})
    if not active or not isinstance(models, dict) or active not in models:
        return False, "Active trust model not configured", {}
    model = models[active]
    weights = model.get("weights", {})
    if not isinstance(weights, dict):
        return False, "Active trust model weights invalid", {}
    result = compute_trust_score(signals, weights)
    result["model_version"] = active
    result["rationale"] = model.get("rationale", "")
    return True, "ok", result


__all__ = ["compute_trust_score", "register_trust_model", "score_with_active_model"]
