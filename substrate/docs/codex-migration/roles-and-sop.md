# Lead and Teammate SOP (Codex)

## Lead
- Initialize and verify WBS state.
- Assign or direct next packet based on `ready` output.
- Require packet notes with artifact evidence path.
- Request full delivery report on phase completion.
- Require `closeout-l2` with drift assessment before declaring any Level-2 area complete.
- Enforce validation evidence for high-impact changes (governance, API, CI, security).

## Teammate
- Claim one packet at a time.
- Execute only packet scope.
- Mark done/failed with concise evidence note.
- Report blockers early with packet ID and constraint.
- If validation is not run, state that explicitly in notes/report.

## Packet Lifecycle
1. `ready`
2. `claim <id> <agent>`
3. execute scoped work
4. `done` or `fail`
5. `note` if evidence updates are needed post-completion
6. For completed Level-2 areas: `closeout-l2 <area_id|n> <agent> <drift_assessment.md> [notes]`

## Execution Discipline
- One packet at a time per agent unless explicitly directed otherwise.
- Do not silently expand packet scope.
- Include in completion: what changed, artifact path, validation performed.

## Anti-Drift Controls
- Reconcile `status` and `log` regularly during long runs.
- Keep evidence paths stable and repository-relative.
- Capture residual risks and immediate next actions in reports.

## Escalation Rules
- If blocked, use `fail` with clear dependency impact.
- If requested action was not executed, state it explicitly in closeout report.

## Evidence Standard
- Include artifact path(s) in packet notes.
- Include validation command(s) if relevant.
- Drift assessments must use the required sections from `docs/codex-migration/drift-assessment-template.md`.
