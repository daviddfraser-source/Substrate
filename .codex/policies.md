# Codex Execution Policies

These are Codex working conventions for this repository.
They do not override governance rules in `constitution.md` and `AGENTS.md`.

## Default Behavior

- One packet at a time unless the user explicitly requests parallel packet work.
- Keep diffs surgical and avoid unrelated file churn.
- Run the smallest relevant validation first, then broaden only if needed.
- Use explicit evidence strings: what changed, where, and how validated.

## Progress and Reporting

- Provide concise progress updates during longer implementation/testing loops.
- Report exact files changed and exact validation commands run.
- If a requested action was not executed, state it directly.

## Risk and Completion

- `done` requires evidence and risk acknowledgment.
- Use `--risk none` when no residual risk remains.
- Use `--risk declared --risk-file <path>` when residual risk exists.
