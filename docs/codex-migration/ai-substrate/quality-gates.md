# Quality Gates & Guardrails

## CI workflow
- Runs on push/PR targeting `main`.
- Steps: checkout, install dependencies, `npm run lint`, `npm run typecheck`, `npm run test`, `npx prisma generate`, `npm run schema:push --preview-feature`.
- All steps must pass before merge; the workflow file is `.github/workflows/ai-substrate-validation.yml`.

## Local pre-flight
- `scripts/preflight-checks.sh` (or `npm run test`) replicates the CI sequence.
- Failure logs include `logs/ai-substrate/preflight.log`.

## Drift detection
- `docs/codex-migration/ai-substrate/typed-context-index.json` lists canonical files. Updates to these need corresponding diffs in `docs/codex-migration/ai-substrate/quality-gates.md`.
- Policy drift: update `lib/auth/policy.ts` and `lib/db/adapter.ts` simultaneously; `scripts/policy-drifts.sh` documents this.

## Policy failure playbook
- On guardrail failure, include the log path plus the relevant doc (e.g., `docs/codex-migration/ai-substrate/policy-failures.md`) in the issue description.
