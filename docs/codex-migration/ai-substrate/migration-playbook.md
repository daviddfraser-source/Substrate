# Migration & Adoption Playbook

## Migration tracks
- **Greenfield**: Start from `templates/ai-substrate`; follow `scaffold-package.md` and `quality-gates.md`.
- **Incremental**: Adopt adapter seam first by copying `templates/ai-substrate/lib/db` and `lib/auth` into the existing project; update imports.
- **Policy-only**: Keep UI stack but adopt `docs/codex-migration/ai-substrate/authz-model.md` and `lib/auth/policy.ts`.

## Decision matrix
| Project type | Priority | Recommended track | Notes |
|--------------|----------|-------------------|-------|
| Internal tool | High | Greenfield or Incremental | Type safety prioritized |
| Enterprise SaaS | Medium | Policy-only | Keep existing compliance stack |
| Legacy CLI | Low | Policy-only + minimal data adapter | Use docs to sync limited features |

## Rollback strategy
1. Keep git branches for each track with `migration/ai-substrate` prefix.
2. Use `reports/ai-substrate-eval.json` as baseline; revert to last green state if evaluation fails.
3. For schema changes, keep `prisma/migrations/*.sql` under review; rollback by reapplying previous migration with `prisma migrate resolve`.

## Checklist
1. Review `docs/codex-migration/ai-substrate/typed-context.md`.
2. Ensure `schema.prisma` and `lib/validation/env.ts` match target project.
3. Run `scripts/preflight-checks.sh`.
4. Confirm AI agents can access new context bundle (`typed-context-index.json`).
5. Document residual risks and owners in `docs/codex-migration/ai-substrate/release-readiness.md`.
