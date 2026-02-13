# Packet P-PILOT-3.2-DECISION-SURFACE-CONTROLS

**Authority:** Phase 1 governance boundary  
**WBS Coverage:** 3.2.1-3.2.4  
**Purpose:** Constrain the decision surface to approved pilot actions, size options, horizons, and deterministic exits.

## Preconditions
- Packet `P-PILOT-3.1-TICKET-SCHEMA-LIFECYCLE` is complete.
- Pilot PRD baseline is locked.

## Required Inputs
- `Projects/Phase 1/pilot_prd_asx_smallcap_miners_v1.md`
- `Projects/Phase 1/phase1_step3_decision_ticket_schema.md`
- `Projects/Phase 1/governance/phase-1/pilot-prd-baseline-register.md`

## Required Actions
1. Define allowed decision types (`ENTER`, `ADD`, `REDUCE`, `EXIT`, `HOLD`, `DO_NOT_TRADE`).
2. Define constrained position size options (0%, 0.25%, 0.5%, 1%, 2%).
3. Define constrained horizon options (1, 3, 10 trading days).
4. Define deterministic exit-rule fields (take-profit, stop-loss, time-stop) and validation logic.
5. Define rejection behavior for out-of-surface values.

## Required Outputs
- `Projects/Phase 1/governance/phase-1/pilot-decision-surface-spec.md`
- `Projects/Phase 1/governance/phase-1/pilot-exit-rule-validation-spec.md`

## Validation Checks
- Any unsupported action/size/horizon is packet-blocking.
- Exit rules are explicit, typed, and deterministic.
- `DO_NOT_TRADE` remains first-class and auditable.

## Exit Criteria
- Decision surface controls are complete and integrated with lifecycle guards.

## Halt Conditions
- Free-form decision values are accepted.
- Exit behavior can vary without schema change.
