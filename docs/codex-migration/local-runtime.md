# Local Runtime and SQLite Fallback

Date: 2026-02-24
Packet: PRD-6-1

## Local Deployment Assets

- `docker-compose.yml`
- `Dockerfile`
- `.env.example`

## Environment Validation

Runtime config loader in `src/app/runtime_config.py` enforces:

- `DATABASE_URL` required in production
- accepted DB schemes: `postgresql://` or `sqlite:///`
- SQLite fallback is auto-selected when DB URL is not provided in dev/local profiles

## SQLite Fallback

Default fallback path:

- `./data/substrate-dev.db`

Generated runtime URL when unset:

- `sqlite:///./data/substrate-dev.db`

## Validation

Run:

- `python3 -m unittest tests/test_runtime_config.py`
