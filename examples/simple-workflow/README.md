# Simple Workflow Example

This example shows a strict linear chain of three packets.

## Pattern

`LIN-001 -> LIN-002 -> LIN-003`

Use this when work must happen in a fixed order.

## Try It

```bash
python3 .governance/wbs_cli.py init examples/simple-workflow/wbs.json
python3 .governance/wbs_cli.py ready
python3 .governance/wbs_cli.py claim LIN-001 demo
python3 .governance/wbs_cli.py done LIN-001 demo "Evidence: docs/contract.md"
python3 .governance/wbs_cli.py ready
```
