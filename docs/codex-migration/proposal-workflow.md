# Recursive Proposal Workflow Contract

Date: 2026-02-24
Packet: PRD-5-3

## Workflow States

- `submitted`
- `in_review`
- `approved`
- `rejected`

## Guardrails

- Denied proposal types are rejected at creation
- `auto_apply` always raises permission error
- Manual officer review is required for approval/rejection
- All state changes are audit-logged

## Allowed Proposal Types

- lifecycle_rule_refinement
- role_permission_adjustment
- dependency_rule_improvement
- risk_threshold_tuning
- ux_friction_reduction

## Validation

- `python3 -m unittest tests/test_proposal_workflow.py`
