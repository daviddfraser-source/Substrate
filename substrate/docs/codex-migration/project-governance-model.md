# Project-Scoped Governance Model

## Goal
Support multiple governed projects in one repository while preventing cross-project WBS/state mutation.

## Active Project Selector
- File: `substrate/.governance/current-project.json`
- Shape:
  - `active_project`: canonical project id
  - `updated_at`: timestamp
- Environment override:
  - `WBS_PROJECT=<project-id>` takes precedence for the running command/session.

## Project Identity Rules
- Canonical id normalization:
  - lowercase
  - allowed chars: `a-z`, `0-9`, `.`, `_`, `-`
  - invalid chars collapse to `-`
- Reserved default id: `main`.

## Runtime Path Resolution
- `main` project remains backward-compatible with existing paths in `substrate/.governance/`.
- Non-main projects resolve under:
  - `substrate/projects/<project-id>/wbs.json`
  - `substrate/projects/<project-id>/wbs-state.json`
  - `substrate/projects/<project-id>/residual-risk-register.json`
  - `substrate/projects/<project-id>/break-fix-log.json`
  - `substrate/projects/<project-id>/e2e-runs.json`

## Isolation Guarantees
- CLI/API operations read/write only active project paths.
- Lifecycle logs are project-local because they are stored in project-local `wbs-state.json`.
- Break-fix/risk/e2e artifacts are project-local for non-main projects.

## Migration Strategy
1. Keep `main` mapped to current legacy files (`substrate/.governance/*`) to avoid breakage.
2. Add commands to create/switch projects.
3. Copy existing `main` baseline into new projects when requested.
4. Keep guards requiring explicit approval on structural mutation regardless of project.
