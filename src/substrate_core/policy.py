from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

from substrate_core.state import ActorContext

POLICY_PRECEDENCE = [
    "constitutional",
    "governance",
    "risk",
    "capability",
    "environment",
]


@dataclass(frozen=True)
class PolicyDecision:
    allow: bool
    message: str
    trace: List[Dict[str, Any]]
    policy_version: str


def evaluate_policy(
    definition: Dict[str, Any],
    *,
    packet_id: str,
    actor: ActorContext,
    transition: str,
    state: Dict[str, Any],
) -> PolicyDecision:
    policy, version = resolve_policy_document(definition, state)
    if policy is None:
        return PolicyDecision(True, "ok", [], "")
    if not isinstance(policy, dict):
        return PolicyDecision(False, "Policy configuration is invalid", [], "")

    version = version or str(policy.get("version") or "").strip()
    if not version:
        return PolicyDecision(False, "Missing policy version", [], "")

    rules = policy.get("rules", [])
    if not isinstance(rules, list):
        return PolicyDecision(False, "Policy rules must be a list", [], version)

    grouped: Dict[str, List[Dict[str, Any]]] = {k: [] for k in POLICY_PRECEDENCE}
    for raw in rules:
        if not isinstance(raw, dict):
            return PolicyDecision(False, "Invalid policy rule payload", [], version)
        domain = str(raw.get("domain") or "").strip().lower()
        if domain not in grouped:
            return PolicyDecision(False, f"Unknown policy domain: {domain}", [], version)
        grouped[domain].append(raw)

    trace: List[Dict[str, Any]] = []
    for domain in POLICY_PRECEDENCE:
        for rule in grouped[domain]:
            rule_id = str(rule.get("id") or "unnamed-rule")
            applies = _rule_applies(rule, packet_id=packet_id, actor=actor, transition=transition, state=state)
            effect = str(rule.get("effect") or "deny").strip().lower()
            if effect not in {"allow", "deny"}:
                return PolicyDecision(False, f"Unknown policy effect on rule {rule_id}", trace, version)

            decision = "skip"
            if applies:
                decision = effect
                trace.append({"rule_id": rule_id, "domain": domain, "decision": decision})
                if effect == "deny":
                    return PolicyDecision(False, f"Denied by policy rule {rule_id}", trace, version)
                continue
            trace.append({"rule_id": rule_id, "domain": domain, "decision": decision})

    return PolicyDecision(True, "ok", trace, version)


def evaluate_policy_with_opa(
    definition: Dict[str, Any],
    *,
    packet_id: str,
    actor: ActorContext,
    transition: str,
    state: Dict[str, Any],
) -> PolicyDecision:
    native = evaluate_policy(
        definition,
        packet_id=packet_id,
        actor=actor,
        transition=transition,
        state=state,
    )
    if not native.allow:
        return native

    policy, version = resolve_policy_document(definition, state)
    if not isinstance(policy, dict):
        return native
    opa = policy.get("opa")
    if not isinstance(opa, dict) or not bool(opa.get("enabled", False)):
        return native

    mode = str(opa.get("mode") or "optional").strip().lower()
    decision = state.get("opa_adapter_result")
    if not isinstance(decision, dict):
        if mode == "required":
            return PolicyDecision(False, "OPA decision unavailable", native.trace, version or native.policy_version)
        return native

    allow = bool(decision.get("allow", False))
    reason = str(decision.get("reason") or "").strip() or "OPA denied decision"
    trace = list(native.trace)
    trace.append(
        {
            "rule_id": str(decision.get("rule_id") or "opa-adapter"),
            "domain": "opa",
            "decision": "allow" if allow else "deny",
        }
    )
    if not allow:
        return PolicyDecision(False, reason, trace, version or native.policy_version)
    return PolicyDecision(True, "ok", trace, version or native.policy_version)


def resolve_policy_document(definition: Dict[str, Any], state: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str]:
    registry = state.get("policy_registry", {})
    if isinstance(registry, dict):
        active = str(registry.get("active_version") or "").strip()
        versions = registry.get("versions", {})
        if active and isinstance(versions, dict):
            entry = versions.get(active, {})
            if isinstance(entry, dict):
                policy = entry.get("policy")
                if isinstance(policy, dict):
                    return policy, active
    policy = definition.get("policy")
    if isinstance(policy, dict):
        return policy, str(policy.get("version") or "").strip()
    return None, ""


def register_policy_version(
    state: Dict[str, Any],
    *,
    version_id: str,
    policy: Dict[str, Any],
    actor: ActorContext,
    rationale: str,
) -> Tuple[bool, str]:
    token = str(version_id or "").strip()
    if not token:
        return False, "version_id is required"
    if not rationale.strip():
        return False, "rationale is required"
    if not isinstance(policy, dict):
        return False, "policy must be an object"

    registry = state.setdefault("policy_registry", {})
    versions = registry.setdefault("versions", {})
    if token in versions:
        return False, f"Policy version already exists: {token}"
    versions[token] = {
        "version_id": token,
        "policy": policy,
        "status": "draft",
        "rationale": rationale,
        "created_by": actor.user_id,
        "created_at": datetime.now().isoformat(),
        "approval": None,
    }
    return True, "ok"


def activate_policy_version(
    state: Dict[str, Any],
    *,
    version_id: str,
    actor: ActorContext,
    approvals: List[str],
    rationale: str,
) -> Tuple[bool, str]:
    token = str(version_id or "").strip()
    if not token:
        return False, "version_id is required"
    if not rationale.strip():
        return False, "rationale is required"
    if not approvals:
        return False, "at least one approval is required"

    registry = state.setdefault("policy_registry", {})
    versions = registry.setdefault("versions", {})
    entry = versions.get(token)
    if not isinstance(entry, dict):
        return False, f"Policy version not found: {token}"

    current_active = str(registry.get("active_version") or "").strip()
    if entry.get("status") == "active" and current_active == token:
        return False, f"Policy version already active: {token}"

    if current_active and current_active in versions and current_active != token:
        prev = versions[current_active]
        if isinstance(prev, dict):
            prev["status"] = "superseded"
            prev["superseded_at"] = datetime.now().isoformat()

    entry["status"] = "active"
    entry["approval"] = {
        "approved_by": approvals,
        "approved_by_actor": actor.user_id,
        "approved_at": datetime.now().isoformat(),
        "rationale": rationale,
    }
    registry["active_version"] = token
    return True, "ok"


def _rule_applies(
    rule: Dict[str, Any],
    *,
    packet_id: str,
    actor: ActorContext,
    transition: str,
    state: Dict[str, Any],
) -> bool:
    rule_type = str(rule.get("type") or "").strip().lower()
    match = rule.get("match", {})
    if not isinstance(match, dict):
        return False

    target_packet = str(match.get("packet_id") or "").strip()
    if target_packet and target_packet != packet_id:
        return False
    target_transition = str(match.get("transition") or "").strip().lower()
    if target_transition and target_transition != transition.lower():
        return False

    if rule_type == "role":
        allowed_roles = {str(v).strip() for v in (match.get("roles") or []) if str(v).strip()}
        return bool(allowed_roles) and actor.role in allowed_roles

    if rule_type == "status":
        expected = {str(v).strip().lower() for v in (match.get("statuses") or []) if str(v).strip()}
        current = str(state.get("packets", {}).get(packet_id, {}).get("status", "")).strip().lower()
        return bool(expected) and current in expected

    if rule_type == "actor":
        expected = {str(v).strip() for v in (match.get("actors") or []) if str(v).strip()}
        return bool(expected) and actor.user_id in expected

    return False


__all__ = [
    "POLICY_PRECEDENCE",
    "PolicyDecision",
    "evaluate_policy",
    "evaluate_policy_with_opa",
    "resolve_policy_document",
    "register_policy_version",
    "activate_policy_version",
]
