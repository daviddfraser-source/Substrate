# Phase 5 Shared Decision Envelope

This document records the implemented shared decision envelope used by the governance lifecycle core for CLI and API surfaces.

## Engine Authority Path

- Core authority: `src/substrate_core/engine.py` (`PacketEngine`)
- CLI lifecycle adapters: `.governance/wbs_cli.py`
- API lifecycle adapters: `.governance/wbs_server.py` (`run_cmd`)

Both CLI and API invoke `PacketEngine` for `claim`, `done`, `note`, `fail`, and `reset` transitions.

## Decision Envelope

Lifecycle responses expose a `decision` object with:

- `action`
- `packet_id`
- `actor_id`
- `source`
- `status` (`allowed|denied`)
- `policy_result` (`allow|deny|null`)
- `constraint_result` (`pass|deny|null`)
- `reason_codes` (array)

## Surface Mapping

- CLI (`--json`) returns:
  - `success`
  - `message`
  - `decision`
  - `payload`
- API (`/api/claim|done|note|fail|reset`) returns:
  - `success`
  - `message`
  - `decision`
  - `payload`

## Parity Validation

- `tests/test_json_contract.py::test_lifecycle_json_includes_shared_decision_envelope`
- `tests/test_server_api.py::test_claim_and_done_endpoints`
- `tests/test_server_api.py::test_cli_api_claim_decision_parity`
