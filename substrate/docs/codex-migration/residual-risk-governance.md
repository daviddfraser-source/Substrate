# Residual Risk Governance

## Purpose
Residual risk entries capture uncertainty that remains after a packet is marked `done`.

Runtime store:
- `.governance/residual-risk-register.json`

## Closure Contract
Packet completion requires explicit risk acknowledgement:
- no residual risk: `--risk none`
- residual risks declared: `--risk declared --risk-file <path>` or `--risk declared --risk-json '<json>'`

`done` transitions record acknowledgement metadata on the completion log event (`risk_ack`, `risk_ids`).

## Risk Entry Contract
Each risk entry records:
- `risk_id`
- `packet_id`
- `description`
- `likelihood` (`low|medium|high`)
- `impact` (`low|medium|high|critical`)
- `confidence` (`low|medium|high`)
- `declared_by`
- `declared_at`
- `status` (`open|mitigated|accepted|transferred`)

## Ownership and Evidence
- Risk declaration owner defaults to the completion actor.
- Status changes should include `resolution_notes` evidence via:
  - `python3 .governance/wbs_cli.py risk-update-status <risk_id> <status> <agent> "notes"`

## Dedupe Guidance
Use packet-scoped filtering before adding new risks:
- `python3 .governance/wbs_cli.py risk-list --packet <packet_id> --status open`

If a risk already exists, update status/notes instead of creating duplicate entries.

## Relationship to Level-2 Closeout
`closeout-l2` remains packet-completion and drift-document driven.
Residual risk state complements closeout by exposing unresolved uncertainty at packet granularity.
Recommended pre-closeout check:
- `python3 .governance/wbs_cli.py risk-list --status open`
- include unresolved risk references in the drift assessment `## Residual Risks` section.

## Reporting Commands
- `python3 .governance/wbs_cli.py risk-list [--packet id] [--status status] [--limit n]`
- `python3 .governance/wbs_cli.py risk-show <risk_id>`
- `python3 .governance/wbs_cli.py risk-summary`
- `python3 .governance/wbs_cli.py export risk-json <path>`
