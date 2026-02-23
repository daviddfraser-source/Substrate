# Scaffold Package Overview

## Key features
- Next.js 16 App Router with `app/layout.tsx` wrapped in a dark gradient shell.
- Server and client components split via `"use client"` directives; page-level fetches remain server-first.
- `app/api/items/route.ts` demonstrates typed `POST` route validated through `zod`.
- `lib/db/*` implements the Prisma adapter seam plus `db` client helper.
- `components/ui/button.tsx` contains a copy-pastable primitive (similar to Shadcn's style) for buttons.
- `lib/validation/env.ts` and `prisma/schema.prisma` provide strict contract definitions for environment and data models.

## Bootstrapping steps
1. `npm install && npx prisma generate`.
2. Update `.env` with Supabase credentials (`DATABASE_URL`, `SHADOW_DATABASE_URL`).
3. Run `npm run schema:push`, then `npm run dev`.
4. Follow `docs/codex-migration/ai-substrate/typed-context.md` for bridging the AI prompt context.
