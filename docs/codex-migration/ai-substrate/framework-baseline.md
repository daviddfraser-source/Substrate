# Framework Baseline & Runtime Policy

## Supported Runtime
- **Next.js 16.2** (App Router) with incremental minor updates allowed only for security patches.
- **Node.js 20.x** (Active LTS) pinned to the current patch; update policy requires explicit ADR.
- Default `turbo` and `eslint` configs inherit from this repository to keep lint/format behavior stable.

## Structural Rules
- All UI logic defaults to **server components** unless React state or browser-only APIs are required.
- Server components live in `app/` subdirectories; client components add `"use client"` and end with `.client.tsx`.
- Each server action is co-located with the UI trigger inside `app`, and mutations must import `revalidatePath` from `next/cache` only when revalidation occurs.
- Lint gate enforces `eslint:recommended` plus custom rules (see `package.json` scripts) that flag hooks/state usage in server-only files.

## Caching & Data Strategy
- Data fetching defaults to `fetch` with `next/cache` and `{ next: { revalidate: 0 }}` for mutation-friendly behavior; caching is only for read-only pages.
- `app-router` pages needing persistent caching explicitly declare TTL in `route.ts` or `layout.tsx`; documentation describes how to opt out (`revalidate: 0`).
- Mutations use `Server Actions` with `no-cache` fetch options and explicit revalidation towards touched routes.

## Configuration Enforcement
- `next.config.js` enforces `experimental.serverActions = true`, strict TypeScript (`tsconfig.json` extends `./tsconfig.base.json`), and `output: "standalone"` for deployment alignment.
- Template `package.json` defines scripts `format`, `lint`, `typecheck`, `dev`, `start`, `build`, `preview`, and `schema:push` to keep Prisma migrations predictable.

## Decision Tracking
Documented decisions reference future `docs/codex-migration/ai-substrate/framework-baseline.md` and drive GitHub labels `ai-substrate`. Changes to these rules require ADR updates and go/no-go approvals recorded in `docs/codex-migration/drift-wbs6.md`.
