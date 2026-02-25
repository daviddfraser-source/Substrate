# Phase 5 Packet P5-09: Infra Observability + Docker Deployment Runbook

## What This Packet Delivers
- Structured logging + trace primitives and readiness/liveness endpoints in app operations layer
- Docker-first reproducible profile for API/worker + Postgres + Redis + observability stack
- Local observability configuration for OpenTelemetry Collector and Prometheus

## Artifacts
- `src/app/api/operations.py`
- `src/app/api/contracts.py`
- `Dockerfile`
- `docker-compose.observability.yml`
- `infra/observability/otel-collector.yaml`
- `infra/observability/prometheus.yml`
- `tests/test_operations_endpoints.py`
- `tests/test_api_contracts.py`
- `tests/test_infra_observability_deploy.py`

## Local Bring-Up
```bash
docker compose -f docker-compose.observability.yml up --build
```

## Runtime Endpoints
- API: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/admin)

Health and observability endpoints expected from contract:
- `/health`
- `/readyz`
- `/livez`
- `/metrics`
- `/traces`

## Validation Command
```bash
python3 -m unittest tests/test_operations_endpoints.py tests/test_api_contracts.py tests/test_infra_observability_deploy.py
```

## Notes
- This packet provides local/developer observability profile and contract-level endpoints.
- Production-grade scraping, retention, and alerting tuning should be layered in environment-specific deployment configs.
