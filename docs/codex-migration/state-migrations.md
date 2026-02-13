# State Migration Baseline Scripts

Current migration scripts:
- `src/governed_platform/governance/migrations/v0_to_v1.py`
- `src/governed_platform/governance/migrations/v1_to_v1.py`
- `src/governed_platform/governance/migrations/runner.py`

## Intent
- `v0_to_v1`: upgrade legacy state with missing version metadata.
- `v1_to_v1`: normalize 1.0 state shape and required top-level fields.

## Execution
```bash
python3 .governance/migrate_state.py .governance/wbs-state.json
```
