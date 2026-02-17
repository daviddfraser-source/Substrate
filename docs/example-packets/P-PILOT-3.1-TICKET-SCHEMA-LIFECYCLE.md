# Packet P-PILOT-3.1-TICKET-SCHEMA-LIFECYCLE

**Authority:** Phase 1 governance boundary  
**WBS Coverage:** 3.1.1-3.1.3  
**Purpose:** Define the Decision Ticket schema, lifecycle states, and deterministic transition guards.

## Preconditions
- Packet `P-PILOT-2.4-INGESTION-DETERMINISM-RETENTION` is complete.
- Pilot ticker and evidence schemas are locked.

## Required Inputs
- `Projects/Phase 1/phase1_step3_decision_ticket_schema.md`
- `Projects/Phase 1/governance/phase-1/dsme-state-machine.md`
- `Projects/Phase 1/governance/phase-1/dsme-transition-guards.md`

## Required Actions
1. Define canonical Decision Ticket schema with deterministic primitives.
2. Define lifecycle states (draft, evidence_ready, assumptions_ready, scenario_ready, failure_ready, governance_ready, approved, rejected, superseded).
3. Define transition guards and explicit no-skip/no-silent-regress constraints.
4. Define violation codes for invalid transitions and missing required fields.

## Required Outputs
- `Projects/Phase 1/governance/phase-1/pilot-decision-ticket-schema.md`
- `Projects/Phase 1/governance/phase-1/pilot-ticket-lifecycle-state-model.md`
- `Projects/Phase 1/governance/phase-1/pilot-ticket-transition-violation-codes.md`

## Validation Checks
- Schema fields are deterministic and hashable.
- Every state transition has machine-testable prerequisites.
- Regression/supersession behavior is explicit and audited.

## Exit Criteria
- Ticket lifecycle and schema are complete, testable, and governance-linked.

## Halt Conditions
- Ticket can move to approval without full lifecycle evidence.
- Transition guards permit non-deterministic outcomes.
