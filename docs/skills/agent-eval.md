# agent-eval Skill Operation

## Purpose
Detect agent behavior drift with repeatable Promptfoo evaluation runs.

## Local Workflow
```bash
npm install -g promptfoo
./skills/agent-eval/scripts/smoke.sh
./skills/agent-eval/scripts/run.sh
```

## CI Workflow
- GitHub Actions job: `skills-agent-eval-smoke`
- Installs Node + Promptfoo and runs `smoke.sh`.

## Evidence Artifact
- `docs/codex-migration/skills/agent-eval-report.md`
