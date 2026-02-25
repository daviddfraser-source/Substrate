from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from substrate_core.state import ActorContext


def register_prompt_version(
    state: Dict[str, Any],
    *,
    prompt_id: str,
    version_id: str,
    template_text: str,
    owner: str,
    model_compatibility: List[str],
    actor: ActorContext,
    rationale: str,
) -> Tuple[bool, str]:
    p_id = str(prompt_id or "").strip()
    v_id = str(version_id or "").strip()
    if not p_id:
        return False, "prompt_id is required"
    if not v_id:
        return False, "version_id is required"
    if not str(template_text or "").strip():
        return False, "template_text is required"
    if not str(owner or "").strip():
        return False, "owner is required"
    if not str(rationale or "").strip():
        return False, "rationale is required"

    registry = state.setdefault("prompt_registry", {})
    prompts = registry.setdefault("prompts", {})
    entry = prompts.setdefault(p_id, {"versions": {}, "active_version": ""})
    versions = entry.setdefault("versions", {})
    if v_id in versions:
        return False, f"Prompt version already exists: {p_id}@{v_id}"

    versions[v_id] = {
        "prompt_id": p_id,
        "version_id": v_id,
        "template_text": template_text,
        "owner": owner,
        "model_compatibility": list(model_compatibility or []),
        "status": "draft",
        "created_by": actor.user_id,
        "created_at": datetime.now().isoformat(),
        "change_log": [
            {
                "actor": actor.user_id,
                "timestamp": datetime.now().isoformat(),
                "action": "registered",
                "rationale": rationale,
            }
        ],
        "approval": None,
    }
    return True, "ok"


def activate_prompt_version(
    state: Dict[str, Any],
    *,
    prompt_id: str,
    version_id: str,
    actor: ActorContext,
    approvals: List[str],
    rationale: str,
) -> Tuple[bool, str]:
    p_id = str(prompt_id or "").strip()
    v_id = str(version_id or "").strip()
    if not p_id:
        return False, "prompt_id is required"
    if not v_id:
        return False, "version_id is required"
    if not approvals:
        return False, "at least one approval is required"
    if not str(rationale or "").strip():
        return False, "rationale is required"

    registry = state.setdefault("prompt_registry", {})
    prompts = registry.setdefault("prompts", {})
    entry = prompts.get(p_id)
    if not isinstance(entry, dict):
        return False, f"Prompt not found: {p_id}"
    versions = entry.get("versions", {})
    current = str(entry.get("active_version") or "").strip()
    if v_id not in versions:
        return False, f"Prompt version not found: {p_id}@{v_id}"

    if current and current in versions and current != v_id:
        versions[current]["status"] = "superseded"
        versions[current]["superseded_at"] = datetime.now().isoformat()

    active = versions[v_id]
    active["status"] = "active"
    active["approval"] = {
        "approved_by": list(approvals),
        "approved_by_actor": actor.user_id,
        "approved_at": datetime.now().isoformat(),
        "rationale": rationale,
    }
    active.setdefault("change_log", []).append(
        {
            "actor": actor.user_id,
            "timestamp": datetime.now().isoformat(),
            "action": "activated",
            "rationale": rationale,
        }
    )
    entry["active_version"] = v_id
    return True, "ok"


def resolve_active_prompt(state: Dict[str, Any], prompt_id: str) -> Tuple[bool, str, Dict[str, Any]]:
    p_id = str(prompt_id or "").strip()
    if not p_id:
        return False, "prompt_id is required", {}
    registry = state.get("prompt_registry", {})
    prompts = registry.get("prompts", {})
    entry = prompts.get(p_id)
    if not isinstance(entry, dict):
        return False, f"Prompt not found: {p_id}", {}
    active = str(entry.get("active_version") or "").strip()
    versions = entry.get("versions", {})
    if not active or active not in versions:
        return False, f"Active prompt version not configured: {p_id}", {}
    payload = dict(versions[active])
    payload["active_version"] = active
    return True, "ok", payload


__all__ = [
    "register_prompt_version",
    "activate_prompt_version",
    "resolve_active_prompt",
]
