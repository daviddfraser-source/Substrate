# Substrate Template Usage

## 1. Choose a Profile
- `.governance/wbs.json`: default clean baseline scaffold for clone-and-own starts.
- `templates/wbs-codex-minimal.json`: fast startup, minimal governance footprint.
- `templates/wbs-codex-full.json`: comprehensive scaffold setup.
- `templates/wbs-codex-refactor.json`: legacy migration compatibility profile.

## 2. Day-0 Bootstrap (Recommended)
```bash
scripts/init-scaffold.sh templates/wbs-codex-minimal.json
python3 .governance/wbs_cli.py ready
```

Reset to a clean scaffold state (idempotent):
```bash
scripts/reset-scaffold.sh templates/wbs-codex-minimal.json
```

Or use guided onboarding:
```bash
python3 start.py --wizard-scaffold
```

## 3. First Packet Lifecycle
```bash
python3 .governance/wbs_cli.py claim <packet_id> <agent>
python3 .governance/wbs_cli.py done <packet_id> <agent> "summary + evidence" --risk none
python3 .governance/wbs_cli.py note <packet_id> <agent> "updated evidence"
```

## 4. Health Checks
```bash
python3 .governance/wbs_cli.py template-validate
scripts/scaffold-check.sh
python3 .governance/wbs_cli.py risk-list --status open
```

## 5. Close Out Level-2 Areas
```bash
python3 .governance/wbs_cli.py closeout-l2 <area_id|n> <agent> docs/codex-migration/drift-wbs<area>.md "closeout note"
```

Use `docs/codex-migration/drift-assessment-template.md` for drift assessment structure.

## 6. Artifact Boundaries

Scaffold artifacts (commit/ship):
- `.governance/wbs.json`, `templates/*.json`, `scripts/*`, `docs/*`, `src/*`, `prompts/*`

Runtime artifacts (generated):
- `.governance/wbs-state.json`
- `.governance/activity-log.jsonl` (legacy format if present)
- `.governance/residual-risk-register.json`

Before publishing template forks:
- remove `.meta/`
- ensure runtime artifacts are not tracked (`scripts/governance-state-guard.sh --check-tracked`)
