# Packet Context Bundle Standard

## Path Convention
- `.governance/packets/<packet_id>/context.md`

## Required Sections
1. Packet Summary
2. Scope
3. Purpose
4. Preconditions
5. Required Inputs
6. Required Actions
7. Required Outputs
8. Validation Checks
9. Exit Criteria
10. Halt Conditions
11. Dependency Context
12. Recent Events
13. Execution Steps

## Generation Command
```bash
python3 scripts/generate-packet-bundle.py <packet_id>
```

## Size Budget
- Default max size: 24 KB per bundle
- Goal: enough context to execute the packet without loading full repository state

## Recommended Session Flow
```bash
python3 scripts/generate-session-brief.py
python3 .governance/wbs_cli.py ready --json
python3 .governance/wbs_cli.py claim <packet_id> <agent>
python3 scripts/generate-packet-bundle.py <packet_id>
```
