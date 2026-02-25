# Policy OPA Adapter Contract

## Purpose

Define deterministic OPA compatibility behavior without breaking native policy enforcement.

## Adapter Modes

- `optional`: if OPA decision is unavailable, native policy decision is used.
- `required`: if OPA decision is unavailable, transition is denied (`fail-closed`).

## Runtime Inputs

- Policy config:
  - `policy.opa.enabled` (bool)
  - `policy.opa.mode` (`optional|required`)
- OPA decision payload (state-driven adapter contract):
  - `state["opa_adapter_result"] = { "allow": bool, "reason": str, "rule_id": str }`

## Deterministic Resolution

1. Evaluate native policy first.
2. If native denies, deny immediately.
3. If OPA disabled, return native decision.
4. If OPA enabled and decision unavailable:
   - required mode: deny
   - optional mode: return native decision
5. If OPA decision present:
   - deny on `allow=false`
   - allow on `allow=true`
6. Append OPA trace decision to policy trace.
