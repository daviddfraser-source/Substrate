# Packet Schema Guide

Canonical schema: `.governance/packet-schema.json`

## Required Fields

- `packet_id`: unique packet identifier string
- `wbs_refs`: one or more WBS refs covered by packet
- `title`: short packet title
- `purpose`: clear intent statement
- `status`: one of `DRAFT|PENDING|IN_PROGRESS|BLOCKED|DONE|FAILED`
- `owner`: responsible owner
- `priority`: `LOW|MEDIUM|HIGH|CRITICAL`
- `preconditions`: prerequisite conditions list
- `required_inputs`: required inputs list
- `required_actions`: required implementation actions
- `required_outputs`: expected outputs/artifacts
- `validation_checks`: checks to verify completion quality
- `exit_criteria`: completion conditions
- `halt_conditions`: stop/abort conditions

## Common Optional Fields

- `authority`: governance authority source
- `executor`: executor identity when different from owner
- `type`: packet class
- `references`: external links/refs
- `implementation_spec`: detailed implementation plan
- `evidence`: evidence artifact paths
- `risk_notes`: residual risks
- `metadata`: timestamps/tags

## Valid Example

```json
{
  "packet_id": "CDX-13-11",
  "wbs_refs": ["13.11"],
  "title": "Publish packet schema guide",
  "purpose": "Document required fields, validation rules, and examples.",
  "status": "PENDING",
  "owner": "codex-lead",
  "priority": "HIGH",
  "preconditions": ["CDX-13-10 complete"],
  "required_inputs": [],
  "required_actions": ["Write docs/packet-schema-guide.md"],
  "required_outputs": ["docs/packet-schema-guide.md"],
  "validation_checks": ["Schema fields match packet-schema.json"],
  "exit_criteria": ["Guide merged and referenced"],
  "halt_conditions": ["Schema source missing"]
}
```

## Invalid Example

```json
{
  "packet_id": "CDX-13-11",
  "title": "Missing required fields",
  "status": "OPEN"
}
```

Invalid reasons:
- missing required arrays/fields (`wbs_refs`, `purpose`, `required_actions`, etc.)
- invalid enum value (`status: OPEN`)

## Validation Commands

```bash
python3 .governance/wbs_cli.py validate-packet .governance/wbs.json
python3 .governance/wbs_cli.py validate-packet path/to/packet.json
```
