# agent-eval

## Purpose
Run repeatable agent behavior evaluations using Promptfoo to detect drift across prompts, tools, and workflow changes.

## Inputs
- Evaluation config: `skills/agent-eval/assets/promptfooconfig.yaml`
- Optional env vars for model/provider credentials supported by Promptfoo

## Outputs
- Markdown summary: `docs/codex-migration/skills/agent-eval-report.md`
- Raw output directory: `docs/codex-migration/skills/agent-eval-results/`

## Preconditions
- `promptfoo` installed and available on PATH.
- Repository has prompts/tests represented in the Promptfoo config.

## Workflow
1. Run smoke check to verify `promptfoo` availability.
2. Execute the eval run script.
3. Review generated score summary and failing cases.
4. Add report path(s) to packet evidence notes.

## Commands
```bash
./skills/agent-eval/scripts/smoke.sh
./skills/agent-eval/scripts/run.sh
```

## Failure Modes and Fallbacks
- `promptfoo` missing: install via `npm i -g promptfoo` or local dev dependency.
- Provider credentials missing: run with local/mock provider configuration first.

## Validation
- `agent-eval-report.md` exists with run timestamp and pass/fail summary.
- Non-zero exit from `run.sh` when eval execution fails.

## Evidence Notes Template
`Evidence: docs/codex-migration/skills/agent-eval-report.md`

## References
- https://github.com/promptfoo/promptfoo
