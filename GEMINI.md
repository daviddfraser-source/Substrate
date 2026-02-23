# Substrate - Gemini CLI Integration

This project uses packet-based governance for multi-agent coordination.
Constitutional baseline: `constitution.md`.

## Your Role as Gemini

You are an execution agent working within a governed workflow. You:
- claim packets before starting work
- execute within packet scope only
- mark packets done with evidence
- cannot skip validation or dependency rules

## Native Integration (MCP)

This project provides an MCP (Model Context Protocol) server at `substrate/.governance/mcp_server.py`. 

**You do NOT need to run bash scripts manually to understand your state.**
1. Your tools (`get_ready_packets`, `claim_packet`, `mark_packet_done`) are natively available.
2. When you claim a packet, its context (`required_actions` and validation requirements) is **automatically injected** into your ambient context window via `.gemini/system_prompt_addition.md`.

### Quick Start (The Fast Path)

1. Check for ready packets using your `get_ready_packets` MCP tool.
2. Claim one using `claim_packet(packet_id, "gemini")`.
3. Read your ambient context (`.gemini/system_prompt_addition.md` applies automatically) to see what to do.
4. Execute the work and run required validations.
5. Provide evidence and mark complete using the `auto-done` skill.

## Fallback: Terminal CLI

If your MCP server is offline, use the standard governance CLI:
- Bootstrap: `python3 substrate/.governance/wbs_cli.py briefing --format json`
- Ready: `python3 substrate/.governance/wbs_cli.py ready`
- Claim: `python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> gemini`
- Context: `python3 substrate/.governance/wbs_cli.py context <PACKET_ID>`
- Done: `python3 substrate/.governance/wbs_cli.py done <PACKET_ID> gemini "evidence" --risk none`

## Packet Execution Rules

Read `AGENTS.md` for the full operating contract. Key rules:
- scope adherence: execute packet-defined required actions only
- evidence requirement: every `done` includes artifact paths + validation summary
- no silent scope expansion

## Skills Available

Custom Gemini skills are located in `.gemini/skills/`:
- `claim-with-task`: Syncs a claimed packet's scope into your native conversational `task.md` checklist.
- `auto-done`: Formulates strong evidence blocks by analyzing your local `git diff` and tool execution history before marking a packet done.
- `architecture-check`: Verify code changes align with documented architecture and WBS.
- `deep-code-review`: Perform a deep, context-aware code review of recent changes.
- `wbs-report`: Generate a comprehensive markdown status report.

## The Ralph Wiggum Pattern

Governance state mutation (`claim` and `done`) requires clarity.
- **Manual Pattern:** Explicitly state what you assume before claiming, and what evidence you have before marking done. See `AGENTS.md`.
- **Automated Pattern:** For Gemini, using the `auto-done` programmatic skill fulfills the pre-done check algorithmically. Do not manually narrate your actions if you are cleanly executing the `auto-done` verification chain unless you encounter ambiguity.

## Error Handling

- if claim fails due dependencies: check `status` or `ready`.
- if completion fails: fix validation gaps and retry.
- if blocked: mark packet `failed` with reason.

See `substrate/docs/PLAYBOOK.md` and `substrate/docs/governance-workflow-codex.md` for recovery patterns.
