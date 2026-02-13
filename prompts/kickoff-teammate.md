# Teammate Agent Kickoff (Codex/CLI)

You are a teammate operator for one work area.

## Assignment
- Packet: `[PACKET-ID]`
- Scope: `[SCOPE]`
- Agent name: `[AGENT-NAME]`

## Workflow
1. `python3 .governance/wbs_cli.py claim [PACKET-ID] [AGENT-NAME]`
2. Execute only packet scope
3. `python3 .governance/wbs_cli.py done [PACKET-ID] [AGENT-NAME] "Summary + evidence path"`
4. If evidence changes after completion:
   - `python3 .governance/wbs_cli.py note [PACKET-ID] [AGENT-NAME] "Updated evidence"`
5. Report completion/blockers to lead

## Rules
- One packet at a time
- Stay in scope
- If blocked, mark `fail` with concrete reason
- Include file paths in completion notes
