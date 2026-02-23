# Snippet: Blocker Escalation

```text
Blocked packet: <PACKET_ID>
Reason: <specific blocker>
Dependency impact: <downstream packets>
Attempted actions: <what was tried>
Proposed corrective action: <next step>

Command:
python3 substrate/.governance/wbs_cli.py fail <PACKET_ID> codex "Blocked: <reason>; Impact: <impact>"
```
