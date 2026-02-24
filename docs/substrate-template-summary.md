# Substrate Template Summary

## Purpose
The Substrate template is a production-ready application shell for governance-driven delivery. It combines enterprise app scaffolding with deterministic governance controls so teams can launch faster while maintaining auditability and role-based control.

The scaffolded app layer is optional: teams can adopt the full template or only the modules they need.

## How to Use the Template

1. Start the stack and open the template UX.
2. Navigate through the left menu:
   - `Development > Instruction Guide` for operating guidance.
   - `Development > Template Architecture` for system structure.
   - `Development > WBS Manager` for governed packet execution.
3. Execute work using packet lifecycle discipline:
   - claim -> execute -> done/fail -> note.
4. Attach evidence and validation output when completing packets.
5. Use closeout only when all scoped packets are complete.

## Governance Principles
- Deterministic governance first.
- Backend-enforced RBAC.
- Auditability by default.
- Observability before optimization.
- Bounded, reviewable recursion only.
- No autonomous self-modification.

## Template Architecture Overview

### Frontend
- Next.js (App Router) + TypeScript.
- AG Grid as the primary WBS/data interaction surface.
- TanStack Query for server data flows.
- Local state management via Zustand.
- Dependency graph integration (D3/Cytoscape).

### Backend
- FastAPI API layer with OpenAPI documentation.
- SQLAlchemy ORM and Alembic migrations.
- PostgreSQL primary storage, SQLite dev fallback.
- JWT/OIDC auth support.
- RBAC middleware and structured logging.

### Infrastructure
- Docker and docker-compose for local deployment.
- Kubernetes-ready deployment model.
- Health and metrics endpoints for observability.
- Optional Redis for caching.

## Included Capability Modules
- Authentication and profile/session flow.
- Role and tenant administration.
- WBS/packet management and dependency tracking.
- Risk register.
- Immutable audit viewer.
- Agent registration, API keys, and action logging.
- Telemetry capture and proposal-based recursive improvement.

## Key Endpoints (Representative)
- `/auth`, `/tenants`, `/users`, `/roles`
- `/projects`, `/packets`, `/dependencies`, `/risks`
- `/audit`, `/agents`, `/metrics`, `/proposals`

## Deployment Modes
- Local Docker development.
- Single-node production.
- Kubernetes cluster.
- Air-gapped mode.

Recursive engine behavior must be tenant-configurable and approval-gated.
