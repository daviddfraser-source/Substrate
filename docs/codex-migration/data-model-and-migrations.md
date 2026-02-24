# Data Model and Migration Baseline

Date: 2026-02-24
Packet: PRD-3-1

## Core Entities

The baseline includes all PRD-required entities:

- Tenant
- User
- Role
- Project
- Packet
- Dependency
- Risk
- AuditEntry
- AgentIdentity
- APIKey
- MetricEvent
- OptimizationProposal
- RuleVersion
- PerformanceSnapshot
- ImprovementImpactReport

Canonical registry: `src/app/data/entities.py`.

## Migration Strategy

- Primary migration artifacts: `src/app/data/migrations/*.sql`
- SQLite fallback runner: `src/app/data/migrate.py` (`apply_sqlite_migrations`)
- Alembic compatibility marker: `src/app/data/alembic_stub.py`

The SQL avoids SQLite-only `AUTOINCREMENT` so migration scripts remain portable to PostgreSQL-oriented migration tooling.

## Validation

- Run `python3 -m unittest tests/test_data_migrations.py`
- Confirms schema bootstrap in SQLite
- Confirms table coverage and entity registry completeness
