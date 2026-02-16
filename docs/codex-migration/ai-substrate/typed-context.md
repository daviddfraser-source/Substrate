# Typed Context for AI Agents

Agents should read the following files first when editing the template:

1. `templates/ai-substrate/prisma/schema.prisma` – canonical data model, relationships, field constraints, and Prisma generator metadata.
2. `templates/ai-substrate/lib/validation/env.ts` – defines the Zod schema that all environment variables must satisfy. Agents should update both the schema and `docs/codex-migration/ai-substrate/quality-gates.md` when this file changes.
3. `templates/ai-substrate/lib/db/adapter.ts` and `templates/ai-substrate/lib/db/client.ts` – show how the Prisma client is instantiated and the adapter seam is exposed. Use `createAdapter` to swap ORMs in future.
4. `templates/ai-substrate/lib/auth/policy.ts` – describe the shape of permission contexts and the `defineAbilities`/`assertCan` helpers.
5. `templates/ai-substrate/components/ui/button.tsx` – provides a live, editable UI primitive that always ships with the template.

## Context Bundle

Agents should produce a mini-bundle before making changes:
- `context/schema.md`: brief summary of `schema.prisma` field names/types.
- `context/actions.md`: list of API endpoints and their Zod validators.
- `context/policies.md`: table mapping roles to allowed actions (derived from `lib/auth/policy.ts`).

## Example Flow

1. Update Prisma schema.
2. Run `npx prisma generate`.
3. Update `lib/validation/env.ts` if new env vars are needed.
4. Adjust UI components, referencing the adapter seam files if touching data access.
5. Regenerate typed context bundle (scripts should report which files changed).

## Supporting files

- `docs/codex-migration/ai-substrate/typed-context-index.json` (see next section)
