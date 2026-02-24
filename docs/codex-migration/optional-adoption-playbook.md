# Optional Scaffold Adoption Playbook

Date: 2026-02-24
Packet: PRD-7-3

## Objective

Enable teams to adopt optional app-shell modules incrementally from a stable core-governance baseline.

## Migration Paths

### Path A: Core-only (default)

1. Set `SUBSTRATE_PROFILE=core-governance`.
2. Keep optional shell toggles disabled.
3. Validate lifecycle/API operations.

### Path B: Incremental opt-in

1. Enable optional shell in non-production environment.
2. Register a limited hook set and validate behavior.
3. Enable extension panels after hook behavior is stable.
4. Promote to production after rollback validation.

### Path C: Full scaffold

1. Set `SUBSTRATE_PROFILE=full-scaffold`.
2. Enable shell hooks and extension panels.
3. Validate UI and API parity with core behavior.

## Operational Tradeoffs

- Core-only: minimal operational surface, reduced UI ergonomics.
- Incremental: lower risk, slower feature adoption.
- Full scaffold: highest feature coverage, larger change surface.

## Reversible Rollback Procedure

1. Disable optional shell toggles.
2. Redeploy using `core-governance` profile.
3. Verify packet lifecycle and API endpoints.
4. Keep optional modules isolated from core state transitions.

## Adoption Checklist

- [ ] Core profile validated in target environment
- [ ] Optional toggles documented and version-controlled
- [ ] Rollback tested and timed
- [ ] Audit and metrics continuity verified during toggle transitions
