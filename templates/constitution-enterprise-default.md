# Constitution Template (Enterprise Default)

## Governance Invariants
1. Deterministic governance before optimization.
2. Backend-enforced RBAC for all state-changing actions.
3. Immutable, queryable audit trail for every transition.
4. Packet lifecycle discipline: claim -> execute -> done/fail -> note.
5. Recursive improvement is proposal-based and approval-gated.
6. No autonomous self-modification of core governance controls.

## Session Execution Contract
- Start with governed briefing/context.
- Execute one packet at a time unless explicitly parallelized.
- Record evidence paths and validation output before completion.
- Reject completion when required validation is missing.

## Security Baseline
- Authenticated sessions required for governance APIs.
- Role checks must be enforced server-side.
- Sandbox policy required for embedded execution surfaces.

## Quality and Closeout
- Pre-commit checks enforce governance integrity.
- CI runs strict validation and contract tests.
- L2 closeout requires drift assessment with required sections.
