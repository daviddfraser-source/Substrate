# Optional Shell Hooks and Extension Points

Date: 2026-02-24
Packet: PRD-7-2

## Module

- `app/src/ui/optionalShell.ts`

## Behaviors

- Optional shell can be fully disabled via config
- Hook registration is ignored when disabled
- Hook emission only runs in enabled mode
- Disabled mode is explicitly safety-checkable via `isDisabledModeSafe()`

## Extension Points

- event-based hook registration (`registerHook`)
- event dispatch (`emit`)

## Validation

- `python3 -m unittest tests/test_optional_shell_contract.py`
