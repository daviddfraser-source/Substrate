# Designing a Good WBS

## Packet Sizing

**Target**: 15-60 minutes of focused work.

| Type | Target Size |
|------|------------|
| Code | 50-200 lines |
| Docs | 1-3 pages |
| Research | 1 question |
| Testing | 1 suite |

Split large packets by: component, feature slice, layer, or phase.

## Dependencies

Good:
```json
{"FEAT-003": ["FEAT-001", "FEAT-002"]}
```

Avoid:
- Circular: A→B→A (rejected by CLI)
- Over-constraining: everything depends on everything
- Hidden: real deps not declared

Maximize parallelism:
```
      ┌─ B ─┐
  A ──┼─ C ─┼── F
      └─ D ─┘
```

## Writing Scopes

Template:
```
[ACTION] [WHAT] [WHERE]. Output: [DELIVERABLE].
```

Good: `Implement JWT auth in api/auth.py. Output: working endpoints with tests.`
Bad: `Do the auth stuff.`

Checklist:
- Clear action verb
- Specific deliverable
- Success criteria
- Constraints mentioned

## Work Areas

- Group by function, phase, or component
- 3-6 packets per area
- Split areas with 10+ packets

## Quick Checklist

- [ ] Clear deliverables
- [ ] No packet > 1 hour
- [ ] Complete dependencies
- [ ] No circular deps
- [ ] Parallelism possible

## Guided Planner Mode

Use the guided planner when you want to generate a valid WBS without hand-editing JSON.

Interactive flow:

```bash
python3 .governance/wbs_cli.py plan
```

Non-interactive flow (recommended for tests/automation):

```bash
python3 .governance/wbs_cli.py plan --from-json planner-spec.json --output .governance/wbs-draft.json
```

Apply planned output directly:

```bash
python3 .governance/wbs_cli.py plan --from-json planner-spec.json --apply
```

Planner spec shape:

```json
{
  "project_name": "My Project",
  "approved_by": "lead",
  "work_areas": [
    {
      "id": "1.0",
      "title": "Discovery",
      "description": "optional",
      "packets": [
        {
          "id": "DISC-001",
          "title": "Draft scope",
          "scope": "Draft scope. Output: docs/scope.md",
          "depends_on": []
        }
      ]
    }
  ],
  "dependencies": {
    "DISC-002": ["DISC-001"]
  }
}
```

Notes:
- IDs are normalized for consistency (`task one` -> `TASK-ONE`).
- Dependency aliases are resolved during normalization.
- Dependency cycles are rejected with actionable guidance.

## Experimental Markdown Import

You can import an existing markdown plan into a draft WBS:

```bash
python3 .governance/wbs_cli.py plan --import-markdown docs/project-proposal.md --output .governance/wbs-imported.json
```

Important behavior:
- This path is experimental and marks imported packets with `import_confidence`.
- Low-confidence mappings are tagged with `import_requires_review: true`.
- Ambiguous imports are surfaced as `import_warnings` at the top level.
- `--apply` is blocked when ambiguity exists unless you explicitly pass `--allow-ambiguous`.

Recommended correction loop:
1. Run `plan --import-markdown ... --output ...`.
2. Edit low-confidence packet titles/scopes/dependencies.
3. Re-export through planner with `plan --from-json corrected.json --output final.json`.
4. Initialize and validate: `init final.json` then `validate`.
