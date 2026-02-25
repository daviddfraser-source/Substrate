# Template Pack Guide

## Purpose
Provide pre-baked governance bootstrap artifacts so new projects avoid token-heavy context reconstruction.

## Included Templates
- `templates/wbs-scaffold-build.json` — balanced enterprise scaffold archetype
- `templates/wbs-codex-minimal.json` — smallest governed startup
- `templates/wbs-codex-full.json` — broad, high-coverage scaffold
- `templates/constitution-enterprise-default.md` — enterprise default governance invariants

## Suggested Selection
- Fast prototype: `wbs-codex-minimal.json`
- Standard enterprise scaffold: `wbs-scaffold-build.json`
- Large multi-track delivery: `wbs-codex-full.json`

## Bootstrap Commands
```bash
scripts/init-scaffold.sh templates/wbs-scaffold-build.json
python3 .governance/wbs_cli.py ready
python3 .governance/wbs_cli.py claim <packet_id> <agent>
python3 .governance/wbs_cli.py context <packet_id> --format json
```

## Validation
Run strict checks before using templates in production:
```bash
python3 .governance/wbs_cli.py validate --strict
python3 .governance/wbs_cli.py validate-packet templates/wbs-scaffold-build.json
```
