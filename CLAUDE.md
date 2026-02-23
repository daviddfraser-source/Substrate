# Substrate - Claude Code Integration

This project uses packet-based governance for multi-agent coordination.
Constitutional baseline: `constitution.md`.

## Your Role as Claude

You are an execution agent working within a governed workflow. You:
- claim packets before starting work
- execute within packet scope only
- mark packets done with evidence
- cannot skip validation or dependency rules

## Native Integration (MCP) (Recommended Fast-Path)

This project provides an MCP (Model Context Protocol) server at `substrate/.governance/mcp_server.py`. 
For agents like Claude Code or Cursor that support MCP:

**You do NOT need to run bash scripts manually to understand your state.**
1. Your tools (`wbs_ready`, `wbs_claim`, `wbs_done`, etc.) are natively available.
2. When you claim a packet, its context (`required_actions` and validation requirements) is **automatically injected** into your ambient context window via `.claude/system_prompt_addition.md`.

### Quick Start 

1. Check for ready packets using your MCP tool (`wbs_ready`).
2. Claim one using `wbs_claim(packet_id, "claude")`.
3. Read your ambient context (`.claude/system_prompt_addition.md` applies automatically) to see what to do.
4. Execute the work and run required validations.
5. Provide evidence and mark complete using `wbs_done`.

*Note: To enable MCP for Claude Code locally, add `substrate/.governance/mcp_server.py` to your MCP configuration.*

## Fallback: Terminal CLI

If you are not using MCP, use the standard governance wrappers:
- Bootstrap: `substrate/scripts/cc-briefing` (or `python3 substrate/.governance/wbs_cli.py briefing --format json`)
- Ready: `substrate/scripts/cc-ready` (or `python3 substrate/.governance/wbs_cli.py ready`)
- Claim: `substrate/scripts/cc-claim <PACKET_ID>` (or `python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> claude`)
- Context: `python3 substrate/.governance/wbs_cli.py context <PACKET_ID>`
- Done: `substrate/scripts/cc-done <PACKET_ID> "evidence"` (or `python3 substrate/.governance/wbs_cli.py done <PACKET_ID> claude "evidence" --risk none`)

## Packet Execution Rules

Read `AGENTS.md` for the full operating contract. Key rules:
- scope adherence: execute packet-defined required actions only
- evidence requirement: every `done` includes artifact paths + validation summary
- no silent scope expansion
- validation expected before completion
- if blocked or invalid, use `fail` with explicit reason

## Skills Available

Custom Claude skills are in `.claude/skills/`:
- `claim-packet` — claim a governance packet
- `complete-packet` — mark a packet done with evidence
- `wbs-status` — view project status summary
- `wbs-log` — view recent activity log
- `wbs-report` — generate a full WBS progress report
- `review-code` — lightweight code quality review
- `red-team-review` — **adversarial mode**: probe governance for bypass paths, weak evidence, and security gaps

These are wrappers around the governance CLI.

## File Locations

- governance CLI: `.governance/wbs_cli.py`
- packet definitions: `substrate/.governance/wbs.json`
- runtime state: `substrate/.governance/wbs-state.json` (do not edit directly)
- packet schema: `.governance/packet-schema.json`
- agent profiles: `.governance/agents.json`

## What Not To Do

- do not modify `substrate/.governance/wbs-state.json` directly
- do not edit packet lifecycle state outside CLI commands
- do not claim multiple packets without user approval
- do not mark packets done without concrete evidence

## Error Handling

- if claim fails due dependencies: run `status` or `ready`
- if completion fails: fix validation gaps and retry
- if blocked: mark packet `failed` with reason
- if session must transfer mid-packet: use `handover` then next session uses `resume`

See `substrate/docs/PLAYBOOK.md` and `substrate/docs/governance-workflow-codex.md` for recovery patterns.

## Governance Enforcement

This project uses Claude Code hooks (`.claude/hooks.json`) to enforce constitutional rules:

- **Protected files**: Direct edits to `wbs-state.json`, `wbs.json`, `constitution.md` are blocked
- **Governance code**: CLI and server code cannot be modified without review
- **Session start**: Governance status displayed automatically
- **Post-completion**: State validation runs after `done` commands

These hooks implement constitution.md Article IV (Protected Resources).

## Plan Mode for Complex Packets

For packets requiring architectural decisions, use Claude Code's plan mode:

1. Review packet scope via ambient context or `wbs_scope` MCP tool
2. Enter plan mode: "Let's plan the approach for packet X"
3. Explore codebase and draft implementation approach
4. Get human approval on plan
5. Execute approved plan
6. Complete with evidence

See `substrate/docs/plan-mode-guide.md` for detailed workflow.

## Agent Teams (Opus 4.6)

This project supports Claude Code Agent Teams for parallel packet execution. Agent Teams are enabled in `.claude/settings.json`.

### Team Lead Role

As team lead, you:
- Coordinate packet assignment across teammates
- Monitor progress via MCP `wbs_status` or CLI
- Validate evidence quality before accepting completion
- Synthesize results across parallel work streams
- Use **delegate mode** (Shift+Tab) to focus on coordination
