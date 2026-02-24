# PRD v3 Architecture Boundary and Optionality Decision

Date: 2026-02-24
Decision owners: governance lead, platform lead
Authority: PRD v3.0 + constitutional governance controls

## Purpose

Define the mandatory core delivery baseline for Substrate App Scaffold and the optional app scaffold adoption boundary.

## Mandatory Core Baseline

The following capabilities are mandatory for core delivery:

- Governance lifecycle engine and packet state management
- Authentication and backend-enforced RBAC controls
- Database and migration baseline for required entities
- API contracts for governance modules and integrations
- Auditability, telemetry, and observability controls
- Deterministic recursive proposal workflow with manual approval requirement
- Deployment-ready runtime profiles and baseline non-functional checks

These capabilities define the core governance control plane and must be independently operable.

## Optional App Scaffold Adoption Track

Optional means adopters may run the core governance platform without enabling the full app-shell package.

Optional scope includes:

- App-shell packaging profile
- Optional frontend shell module wiring
- Optional adoption and migration playbook

Optional modules may be enabled incrementally and must not be required for core packet lifecycle, API governance, or closeout readiness.

## Dependency and Closeout Boundary

Dependency policy for active WBS:

- Area `7.0` (`PRD-7-1` to `PRD-7-3`) is optional.
- Release closeout path (`PRD-8-1`, `PRD-8-2`) does not depend on `7.x` packets.
- Core closeout is gated by mandatory tracks only (areas `1.0` to `6.0`, then `8.0`).

This preserves optional app adoption while maintaining deterministic and auditable core delivery.

## Guardrails

- No optional module may introduce hard runtime dependency for mandatory core flows.
- No optional module may bypass or weaken RBAC, authentication, or audit controls.
- Any optional toggle must have deterministic enabled/disabled behavior and documented rollback.

## Evidence

- `.governance/wbs.json` dependency graph (no `7.x` prerequisites for `PRD-8-1` / `PRD-8-2`)
- `python3 .governance/wbs_cli.py validate`
- `python3 .governance/wbs_cli.py ready`

