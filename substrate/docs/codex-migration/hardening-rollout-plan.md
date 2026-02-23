# Hardening Rollout Plan (WBS 12)

## Phase A: Internal Stabilization
- Run migration on active state files.
- Validate CLI/server parity with existing workflows.
- Run full test suite and scaffold-check.

## Phase B: Controlled Adoption
- Enable supervisor policy requirements in operational runbooks.
- Use skill permission policy in all automated skill runs.
- Require schema registry check in CI.

## Phase C: Broad Rollout
- Publish updated template bundle.
- Adopt WBS 12 hardening modules as baseline in new scaffold users.
- Track incident/regression metrics for one release cycle.

## Rollback Strategy
- Keep compatibility CLI and server interfaces intact.
- Revert to prior bundle while preserving state backups if blocking issues occur.
