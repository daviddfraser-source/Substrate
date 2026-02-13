# Error Codes

This catalog standardizes common operator-facing failures. Codes are stable documentation identifiers even when message wording evolves.

## Governance Lifecycle

- `WBS-E-001` Packet not found
  - Action: verify packet id in `.governance/wbs.json`.
- `WBS-E-002` Packet already claimed/in progress
  - Action: check assignee in `status` and coordinate handoff/reset.
- `WBS-E-003` Dependencies unresolved
  - Action: run `ready` and complete upstream packets first.
- `WBS-E-004` Invalid transition for current state
  - Action: inspect packet state and use allowed transition path.

## Validation and Schema

- `WBS-E-101` WBS definition validation failed
  - Action: run `python3 .governance/wbs_cli.py validate` and fix reported issues.
- `WBS-E-102` Packet schema validation failed
  - Action: run `python3 .governance/wbs_cli.py validate-packet <path>`.
- `WBS-E-103` Schema registry missing or invalid
  - Action: verify `.governance/schema-registry.json` and referenced schema paths.

## Dashboard/API

- `WBS-E-201` API route not found
  - Action: confirm dashboard server/port and endpoint path.
- `WBS-E-202` Invalid JSON request body
  - Action: resend request with valid JSON and required fields.
- `WBS-E-203` Packet viewer payload unavailable
  - Action: verify `/api/packet` response and restart stale server instance.

## Closeout/Drift

- `WBS-E-301` Level-2 closeout attempted with incomplete packets
  - Action: complete all area packets before `closeout-l2`.
- `WBS-E-302` Drift assessment missing required sections
  - Action: use `docs/drift-assessment-template.md`.
- `WBS-E-303` Drift assessment path not found
  - Action: verify file path and rerun closeout command.
