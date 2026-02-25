# Substrate PRD v4.1 Redline Delta

Date: 2026-02-25
Source: "SUBSTRATE Deterministic Governance & Constraint Engine ... PRD v4.1"
Purpose: Resolve scope, determinism, and audit ambiguities before implementation.

## 1) Normative Scope Matrix (New Section 4.1)

Add immediately after Section 4 ("Scope Discipline"):

| Capability | v4.0 Kernel | v4.1 Governance | v4.2 Intelligence | v4.3 Enterprise Scale |
|---|---|---|---|---|
| `substrate_core` shared engine | MUST | MAINTAIN | MAINTAIN | MAINTAIN |
| Typed ontology enforcement | MUST | MAINTAIN | MAINTAIN | MAINTAIN |
| Deterministic constraint pipeline | MUST | MAINTAIN | MAINTAIN | MAINTAIN |
| Native policy evaluation | MUST | EXTEND (versioning + precedence trace) | MAINTAIN | MAINTAIN |
| Immutable audit (append-only) | MUST | MAINTAIN | MAINTAIN | EXTEND (hash-chain) |
| PostgreSQL graph core | MUST | MAINTAIN | MAINTAIN | MAINTAIN |
| Docker deployment | MUST | MAINTAIN | MAINTAIN | MAINTAIN |
| OPA compatibility | MUST NOT | SHOULD | MAINTAIN | MAINTAIN |
| Trust scoring | MUST NOT | SHOULD | MAINTAIN | MAINTAIN |
| Snapshot/diff | MUST NOT | SHOULD | MAINTAIN | MAINTAIN |
| Drift detection | MUST NOT | MUST NOT | SHOULD | MAINTAIN |
| Scenario simulation | MUST NOT | MUST NOT | SHOULD | MAINTAIN |
| Federation | MUST NOT | MUST NOT | MUST NOT | SHOULD |
| Air-gap validation | MUST NOT | MUST NOT | MUST NOT | SHOULD |

Normative interpretation:
- If a capability is `MUST NOT` for a phase, related backlog items cannot block that phase closeout.
- v4.0 closeout is valid when all v4.0 `MUST` items meet DoD regardless of deferred capabilities.

## 2) Shared Core Contract Hardening (Section 6)

Add to Section 6:

- `substrate_core` is the only transition authority.
- CLI/API/embedded terminal are transport adapters and cannot add business logic.
- Every adapter call must emit the same transition result envelope:
  - `decision`: `allow|deny`
  - `reason_codes`: deterministic codes
  - `policy_trace_id`: nullable
  - `audit_event_id`: required on committed transitions

Add invariant:
- If any surface returns a materially different decision for identical input, release is blocked.

## 3) Determinism Contract (New Section 8.4)

Add a new subsection:

- Hooks MUST be deterministic for identical `(entity_snapshot, transition, policy_version, actor_context)`.
- Hooks MUST be side-effect free before commit; external calls are disallowed in pre-commit path.
- Trust scoring models MUST be version-pinned and pure; no runtime model mutation.
- Policy evaluation input set MUST be canonicalized and hashable; audit logs must include input hash.
- Any non-deterministic dependency in transition path is a release blocker.

## 4) Policy Precedence and Fail-Closed Behavior (Section 9)

Add to Section 9:

Evaluation order (highest precedence first):
1. Constitutional rules
2. Active governance policy set
3. Risk gates
4. Role/capability constraints
5. Environmental constraints

Conflict resolution:
- Higher-precedence deny always wins.
- Unknown policy state => deny (fail-closed).
- Missing policy version => deny (fail-closed).

Required audit trace fields:
- `policy_version`
- `rule_ids_evaluated`
- `decision_by_rule`
- `final_decision`
- `precedence_path`

## 5) Immutability vs Rewind Clarification (Section 12)

Replace ambiguous "rewind capability" phrasing with:

- Rewind is event-sourced compensation, not mutation.
- Past audit events are immutable and never edited/deleted.
- Rewind creates new compensating events linked to prior event IDs.
- Provenance queries must show original and compensating chains.

## 6) DoD Boundary Clarification (Section 19)

Split current DoD into:

### 19.1 Kernel-Mandatory (v4.0)
- Bring up stack with `docker-compose up`
- Execute deterministic lifecycle transitions through shared core
- Enforce typed dependency/policy gates
- Produce immutable audit and provenance export
- Demonstrate graph traversal and impact query

### 19.2 Reference Surface (Non-Blocking for v4.0)
- Login UX and project creation UX can be satisfied by thin reference API/script path
- Full app scaffold experience is advisory for kernel release and cannot block v4.0 closeout

## 7) Commercial Boundary Table (New Section 21)

Add explicit licensing segmentation:

| Capability | Core (MIT) | Enterprise/Commercial |
|---|---|---|
| Engine core, ontology runtime, constraints, base policy | Yes | Yes |
| Baseline audit/provenance | Yes | Yes |
| Domain reference ontologies | No | Yes |
| Federation toolchain | No | Yes |
| Air-gap compliance kits | No | Yes |
| Advanced assurance packs | No | Yes |

## 8) Roadmap Alignment Edits (Section 17)

Update roadmap text to align with Section 4.1 matrix:
- Keep v4.0 limited to kernel `MUST` scope.
- Keep v4.1 to governance extensions only (policy versioning/precedence trace, trust v1, OPA adapter, snapshot/diff).
- Reserve hash-chain and air-gap validation for v4.3 as currently stated.

## 9) Decision Log (Recommended Addendum)

Add appendix:
- `ADR-v4.1-001`: Phase boundary matrix as normative control.
- `ADR-v4.1-002`: Determinism contract for hooks/trust/policy.
- `ADR-v4.1-003`: Event-sourced rewind semantics.
