# pr-review-automation

## Purpose
Provide consistent PR feedback over changed lines using Reviewdog-compatible input.

## Inputs
- Git diff context
- Lint or check output in Reviewdog format (or converted to it)

## Outputs
- `docs/codex-migration/skills/pr-review-report.md`

## Preconditions
- `reviewdog` installed on PATH.

## Workflow
1. Run smoke check for Reviewdog availability.
2. Build changed-file list.
3. Execute Reviewdog in local mode or CI mode.
4. Save review summary artifact.

## Commands
```bash
./skills/pr-review-automation/scripts/smoke.sh
./skills/pr-review-automation/scripts/run.sh
```

## Failure Modes and Fallbacks
- `reviewdog` missing: install binary before run.
- No diff context: fallback to base branch `origin/main`.

## Validation
- Review summary file exists.
- Non-zero exit on review execution failure.

## Evidence Notes Template
`Evidence: docs/codex-migration/skills/pr-review-report.md`

## References
- https://github.com/reviewdog/reviewdog
