# AI Task Evaluation Harness

## Purpose
Measure how reliably AI agents complete representative tasks (create-item, auth-check, schema change).

## Task scenarios
1. **CRUD scenario**: Agent modifies `templates/ai-substrate/app/page.tsx` to add a featured item, runs `npm run test`, ensures build passes.
2. **Authorization scenario**: Agent updates `lib/auth/policy.ts`, runs `scripts/eval-policy.js`, ensures no policy violations are reported.
3. **Schema change scenario**: Agent adds a field to `schema.prisma`, runs `npx prisma generate`, updates `lib/data/items.ts`, and reruns `npm run test`.

## Scoring rubric
- Pass/fail recorded in `reports/ai-substrate-eval.json`.
- Each scenario yields `success: true/false`, `duration`, and `notes`.
- A minimum of 2/3 passing scenarios keeps the template in `ai-substrate/green-status.md`.

## Reporting
- `scripts/run-ai-eval.py` runs the scenarios and writes JSON results.
- Use `reports/ai-substrate-eval.json` as source for release readiness and gating documentation.
