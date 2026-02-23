# Codex Migration Guide

## Goal
Run this WBS orchestration repo in a Codex-first, CLI-first mode without requiring Claude skill wrappers.

## Step 1: Initialize WBS
```bash
python3 .governance/wbs_cli.py init templates/wbs-codex-refactor.json
python3 .governance/wbs_cli.py ready
```

## Step 2: Execute Packet Lifecycle
```bash
python3 .governance/wbs_cli.py claim <packet_id> <agent>
python3 .governance/wbs_cli.py done <packet_id> <agent> "summary + evidence"
python3 .governance/wbs_cli.py note <packet_id> <agent> "updated evidence"
```
- Execute one packet at a time per agent unless explicitly directed otherwise.
- Do not expand packet scope without explicit instruction.
- Completion notes should include: what changed, artifact path, validation performed.

## Step 3: Use Governance Contracts
- `AGENTS.md`: operating contract and reporting standard
- `.governance/packet-schema.json`: canonical packet schema
- `docs/codex-migration/packet-standard.md`: packet structure guidance and examples
- `docs/codex-migration/command-map.md`: command translation
- `docs/codex-migration/roles-and-sop.md`: lead/teammate protocol
- `docs/codex-migration/closeout.md`: closeout requirements

## Step 4: Recovery and Diagnostics
Use `docs/PLAYBOOK.md` for JSON-state recovery actions.
- During long-running execution, reconcile:
  - `python3 .governance/wbs_cli.py status`
  - `python3 .governance/wbs_cli.py log 30`

## Step 5: Reporting
For each WBS phase, provide a full delivery report:
- scope
- status counts
- per-packet details with timestamps and evidence
- risks and next actions
- If validation was not run for an item, state that explicitly.
- If any requested action was not executed, state that explicitly.

## Step 6: Level-2 Closeout Drift Assessment
When a Level-2 area is complete, close it out with drift review:
```bash
python3 .governance/wbs_cli.py closeout-l2 <area_id|n> <agent> docs/codex-migration/drift-wbs<area>.md "closeout note"
```

Use `docs/codex-migration/drift-assessment-template.md` and include all required sections.
Cryptographic hashing is not required.

## Step 7: Blockers and Escalation
If blocked, mark failure with explicit reason and dependency impact:
```bash
python3 .governance/wbs_cli.py fail <packet_id> <agent> "reason + impacted dependency chain"
```
