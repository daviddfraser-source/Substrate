# Parallel Work Example

This example shows three independent packets that can be claimed concurrently, plus one integration packet that waits for all three.

## Pattern

`PAR-001`, `PAR-002`, and `PAR-003` can run in parallel.

`PAR-004` is the synchronization gate.

## Try It

```bash
python3 .governance/wbs_cli.py init examples/parallel-work/wbs.json
python3 .governance/wbs_cli.py ready
python3 .governance/wbs_cli.py claim PAR-001 agent-a
python3 .governance/wbs_cli.py claim PAR-002 agent-b
python3 .governance/wbs_cli.py claim PAR-003 agent-c
```
