# Packet Standard

This repository uses a canonical packet schema defined at:
- `.governance/packet-schema.json`

## Why
The packet viewer and governance workflow must render and validate complete packet content, not only title/scope/status.

## Required Packet Fields
Every packet must define:
- `packet_id`
- `wbs_refs` (array)
- `title`
- `purpose`
- `status`
- `owner`
- `priority`
- `preconditions`
- `required_inputs`
- `required_actions`
- `required_outputs`
- `validation_checks`
- `exit_criteria`
- `halt_conditions`

## Optional Extended Fields
- `authority`, `executor`, `type`, `references`
- `implementation_spec` (for full engineering specification packets)
- `evidence`, `risk_notes`, `metadata`

## Supported Packet Styles

### 1) Compact Governance Packet
Use for pilot/governance packets with concise deterministic controls.

```json
{
  "packet_id": "P-PILOT-3.1-TICKET-SCHEMA-LIFECYCLE",
  "wbs_refs": ["3.1.1", "3.1.2", "3.1.3"],
  "title": "Ticket schema and lifecycle",
  "purpose": "Define deterministic ticket lifecycle and transition guards.",
  "status": "PENDING",
  "owner": "governance-lead",
  "priority": "HIGH",
  "preconditions": ["P-PILOT-2.4 complete"],
  "required_inputs": ["governance/phase-1/dsme-state-machine.md"],
  "required_actions": ["Define lifecycle states", "Define transition guards"],
  "required_outputs": ["governance/phase-1/pilot-ticket-lifecycle-state-model.md"],
  "validation_checks": ["Every transition has deterministic prerequisites"],
  "exit_criteria": ["Lifecycle model complete and testable"],
  "halt_conditions": ["Approval possible without full evidence"]
}
```

### 2) Full Engineering Spec Packet
Use when implementation steps, files, and acceptance gates need full specification.

```json
{
  "packet_id": "CODEX-SPEC-EXP-LEDGER-PHASE4-01",
  "wbs_refs": ["4.1", "4.2", "4.3"],
  "title": "Renderer contract hardening",
  "purpose": "Remove defensive compensation and add explicit error rendering.",
  "status": "PENDING",
  "owner": "codex-worker",
  "priority": "CRITICAL",
  "preconditions": ["Phase 3 complete"],
  "required_inputs": ["apps/business_case/js/scenario-output.js"],
  "required_actions": ["Create error renderer", "Install error boundary"],
  "required_outputs": ["apps/business_case/js/ledger-error-renderer.js"],
  "validation_checks": ["No blank screen paths remain"],
  "exit_criteria": ["Error UI and validations complete"],
  "halt_conditions": ["Silent failure still possible"],
  "implementation_spec": {
    "objective": "Hard fail invalid ledger structure with explicit UI.",
    "steps": [
      {
        "id": "4.2.1",
        "title": "Create Error Rendering Module",
        "action": "Create ledger-error-renderer.js",
        "files": ["apps/business_case/js/ledger-error-renderer.js"]
      }
    ],
    "acceptance_criteria": ["Renderer catches and surfaces all known error states"]
  }
}
```

## Governance Rule
- Packet content in specs/docs should map cleanly to the canonical fields above.
- Packet viewer should render the whole packet object and runtime state together.
