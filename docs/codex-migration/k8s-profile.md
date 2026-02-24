# Kubernetes Deployment Profile

Date: 2026-02-24
Packet: PRD-6-2

## Assets

- `infra/k8s/deployment.yaml`
- `infra/k8s/service.yaml`
- `infra/k8s/servicemonitor.yaml`

## Probe and Metrics Contract

- readiness/liveness probes: `/health`
- metrics scrape endpoint: `/metrics`

## Mode-specific Configuration

- Production profile sets `APP_ENV=production`
- `DATABASE_URL` is sourced from Kubernetes secret

## Validation

- `python3 -m unittest tests/test_k8s_profile.py`
