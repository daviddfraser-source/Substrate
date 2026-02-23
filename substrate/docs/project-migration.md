# Project Migration Guide

## Purpose
Migrate from single-project governance to project-scoped governance with minimal disruption.

## Baseline
- `main` is the default project and remains backward-compatible with existing:
  - `.governance/wbs.json`
  - `.governance/wbs-state.json`

## Quick Migration
```bash
substrate/scripts/migrate-to-projects.sh
```

This ensures:
- `.governance/current-project.json` exists
- active project is visible via `project-show`

## Create Additional Project Namespace
```bash
WBS_CHANGE_APPROVAL=WBS-APPROVED:GOV-13-8 \
substrate/scripts/migrate-to-projects.sh --create client-a
```

Or seed from explicit WBS file:
```bash
WBS_CHANGE_APPROVAL=WBS-APPROVED:GOV-13-8 \
substrate/scripts/migrate-to-projects.sh --create client-a --from substrate/templates/wbs-codex-minimal.json
```

## Activate Project
```bash
WBS_CHANGE_APPROVAL=WBS-APPROVED:GOV-13-8 \
substrate/scripts/migrate-to-projects.sh --activate client-a
```

## CLI Usage
- Show project context:
```bash
python3 substrate/.governance/wbs_cli.py project-show
```
- List projects:
```bash
python3 substrate/.governance/wbs_cli.py project-list
```
- Run one-off command in specific project:
```bash
python3 substrate/.governance/wbs_cli.py --project client-a status
```

## Guardrails
- Structural WBS mutation requires approval token in strict mode.
- Git commit guard requires trailer when protected WBS/governance definition files change:
  - `WBS-Change-Approved: <change-id>`
