# Snippet: Claim -> Execute -> Done

Use this when starting implementation on a packet.

```text
1) Claim: python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex
2) Context: python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000
3) Implement strictly within scope
4) Validate impacted behavior
5) Done: python3 substrate/.governance/wbs_cli.py done <PACKET_ID> codex "Evidence: <files>, Validation: <commands/results>" --risk none
6) Note: python3 substrate/.governance/wbs_cli.py note <PACKET_ID> codex "Evidence paths: <paths>"
```
