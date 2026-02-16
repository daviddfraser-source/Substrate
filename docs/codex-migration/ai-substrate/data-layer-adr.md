# Data Layer ADR: Prisma-First with adapter seam

## Context
The substrate relies on Supabase/PostgreSQL for persistence. Prisma offers the most concise single-source schema (`schema.prisma`) while generating fully typed clients for the frontend. Drizzle and other lighter ORMs are strong alternatives, but they disperse schema definitions across multiple TypeScript files, reducing signal in AI prompts.

## Decision
- **Primary ORM**: Prisma. `schema.prisma` resides at the repo root inside the template scaffold and is treated as the canonical data model.
- **Adapter seam**: All data access lives behind an explicit `lib/db` folder that exports a single `client` instance and adapter-specific helpers (`executeQuery`, `withTransaction`). Feature code imports from hooks such as `db.user.findMany()` rather than referencing Prisma clients directly.
- **Drizzle swap path**: The adapter exposes `lib/db/adapter.ts` implementing a typed `DatabaseAdapter` interface. A future switch to Drizzle only requires implementing the interface (`DrizzleAdapter` in the same folder) and toggling `lib/db/index.ts` to re-export the new adapter.
- **Connection strategy**: Always use `datasource db { provider = "postgresql" url = env("DATABASE_URL") }` with `statement_timeout = 5000` and `connect_timeout = 10`. Prisma clients share a singleton `prisma` instance guarded by `globalThis` in dev to avoid too many connections; production deployments use Supabase-managed pooling credentials (`pool_authorization_token`, `pool_host`, `pool_port`).

### Connection profile
- `DATABASE_URL` points to the Supabase database, optionally routed through the Supabase connection pooler.
- `SHADOW_DATABASE_URL` is required for migrations run locally and must follow the same type definitions.
- `POOL_CONNECTION_LIMIT` defaults to `5` in development and `25` in production; this value surfaces in `lib/db/client.ts` to configure Prisma and the adapter.

## Consequences
- The schema file becomes the AI context anchor; writing tests or queries starts from it.
- Adapter pattern enforces minimal Prisma surface area inside features, improving replaceability.
- Documented connection profile ensures operational consistency when teams copy the template.

## References
- Supabase official Postgres pooling guide
- Prisma singleton usage best practices
