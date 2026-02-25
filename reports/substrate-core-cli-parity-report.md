# Substrate Core Refactor Parity Report (WBS 15.11)

## Scope
CLI/API/terminal parity checks after migrating lifecycle mutations to `src/substrate_core/PacketEngine`.

## Test Evidence
- `python3 -m unittest tests/test_cli_contract.py tests/test_cli_e2e.py tests/test_cli_transitions_edge.py tests/test_cli_export.py`
  - Result: 17 tests passed.
- `python3 -m unittest tests/test_server_api.py tests/test_terminal_engine_integration.py`
  - Result: 15 tests passed.

## Parity Findings
- CLI lifecycle command outputs and transitions remain compatible for claim/done/note/fail/reset paths.
- Dependency gating and handover constraints remain enforced.
- API mutation endpoints execute engine directly (no CLI subprocess dependency).
- Embedded terminal substrate command paths execute engine/in-process handlers directly (no CLI subprocess dependency).
- Mutation logs for refactored paths include structured fields (`actor`, `role`, `source`, `action`, `packet`, `result`, `timestamp`).

## Residual Notes
- One combined long-run test invocation produced a transient docs-index timeout; isolated rerun and grouped suite runs passed cleanly.
