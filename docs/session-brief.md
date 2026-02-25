# Session Brief

Generated: 2026-02-24T07:48:55.759033+00:00

Project: Substrate App Scaffold
Approved By: david-fraser

## Status Counts
- done: 50
- in_progress: 1

## Ready Packets
- none

## Blocked Packets
- none

## Startup Path
1. python3 .governance/wbs_cli.py briefing --format json
2. python3 .governance/wbs_cli.py ready --json
3. python3 .governance/wbs_cli.py claim <packet_id> <agent>
4. python3 .governance/wbs_cli.py context <packet_id> --format json
