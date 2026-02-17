# precommit-governance Skill Operation

## Local
```bash
pip install pre-commit
./skills/precommit-governance/scripts/smoke.sh
./skills/precommit-governance/scripts/install.sh
./skills/precommit-governance/scripts/run.sh
```

## CI
- Job: `skills-precommit-governance`
- Installs pre-commit and runs smoke/install/run.

## Evidence
- `.pre-commit-config.yaml`
- Hook execution output from `pre-commit run --all-files`
