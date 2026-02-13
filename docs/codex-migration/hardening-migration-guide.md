# Hardening Migration Guide (WBS 12)

## Objective
Migrate from CLI-coupled governance logic to layered governed platform modules.

## Migration Sequence
1. Introduce `src/governed_platform/governance` (engine + state manager + migrations).
2. Route CLI lifecycle commands to `GovernanceEngine`.
3. Enable supervisor policy hooks for mutating transitions.
4. Add skill execution engine with sandbox and permission policy.
5. Register and enforce schema authority.
6. Add deterministic fingerprint and reproducibility checks.

## Runtime Compatibility
- Existing `.governance/wbs_cli.py` and `.governance/wbs_server.py` remain operator entrypoints.
- State is migrated in place with `.governance/migrate_state.py`.

## Verification
```bash
python3 -m unittest discover -s tests -v
scripts/scaffold-check.sh
scripts/repro-check.py
```
