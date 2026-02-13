# Codex Migration Release Checklist

## Scope Control
- [ ] Target WBS phase and packet IDs confirmed
- [ ] Dependency gating verified (`ready` shows expected first packet)
- [ ] Packet notes include artifact evidence paths

## Quality Gates
- [ ] `./scripts/quality-gates.sh` passes locally
- [ ] CI workflows pass (`quality-gates` and `python-matrix` jobs)
- [ ] Docs lint check passes (`scripts/check_docs_no_legacy_commands.sh`)

## Migration Artifacts
- [ ] `AGENTS.md` updated and aligned with reporting expectations
- [ ] `templates/wbs-codex-refactor.json` reflects current packet/dependency model
- [ ] `docs/codex-migration/` guide and evidence files updated

## Runtime and API
- [ ] `python3 .governance/wbs_cli.py --help` includes expected commands
- [ ] Dashboard action paths tested (claim/done/fail/reset/note)
- [ ] State files are valid JSON (`wbs.json`, `wbs-state.json`)

## Release and Handoff
- [ ] Optional bundle generated (`./scripts/build-release-bundle.sh`)
- [ ] Closeout report delivered to screen for completed WBS scope
- [ ] Each completed Level-2 area has `closeout-l2` drift assessment recorded
- [ ] Next ready packet and owner assigned
