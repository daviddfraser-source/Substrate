# ADR: Governed Agent Platform Hardening Baseline

Date: 2026-02-13
Status: Accepted
Scope: WBS 12.0

## Context
The scaffold currently works as a governed execution tool, but core responsibilities are still concentrated in CLI entrypoints. This creates coupling between governance policy, execution mechanics, and state persistence.

## Decision
Adopt layered platform architecture with explicit authority boundaries:

1. Supervisor Layer
2. Governance Engine
3. Execution Engine
4. Skill Execution Engine
5. Sandbox Abstraction
6. Versioned State Manager
7. Schema Registry
8. Deterministic Verification

## Target Structure
`src/governed_platform/` contains:
- `governance/`
- `execution/`
- `skills/`
- `determinism/`

## Key Principles
- Governance policy must be independently evolvable from execution adapters.
- State must be versioned and migration-capable.
- Packet transitions must be supervisor-mediated.
- Skill execution must run through explicit sandbox + permission policies.
- Schema authority must be centralized and version-aware.
- Determinism must be verified with reproducible fingerprints.

## Compatibility Strategy
- Existing `.governance/wbs_cli.py` and `.governance/wbs_server.py` remain compatibility interfaces.
- New platform modules are introduced first, then command paths progressively delegated.
- Legacy state without explicit version is migrated through migration runner.

## Consequences
Positive:
- Clear responsibility boundaries
- Safer upgrades
- Better enterprise suitability

Tradeoffs:
- Added implementation complexity
- Additional test surface

## Acceptance Criteria
- Platform modules exist with test coverage.
- CLI lifecycle path delegates to governance engine.
- State versioning and migrations validated.
- Supervisor and sandbox enforcement paths tested.
- Deterministic verification available and tested.
