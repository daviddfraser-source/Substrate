# WBS 8.5 Governance Handoff

Date: 2026-02-13
From: codex-lead
To: next operator

## Handoff State
- WBS 1-8 packets complete.
- Dependency gating in place in `.governance/wbs.json`.
- Active process contracts documented in `AGENTS.md`.

## Required Operator Routine
1. `./scripts/preflight.sh .governance/wbs.json`
2. `python3 .governance/wbs_cli.py ready`
3. Execute claim/done/note lifecycle with evidence.
4. Run `./scripts/quality-gates.sh` before release.

## Evidence Index
- WBS 1: `docs/codex-migration/wbs1-delivery-evidence.md`
- WBS 2: `docs/codex-migration/wbs2-delivery-evidence.md`
- WBS 5: `docs/codex-migration/wbs5-delivery-evidence.md`
- WBS 6: `docs/codex-migration/wbs6-delivery-evidence.md`
- WBS 7: `docs/codex-migration/wbs7-delivery-evidence.md`
- WBS 8: `docs/codex-migration/wbs8-delivery-evidence.md`
