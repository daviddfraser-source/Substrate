# API Contract v1 (Phase 5)

## Scope

This contract defines the canonical API behavior for governed Phase 5 surfaces.

## Base Rules

- All state mutation endpoints are server-enforced and governance-mediated.
- All mutation responses use a shared decision envelope.
- All responses include `request_id` and `timestamp`.

## Mutation Envelope

```json
{
  "request_id": "uuid",
  "timestamp": "ISO-8601",
  "status": "allowed|denied|error",
  "decision": {
    "action": "claim|done|fail|note|execute|policy_update|budget_update",
    "entity_id": "string",
    "actor_id": "string",
    "policy_result": "allow|deny",
    "constraint_result": "pass|deny",
    "reason_codes": ["string"],
    "event_id": "uuid"
  },
  "data": {},
  "errors": []
}
```

## Error Envelope

```json
{
  "request_id": "uuid",
  "timestamp": "ISO-8601",
  "status": "error",
  "errors": [
    {
      "code": "P5-E-XXX",
      "message": "human-readable",
      "details": {}
    }
  ]
}
```

## Initial Endpoint Surface

- `POST /governance/claim`
- `POST /governance/done`
- `POST /governance/fail`
- `POST /governance/note`
- `POST /execution/run`
- `POST /policy/evaluate`
- `POST /policy/version/activate`
- `POST /budget/check`
- `GET /analytics/token-usage`
- `GET /analytics/agent-performance`
- `GET /analytics/policy-compliance`
- `GET /analytics/workflow-metrics`
- `GET /analytics/budget-summary`
- `GET /analytics/trend/{metric}`

## Request Invariants

- `actor_id` is required for all mutating requests.
- `project_id` is required for all project-scoped requests.
- Mutating requests must include `idempotency_key`.

## Response Invariants

- Denials are explicit and return reason codes.
- No silent fallback on policy errors.
- Unknown policy or missing contract state returns `denied`.
