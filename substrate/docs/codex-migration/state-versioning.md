# State Versioning Contract

State file: `.governance/wbs-state.json`

## Required Top-Level Fields
- `version`
- `created_at`
- `updated_at`
- `packets`
- `log`
- `area_closeouts`

## Compatibility Rules
- Legacy state without `version` is treated as pre-1.0 and migrated to `1.0`.
- State loaders must preserve existing packet/log data while adding missing contract fields.
- Unknown version values must fail with explicit error until a migration path is provided.

## Migration Runner
```bash
python3 .governance/migrate_state.py .governance/wbs-state.json
```
