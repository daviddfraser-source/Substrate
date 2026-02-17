# Authorization Model: RLS-first with app policy orchestration

## Enforcement hierarchy
- **Primary enforcement**: Postgres Row-Level Security policies defined per table/role. Every template migration includes an `.sql` patch that installs the RLS policy, and the `lib/db/policies` folder contains declarative JSON mapping for each permission set.
- **Secondary enforcement**: Application-layer policy checks live in `lib/auth/policy.ts` and wrap view visibility plus UI actions; these checks log allowed/denied attempts but never substitute for RLS.

## Policy module contract
- `PermissionContext` collects `userId`, `role`, `orgId`, and optional `featureFlags`.
- `defineAbilities(context)` returns CASL-like abilities (`can`, `cannot`) referencing resource strings (`article:create`, `comment:update`).
- `assertCan(action, resource)` is a helper that both throws if unauthorized and records audit context for evaluation harnesses.
- UI components import `lib/auth/policy` helpers to gate button rendering and action invocation.

## Role-to-data mapping
- Standard roles: `reader`, `editor`, `admin`, `support`.
- Each role maps to a Supabase policy partial that restricts access by ownership, org membership, and handle alias (via `user_handle` column).
- `lib/db/policies/ability-map.json` centralizes the mapping and is used to generate CASL `Ability` objects plus SQL exports.

## Denials & audit
- Every RLS policy returns `allow`/`deny` booleans in the policy map; `assertCan` logs failure events to `logs/ai-substrate/policy-denials.log`.
- Denial behavior is documented in `docs/codex-migration/ai-substrate/policy-failures.md`, including the UI-level message bundle and how to map to HTTP 403 responses.

## References
- `docs/codex-migration/ai-substrate/data-layer-adr.md`
- Supabase RLS best practices
