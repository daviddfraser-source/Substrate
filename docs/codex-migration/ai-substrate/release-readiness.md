# Release Readiness & Hardening

## Scope Reviewed
- Scaffold template (`templates/ai-substrate`)
- Quality gates (`docs/.../quality-gates.md`, `.github/workflows/ai-substrate-validation.yml`)
- AI harness (`scripts/run-ai-eval.py`, `reports/ai-substrate-eval.json`, `docs/codex-migration/ai-substrate/eval-history`)

## Hardening checklist
| Area | Status | Notes |
|------|--------|-------|
| Security | ✅ | RLS-first doc covers policies; `lib/auth/policy.ts` is auditable. |
| Performance | ⚠️ | Template relies on Prisma + Supabase pooling; must configure `POOL_CONNECTION_LIMIT` per deployment. |
| Developer Experience | ✅ | Scripts + docs provide context; typed bundles reduce hallucinations. |

## Residual risks
- Supabase connection pooling requires manual credential updates; document in `docs/architecture.md`.
- Prisma migrations may diverge if `schema.prisma` is edited without generating `prisma_client`.
- Template currently uses stub `components/ui/button.tsx`; real production UI needs theming updates.

## Contract history
- `docs/codex-migration/ai-substrate/contract-changelog.md` records ontology changes through `scripts/contract-log-entry.sh`; keep it aligned with pulled releases.

## Next actions
1. Update `.github/workflows/ai-substrate-validation.yml` to publish badge once real CI is in place.
2. Run `scripts/run-ai-eval.py` after major schema changes and checkpoint `reports/ai-substrate-eval.json`, then call `scripts/ai-eval-publish.js` to stamp the history folder.
3. Communicate adoption playbook to teams and gather feedback in release retro notes.
