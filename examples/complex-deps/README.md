# Complex Dependency Example

This example models a multi-level DAG.

## Shape

- `DAG-001` is the root.
- `DAG-002` and `DAG-003` fan out from root.
- `DAG-004` and `DAG-005` converge from both branches.
- `DAG-006` is the final release gate.

## Try It

```bash
python3 .governance/wbs_cli.py init examples/complex-deps/wbs.json
python3 .governance/wbs_cli.py graph
python3 .governance/wbs_cli.py ready
```

This pattern is appropriate for feature programs with multiple dependency layers.
