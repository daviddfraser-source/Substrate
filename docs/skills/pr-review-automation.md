# pr-review-automation Skill Operation

## Purpose
Provide repeatable review automation over current PR diff context.

## Local
```bash
./skills/pr-review-automation/scripts/smoke.sh
./skills/pr-review-automation/scripts/run.sh
```

## CI
- Job: `skills-pr-review-smoke`
- Uses `reviewdog/action-setup@v1`
- Executes skill smoke + run scripts.

## Evidence Artifact
- `docs/codex-migration/skills/pr-review-report.md`
