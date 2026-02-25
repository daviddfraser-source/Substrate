# Determinism and Concurrency Contract v1 (Phase 5)

## Scope

This contract defines deterministic behavior for all governed mutations and execution runs.

## Determinism Rules

- Equal input tuple must produce equal decision tuple.
  - Input tuple: `project_id`, `actor_id`, `action`, `entity_id`, `policy_version`, `state_version`, `idempotency_key`.
  - Decision tuple: `status`, `policy_result`, `constraint_result`, `reason_codes`.
- No hidden random behavior in policy or transition decisions.
- Time-dependent checks must use explicit provided timestamps, not implicit now-time, for replay paths.

## Idempotency Rules

- All mutating API calls require `idempotency_key`.
- Replayed requests with same key and same input tuple must return equivalent decision and original `event_id`.
- Reused key with different input tuple must fail with deterministic error code.

## Ordering Rules

- Entity-level state mutations are linearized by entity lock.
- Cross-entity operations must define lock order by lexical `entity_id` to avoid deadlocks.
- Audit append event is part of the mutation transaction boundary.

## Concurrency Rules

- Policy and budget checks are evaluated against the same committed snapshot used for mutation.
- Budget consume is atomic with execution commit to prevent negative or double-spent balances.
- On contention/timeouts, operation must fail explicitly; no silent retries that mutate outcome ordering.

## Replay Requirements

- Event log replay against baseline snapshot must regenerate identical final state and decision outcomes.
- Replay fixture must include at least:
  - mixed allow/deny policy outcomes
  - concurrent budget check/consume attempts
  - failed transition with preserved denial reason

## Failure Semantics

- Denials are first-class outcomes, not exceptions.
- Exceptions must map to stable error codes and logged failure events.
- Partial mutation without audit append is prohibited.
