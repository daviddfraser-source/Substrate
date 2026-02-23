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

## Session Continuity Hardening
- [ ] Briefing/context contracts validated with live commands:
  - `python3 .governance/wbs_cli.py briefing --format json --recent 20`
  - `python3 .governance/wbs_cli.py context <packet_id> --format json --max-events 40 --max-notes-bytes 4000 --max-handovers 40`
- [ ] Handover lifecycle validated with evidence:
  - `python3 .governance/wbs_cli.py handover <packet_id> <agent> "<reason>" --to <next_agent> --remaining "item1|item2"`
  - `python3 .governance/wbs_cli.py resume <packet_id> <next_agent>`
- [ ] Capability enforcement mode + registry validated:
  - `python3 .governance/wbs_cli.py agent-list`
  - `python3 .governance/wbs_cli.py agent-mode advisory`
- [ ] Planner flow validated:
  - `python3 .governance/wbs_cli.py plan --from-json planner-spec.json --output .governance/wbs-draft.json`
  - `python3 .governance/wbs_cli.py init .governance/wbs-draft.json`
  - `python3 .governance/wbs_cli.py validate`
- [ ] Experimental markdown import validation captured (if enabled):
  - `python3 .governance/wbs_cli.py plan --import-markdown docs/project-proposal.md --output .governance/wbs-imported.json`
- [ ] Git-native governance checks captured:
  - `python3 .governance/wbs_cli.py git-protocol --json`
  - `python3 .governance/wbs_cli.py --json git-verify-ledger --strict`
- [ ] Git-native rollout phase and mode explicitly recorded (disabled/advisory/strict)
- [ ] Reconstruction snapshot captured:
  - `python3 .governance/wbs_cli.py git-reconstruct --limit 500 --output reports/git-reconstruct.json`
- [ ] Rollback path tested and documented:
  - `python3 .governance/wbs_cli.py git-governance-mode advisory`
  - `python3 .governance/wbs_cli.py git-governance-autocommit off`
- [ ] KPI evidence captured using commands in `docs/codex-migration/enhancement-rollout.md`
- [ ] Rollback steps reviewed for all enhancement streams (briefing/context, handover, capability profiles, planner/import, git-native governance)

## Release and Handoff
- [ ] Optional bundle generated (`./scripts/build-release-bundle.sh`)
- [ ] Closeout report delivered to screen for completed WBS scope
- [ ] Each completed Level-2 area has `closeout-l2` drift assessment recorded
- [ ] Next ready packet and owner assigned
