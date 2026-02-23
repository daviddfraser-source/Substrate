# precommit-governance

## Purpose
Enforce WBS governance and docs checks before commit using pre-commit hooks.

## Inputs
- Repository files
- Hook config template at `skills/precommit-governance/assets/pre-commit-config.yaml`

## Outputs
- Active `.pre-commit-config.yaml`
- Optional run report in terminal output

## Preconditions
- `pre-commit` installed on PATH.
- Shell scripts are executable.

## Workflow
1. Install/configure pre-commit template.
2. Install hooks.
3. Run hooks across repository.
4. Record evidence command and status in packet notes.

## Commands
```bash
./skills/precommit-governance/scripts/smoke.sh
./skills/precommit-governance/scripts/install.sh
./skills/precommit-governance/scripts/run.sh
```

## Failure Modes and Fallbacks
- `pre-commit` missing: install via pipx/pip.
- Hook failure: remediate and re-run.

## Validation
- `.pre-commit-config.yaml` exists in repo root.
- `pre-commit run --all-files` exits 0 for compliant repo state.

## Evidence Notes Template
`Evidence: .pre-commit-config.yaml, command output from pre-commit run --all-files`

## References
- https://github.com/pre-commit/pre-commit
