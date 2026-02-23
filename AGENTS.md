# AGENTS.md

## Purpose
Operating contract for Codex sessions in this repository.

Constitutional authority: `constitution.md` (invariant governance rules).

Use this file as executable governance, not background documentation.
- It defines how work is planned, executed, validated, and closed.
- It should be referenced at session start, before major execution, and at closeout.
- If instructions conflict, user instruction wins, then this file, then defaults.
- For governance-rule interpretation conflicts across repo docs, `constitution.md` takes precedence.
- For fast new-chat bootstrap, use `START.md`.

## How To Use This File
- New project initialization (day-0):
  - run `substrate/scripts/init-scaffold.sh substrate/templates/wbs-codex-minimal.json`
  - verify `python3 substrate/.governance/wbs_cli.py ready` returns the expected first packet
  - begin lifecycle with `claim` -> `done --risk none` -> `note`
- At session start:
  - run `python3 substrate/.governance/wbs_cli.py briefing --format json` and review summary before claiming
  - confirm active WBS scope and ready packet(s)
  - after claim, load packet context with `python3 substrate/.governance/wbs_cli.py context <packet_id> --format json`
  - confirm owner and expected output artifact
- During execution:
  - follow packet lifecycle (`claim` -> execute -> `done`/`fail` -> `note`)
  - if session transfer is required, use governed continuity commands (`handover` -> `resume`)
  - keep evidence paths current in packet notes
- At closeout:
  - provide full delivery report in chat
  - record Level-2 drift assessment via `closeout-l2` when applicable

## WBS Execution Rules
- Use `substrate/.governance/wbs_cli.py` (or the equivalent MCP server tools) as the source of truth for packet lifecycle updates.
- Do not create or modify packets unless explicitly requested by the user.
- Prefer explicit commands over assistant-specific slash commands.
- Use `substrate/.governance/packet-schema.json` as the canonical packet content schema.
- Use `substrate/.governance/agents.json` for declared agent capability profiles and enforcement mode.
- Ensure packet definitions include required governance fields (not only title/scope).
- Packet viewer behavior should present the full packet object plus runtime state.

## Execution Discipline (Latest Practice)
- One packet at a time per agent unless user requests parallelization.
- Execute only the scoped packet intent; do not silently expand scope.
- If uncertain, prefer a short clarifying check before changing governance state.
- Every completion claim must include:
  - what changed
  - where the artifact lives
  - how it was validated

## Anti-Drift Controls
- Treat drift as expected risk in long-running agentic work.
- Control drift with:
  - explicit packet scope boundaries
  - evidence-linked completion notes
  - periodic status/log reconciliation (`status`, `log`)
  - Level-2 drift assessments at closeout
- For high-impact changes (governance, API contract, CI, security):
  - require test or command evidence in notes
  - capture residual risk and immediate next action

## Validation and Evals
- Prefer fast local validation before marking done.
- Minimum expectation for code/doc governance changes:
  - syntax/contract validation where relevant
  - impacted tests or smoke checks
- If validation is not run, say so explicitly in notes/report.
- For non-deterministic agent workflows, prefer repeatable eval scripts and persisted reports.

## Required Delivery Reporting
- If the user asks for a WBS delivery report (for a phase, area, or specific WBS ref), output a full report directly in chat.
- A full report must include:
  - Scope covered (for example: `WBS 1.0`, `1.1-1.5`)
  - Completion summary (`done/in_progress/pending/failed/blocked`)
  - Per-packet status lines including packet ID, title, owner, start/completion timestamps, and completion notes
  - Evidence source references (`substrate/.governance/wbs-state.json` and recent log entries)
  - Risks/gaps and immediate next actions
- Do not return only a single aggregate count when a full report is requested.

## Closeout Expectations
- After execution steps, report exactly what changed and what remains.
- If an action was requested but not executed, state that clearly.
- Level-2 WBS closeout (for example `1.0`, `2.0`) requires a drift assessment recorded via:
  - `python3 substrate/.governance/wbs_cli.py closeout-l2 <area_id|n> <agent> <drift_assessment.md> [notes]`
- `closeout-l2` is valid only when all packets in that Level-2 area are `done`.
- Use `substrate/docs/drift-assessment-template.md` as the default template for closeout docs.
- Drift assessment file naming convention:
  - `substrate/docs/codex-migration/drift-wbs<N>.md` (for area `<N>.0`)
- Drift assessment documents must include:
  - `## Scope Reviewed`
  - `## Expected vs Delivered`
  - `## Drift Assessment`
  - `## Evidence Reviewed`
  - `## Residual Risks`
  - `## Immediate Next Actions`
- Cryptographic hashing is not required for drift assessments in this system.

## Decision and Escalation Rules
- If blocked:
  - mark packet `failed` with clear reason and dependency impact
  - do not fabricate completion
- If behavior differs from expected contract:
  - document the gap
  - propose concrete corrective action
- If action requested was not executed:
  - state it directly in closeout report

## Operational Hygiene
- Keep commands and examples copy-pasteable.
- Keep governance docs aligned with actual CLI/API behavior.
- Use stable file paths for evidence to keep packet viewer useful.
- Keep `substrate/docs/governance-workflow-codex.md` aligned with current CLI behavior.

## Packet Standard
- Canonical schema: `substrate/.governance/packet-schema.json`
- Human-readable standard and examples: `substrate/docs/codex-migration/packet-standard.md`

## Claude Code Agents
- Claude Code sessions must follow the same CLI-governed lifecycle as any other agent.
- Preferred execution identity: `claude` (or explicit variants like `claude-1` for multi-agent scenarios).
- Claude should not modify `substrate/.governance/wbs-state.json` directly; all lifecycle changes go through `substrate/.governance/wbs_cli.py`.
- Claude should not claim multiple packets without explicit user approval.
- Claude should collect file-level evidence and validation results before `done`.
- Claude-specific usage guidance lives in:
  - `CLAUDE.md`
  - `.claude/skills/*`
  - `substrate/docs/claude-code-guide.md`

## Gemini Agents
- Gemini sessions must follow the same CLI-governed lifecycle as any other agent.
- Preferred execution identity: `gemini`.
- Gemini should not modify `substrate/.governance/wbs-state.json` directly; all lifecycle changes go through `substrate/.governance/wbs_cli.py`.
- Gemini should not claim multiple packets without explicit user approval.
- Gemini should collect file-level evidence and validation results before `done`.
- Gemini-specific usage guidance lives in:
  - `GEMINI.md`
  - `substrate/scripts/gc-*`

## Codex Agents
- Codex sessions must follow the same CLI-governed lifecycle as any other agent.
- Preferred execution identity: `codex` (or explicit variants like `codex-1` for multi-agent scenarios).
- Codex should not modify `substrate/.governance/wbs-state.json` directly; all lifecycle changes go through `substrate/.governance/wbs_cli.py`.
- Codex should not claim multiple packets without explicit user approval.
- Codex should collect file-level evidence and validation results before `done`.
- Codex-specific usage guidance lives in:
  - `codex.md`
  - `substrate/docs/governance-workflow-codex.md`
- Cross-agent references:
  - `CLAUDE.md`
  - `GEMINI.md`

## Ralph Wiggum Self-Check

The Ralph Wiggum method is a lightweight pre-action self-check run at governance state
mutation boundaries (`claim` and `done`). It is the behavioural implementation of
`constitution.md` Article I §3 — scope clarification — applied consistently rather than
only when things are obviously ambiguous.

The goal is to say what you actually know and don't know, plainly, before acting.
*Note: Depending on the agent's integration (e.g., Gemini via MCP), this check may be automated programmatically via skills (like `auto-done`) rather than narrated.*

### Pre-Claim Check (Mental or Narrated)
Before running `claim`, answer:
1. **What does `required_actions` say I must do?** 
2. **What am I assuming that isn't written there?**
3. **Is there any ambiguity?** If yes — ask the user before claiming.
4. **Which files will I touch?** 

### Pre-Done Check (Mental or Narrated)
Before running `done`, confirm:
1. **What file(s) did I change or create?** 
2. **What validation did I run?** 
3. **Does my evidence string capture all of the above?** If not, rewrite it first.

For agent-specific implementations or tools regarding this check, see the individual
integration guides (`CLAUDE.md`, `GEMINI.md`).
