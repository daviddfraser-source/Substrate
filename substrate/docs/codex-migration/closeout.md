# Session Closeout and Handoff Protocol

## Required Closeout
- Current WBS scope covered.
- Completion counts by status.
- Packet-level status for items touched.
- Evidence references (files and commands run).
- Risks, gaps, and next actions.
- For each Level-2 WBS area closeout, include a drift assessment document and record it with:
  - `python3 .governance/wbs_cli.py closeout-l2 <area_id|n> <agent> <drift_assessment.md> [notes]`
- `closeout-l2` only succeeds when every packet in that area is already `done`.
- Required drift assessment sections:
  - `## Scope Reviewed`
  - `## Expected vs Delivered`
  - `## Drift Assessment`
  - `## Evidence Reviewed`
  - `## Residual Risks`
  - `## Immediate Next Actions`
- Cryptographic hashing is explicitly not required.

## Handoff Checklist
- State file reflects true packet status.
- Packet notes include evidence paths.
- Any partial work is explicitly called out.
- Next recommended packet(s) identified.
