# Migration Release Bundle Contents

Build command:
```bash
./scripts/build-release-bundle.sh
```

Bundle includes:
- Operator contract: `AGENTS.md`
- Entry docs: `README.md`, `CLAUDE.md`
- Core engine: `.governance/wbs_cli.py`, `.governance/wbs_server.py`
- Dashboard UI: `.governance/static/index.html`
- Codex migration WBS template: `templates/wbs-codex-refactor.json`
- Operator utilities: `scripts/`
- Prompt pack: `prompts/`
- Migration docs: `docs/codex-migration/`
- Recovery/operations docs: `docs/PLAYBOOK.md`, `docs/TEAM_PATTERNS.md`, `docs/CRITICAL_APP_EXECUTION_CHECKLIST.md`

Intended use:
- Hand-off package for teams adopting CLI-first Codex workflow.
