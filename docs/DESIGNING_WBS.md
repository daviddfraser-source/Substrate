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
