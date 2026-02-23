# ui-regression Skill Operation

## Local
```bash
python3 .governance/wbs_server.py 8090
UI_BASE_URL=http://127.0.0.1:8090 ./skills/ui-regression/scripts/smoke.sh
UI_BASE_URL=http://127.0.0.1:8090 ./skills/ui-regression/scripts/run.sh
```

## CI
- Job: `skills-ui-regression`
- Installs Playwright + Chromium, starts dashboard server, runs smoke and test scripts.

## Evidence
- `docs/codex-migration/skills/ui-regression-report.md`
- `docs/codex-migration/skills/ui-regression/playwright.log`
