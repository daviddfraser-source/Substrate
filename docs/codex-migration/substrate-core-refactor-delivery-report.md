# Substrate Core Refactor Delivery Report (WBS 15.0)

## Scope Covered
- WBS 15.1-15.12 (Substrate Core Engine refactor for API + embedded terminal enablement).

## Delivered
- Introduced reusable core package under `src/substrate_core/`:
  - `storage.py` (`StorageInterface`, `FileStorage`)
  - `validation.py` (dependency/transition validators)
  - `audit.py` (structured mutation logging)
  - `state.py` (`ActorContext`, `EngineResult`)
  - `engine.py` (`PacketEngine`)
- Refactored CLI lifecycle mutation handlers in `.governance/wbs_cli.py` to call PacketEngine.
- Refactored API lifecycle endpoints in `.governance/wbs_server.py` to call PacketEngine directly (no CLI subprocess).
- Refactored embedded terminal substrate command path to engine/in-process execution (no CLI subprocess for substrate commands).
- Added unit and integration test coverage:
  - `tests/test_substrate_core_storage.py`
  - `tests/test_substrate_core_validation.py`
  - `tests/test_substrate_core_audit.py`
  - `tests/test_substrate_core_engine.py`
  - `tests/test_terminal_engine_integration.py`

## Evidence Artifacts
- Architecture boundary: `docs/codex-migration/substrate-core-refactor-boundary.md`
- Mutation log schema: `docs/codex-migration/substrate-core-mutation-log-schema.md`
- Mutation export sample: `reports/substrate-core-log-export-sample.json`
- Parity report: `reports/substrate-core-cli-parity-report.md`

## Validation Summary
- CLI parity suite: 17 tests passed.
- API + terminal suite: 15 tests passed.
- Substrate core unit suite: 17 tests passed.

## Residual Risks
- Some non-mutation CLI commands still depend on legacy governance engine paths by design (out of scope for this structural phase).
- One combined long-running test invocation hit transient docs-index timeout; isolated and grouped reruns passed.

## Immediate Next Actions
1. Expand PacketEngine coverage to handover/resume/closeout workflows for full governance consolidation.
2. Add dedicated API tests for structured mutation log field guarantees per endpoint.
