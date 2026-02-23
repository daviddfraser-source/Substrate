# WBS Server API Contract Audit (WBS 6.1)

Date: 2026-02-13
Scope: `.governance/wbs_server.py` HTTP API

## Endpoints Reviewed
- GET: `/api/status`, `/api/ready`, `/api/progress`, `/api/log`
- POST: `/api/claim`, `/api/done`, `/api/note`, `/api/fail`, `/api/reset`, `/api/closeout-l2`
- POST (editing): `/api/add-packet`, `/api/add-area`, `/api/add-dep`, `/api/remove-dep`, `/api/edit-packet`, `/api/edit-area`, `/api/remove-packet`, `/api/save-wbs`

## Contract Findings
- Command endpoints return a stable shape: `{ "success": bool, "message": str }`.
- Read endpoints return structured JSON payloads for status/ready/progress/log.
- Lifecycle endpoints enforce required fields:
  - `packet_id` always required
  - `agent_name` required for `claim`, `done`, `note`, `fail`
  - `reset` requires only `packet_id`

## Improvements Implemented
1. Added `/api/note` endpoint parity with CLI `note` command.
2. Preserved existing response schema and command execution path (`run_cmd`).
3. Added regression tests for `claim`, `done`, `fail`, `reset`, plus validation for missing fields.
4. Added `/api/closeout-l2` to support Level-2 drift-assessment closeout workflow.

## Known Constraints
- API currently always responds with HTTP 200 and embeds failure in `{success:false}`.
- Editing endpoints are permissive by design; strict schema validation is not implemented.

## Recommendation
- Keep response shape stable for current dashboard clients.
- Consider introducing explicit non-200 statuses for malformed requests in a later hardening phase.
