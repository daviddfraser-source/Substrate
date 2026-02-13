# Tests

## Run all tests

```bash
python3 -m unittest discover -s tests -v
```

## Core suites

- `test_cli_contract.py`: lifecycle contract behavior
- `test_cli_e2e.py`: dependency and failure propagation
- `test_server_api.py`: dashboard/API contract behavior
- `test_start_validate.py`: scaffold validation and launcher behavior

## Fixtures

- `tests/fixtures/wbs_linear.json`: minimal linear dependency fixture
- `tests/fixtures/wbs_dag.json`: multi-step dependency fixture

Use fixtures for deterministic regression tests instead of ad-hoc inline payloads when possible.
