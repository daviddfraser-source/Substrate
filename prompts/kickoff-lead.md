# Lead Agent Kickoff (Codex/CLI)

You are the lead operator. Coordinate packet execution using the WBS CLI.

## First Steps
1. Read `AGENTS.md`
2. Check status:
   - `python3 .governance/wbs_cli.py status`
   - `python3 .governance/wbs_cli.py ready`
3. Select next packet and assign operator

## Lead Responsibilities
- Coordinate execution, dependencies, and sequencing
- Require evidence notes in every completed packet
- Handle failures (`fail`) and recovery (`reset` for in-progress packets)
- Produce full closeout reports per WBS phase

## Assignment Template
`Work WBS [AREA]. Claim [PACKET-ID], execute scope, then mark done with evidence note.`

## Session Handoff
Include:
- Completed / in-progress / pending / failed / blocked counts
- Packet-level evidence references
- Risks and immediate next actions
