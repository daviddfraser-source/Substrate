# Packet: AG-EXECUTE-CES-ROLLIN-002

**Date:** 2026-01-28  
**Authority:** Deterministic Delivery Constitution v3.1 (via VEX directive)  
**Executor:** AG (Antigravity)  
**Type:** AG_EXECUTION  
**Status:** PENDING  
**Priority:** CRITICAL  
**Reference:** VEX-WORKER-CANONICAL-EXEC-SNAPSHOT-001

---

## Executive Objective
Continue the Canonical Execution Snapshot (CES) rollout by satisfying the outstanding requirements in VEX-WORKER-CANONICAL-EXEC-SNAPSHOT-001. Ensure AG executes the structural plumbing that delivers a single, multi-domain CES and removes all residual ledger inference outside the CES spine.

## Scope
- `apps/business_case/js/sb2-execution-adapter.js`
- `apps/business_case/js/scenario-output.js`
- `apps/business_case/js/execution-state-manager.js`
- Any governance incumbent (logs, documentation) under `Governance/`

## Deliverables
1. **Full Domain Porting:** Replace the PARTIAL placeholders in `_generateCES` so Benefits, Demand, and Capacity domains are captured with ontology-aware series, reconciliation, and explicit statuses; each domain must follow COMPLETE/PARTIAL/INVALID semantics and log rationale for partial/invalid states.
2. **Scenario Outputs Integrity:** Remove any fallback path that derives series/results outside `ces.domains`. All displayed values (headlines, CCD1 series, captions) must originate from the CES payload; `externalResults` may remain for debugging but must not drive UI state.
3. **ExecutionStateManager Alignment:** Confirm `getCES()` is the only data source for scenarios marked REVIEW; any legacy ledger reconstruction functions must be gated behind NO_CES conditions and documented as disabled.
4. **Evidence Logging:** Record each CES creation + domain status proof + UI render validation in `Governance/AG_EXECUTION_EVIDENCE.md`, referencing this packet and its verification steps.

## Mandatory Constraints
- No new UI surfaces beyond Scenario Outputs gain execution authority. Scenario Builder remains preview-only.
- CES generation must still produce exactly one artifact per run; do not reintroduce multiple snapshots or ledger merges.
- All code changes must log packet IDs via AG annotation comments near new logic (`AG-ARCH-CES-001`, etc.).
- Operate exclusively inside the Governance directory for documentation/log updates; application code noted above is read-only for this session unless specifically instructed by VEX; cite new instructions if wider change necessary.

## Verification Requirements
1. Execute a scenario and capture the emitted CES JSON, verifying all four domains include `status`, `ontology`, `series`, `reconciliation`.
2. Reload scenario outputs and log that values match CES domain data; confirm partial/invalid statuses surface with textual clarity.
3. Document failure cases where removing CES disables outputs (evidence: console log or UI indicator showing NO_EXECUTION).
4. Append verification narrative to `Governance/AG_EXECUTION_EVIDENCE.md` and ensure `packet_trace.md` receives an entry summarizing rollin status once execution starts.

## Evidence
- CES payloads (good/partial/invalid).
- UI render log showing CES-driven values.
- Console proof of NO_EXECUTION state when CES absent.
- Updated `AG_EXECUTION_EVIDENCE.md` entries referencing this packet and VEX directive.

## Risk Notes
Incomplete domain coverage leaves Costs with canonical truth while Benefits/Demand/Capacity fall back to heuristics, violating VEX architecture. This AG packet locks in deterministic control before late-stage modules (benefits, Monte Carlo) may run on inconsistent data.

