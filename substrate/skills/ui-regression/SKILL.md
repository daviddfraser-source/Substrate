# ui-regression

## Purpose
Run Playwright critical-path checks for the WBS and packet viewer UX.

## Inputs
- Running dashboard server URL (`UI_BASE_URL`, default `http://127.0.0.1:8090`)

## Outputs
- `docs/codex-migration/skills/ui-regression-report.md`
- Playwright artifacts under `docs/codex-migration/skills/ui-regression/`

## Preconditions
- `node` and `npx` available.
- Playwright executable available (`npx playwright`).
- Dashboard server running.

## Workflow
1. Smoke-check Playwright availability.
2. Run critical-path tests.
3. Save report and artifacts.

## Commands
```bash
./skills/ui-regression/scripts/smoke.sh
./skills/ui-regression/scripts/run.sh
```

## Failure Modes and Fallbacks
- Server unavailable: fail with explicit base URL guidance.
- Playwright missing: install `@playwright/test`.

## Validation
- Report file exists.
- At least one critical-path test executed.

## Evidence Notes Template
`Evidence: docs/codex-migration/skills/ui-regression-report.md`

## References
- https://github.com/microsoft/playwright
