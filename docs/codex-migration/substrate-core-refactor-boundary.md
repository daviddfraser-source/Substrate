# Substrate Core Refactor Boundary (WBS 15.1)

## Objective
Extract governance business logic from CLI and expose a reusable engine API under `src/substrate_core/` with no lifecycle behavior changes.

## Module Boundary
- `src/substrate_core/state.py`
  - Shared runtime data contracts (`ActorContext`, action result payloads).
- `src/substrate_core/storage.py`
  - `StorageInterface` plus `FileStorage` implementation for `.governance/wbs-state.json` and immutable append semantics.
- `src/substrate_core/validation.py`
  - Pure transition and dependency gating checks callable from CLI/API/terminal.
- `src/substrate_core/audit.py`
  - Structured mutation logging (`actor`, `role`, `source`, `action`, `packet`, `timestamp`, `result`).
- `src/substrate_core/engine.py`
  - `PacketEngine` mutation methods (`claim`, `done`, `fail`, `block`, `note`, `get_status`, `validate`).

## Interface Contract
- CLI remains argument parser/output formatter only.
- FastAPI/dashboard routes call `PacketEngine` directly (no CLI subprocess).
- Embedded terminal command parser maps command tokens to `PacketEngine` methods.

## No-Behavior-Change Guardrails
- Lifecycle statuses and dependency semantics remain unchanged.
- Existing state file shape remains compatible (`packets`, `log`, `area_closeouts`, integrity fields).
- Existing CLI command strings and exit code behavior remain intact for claim/done/note/fail/reset.
- Risk acknowledgement behavior for `done` remains enforced in CLI adapter.

## Explicit Non-Goals
- No new packet lifecycle features.
- No schema redesign for WBS definition/state.
- No storage migration to database in this phase.
- No command-surface expansion in CLI.

## Evidence Plan
- Engine unit tests with mocked storage for transition/error paths.
- API integration test verification for direct engine path.
- Terminal command path verification without CLI subprocess.
- Regression checks covering CLI lifecycle parity.
