# Lead Agent Kickoff (Codex/CLI)

Copy-paste this into a fresh lead session:

```text
You are the lead operator for this repository.
1) Read AGENTS.md and CLAUDE.md (plus GEMINI.md if Gemini agents are involved).
2) If state is not initialized, run: python3 .governance/wbs_cli.py init .governance/wbs.json
3) Run: python3 .governance/wbs_cli.py status
4) Run: python3 .governance/wbs_cli.py ready
5) Select one ready packet and assign execution.
6) For each packet, enforce lifecycle: claim -> execute -> done/fail -> note.
7) Require evidence path + validation command in completion notes.
8) Keep one packet per agent unless the user explicitly approves parallel execution.
```

## Teammate Spawn Pattern

Use this assignment format when spawning teammates:

`Work WBS [AREA]. Claim [PACKET-ID], execute exact scope, run validation, then mark done with evidence.`

Example teammate prompt:

```text
Work WBS 9.0. Claim UPG-041 as claude, execute only packet scope, run validation, then:
python3 .governance/wbs_cli.py done UPG-041 claude "Changed <files>; validated with <command>; evidence: <path>"
python3 .governance/wbs_cli.py note UPG-041 claude "Residual risk: <risk>; next action: <action>"
```

## Lead Closeout Checklist

- Report done/in_progress/pending/failed/blocked counts
- Include packet-level evidence references
- Capture residual risks and immediate next actions
