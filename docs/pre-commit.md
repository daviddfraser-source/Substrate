# Pre-commit Hooks (Optional)

Pre-commit is optional in this repository, but recommended for contributor hygiene.

## Install

```bash
pip install pre-commit
pre-commit install
```

## Run Manually

```bash
pre-commit run --all-files
```

## Included Checks

- JSON file integrity
- trailing whitespace / EOF normalization
- Python syntax check for core entry points
- WBS structure validation
- packet schema validation for template profile
- shell lint if `shellcheck` is installed

If `shellcheck` is not installed, shell lint step prints a skip message and continues.
