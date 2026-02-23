# Briefing and Context Output Contract

Status: active contract for implementation stream `UPG-044..UPG-047`.

## Versioning

- `schema_id` identifies payload family.
- `schema_version` uses `MAJOR.MINOR`.
- Breaking field changes require MAJOR increment.
- Additive fields are MINOR increments.
- Deprecated fields must remain readable for at least one MINOR version.

## Common Envelope

All JSON outputs in this contract family must include:

- `schema_id` (string)
- `schema_version` (string)
- `generated_at` (ISO-8601 timestamp string)
- `mode` (`full|compact`)
- `truncated` (boolean)
- `limits` (object of active size controls)

## Briefing Contract

Command target:

```bash
python3 .governance/wbs_cli.py briefing [--format json|text] [--compact] [--recent N]
```

`schema_id`: `wbs.briefing`  
`schema_version`: `1.0`

Required payload keys:

- `project`: `{ project_name, approved_by, approved_at }`
- `counts`: runtime status counts
- `ready_packets`: claimable packets
- `blocked_packets`: packets blocked by failed/incomplete dependencies, with reason list
- `active_assignments`: in-progress packet to agent map
- `recent_events`: latest lifecycle events (newest-first)

JSON example:

```json
{
  "schema_id": "wbs.briefing",
  "schema_version": "1.0",
  "generated_at": "2026-02-17T13:30:00.000000",
  "mode": "full",
  "truncated": false,
  "limits": {
    "recent_events": 10
  },
  "project": {
    "project_name": "Agent Teams Starter Kit — Full Upgrade",
    "approved_by": "human",
    "approved_at": "2025-02-12T00:00:00"
  },
  "counts": {
    "pending": 28,
    "in_progress": 1,
    "done": 23
  },
  "ready_packets": [
    {
      "id": "UPG-045",
      "wbs_ref": "10.2",
      "title": "Implement briefing command and session bootstrap guidance"
    }
  ],
  "blocked_packets": [],
  "active_assignments": [
    {
      "packet_id": "UPG-044",
      "agent": "codex",
      "started_at": "2026-02-17T13:07:16.590230"
    }
  ],
  "recent_events": [
    {
      "packet_id": "UPG-044",
      "event": "started",
      "agent": "codex",
      "timestamp": "2026-02-17T13:07:16.590244",
      "notes": "Claimed by codex"
    }
  ]
}
```

## Context Contract

Command target:

```bash
python3 .governance/wbs_cli.py context <packet_id> [--format json|text] [--compact] [--max-events N] [--max-notes-bytes N] [--max-handovers N]
```

`schema_id`: `wbs.context_bundle`  
`schema_version`: `1.0`

Required payload keys:

- `packet_definition`: full packet object from `.governance/wbs.json`
- `runtime_state`: current packet runtime state from `.governance/wbs-state.json`
- `dependencies`: `{ upstream, downstream }` with status snapshots
- `history`: lifecycle events for the packet (newest-first)
- `handovers`: ordered handover records (empty when not used)
- `file_manifest`: repository-relative file references extracted from packet/evidence context
- `truncation`: explicit counters for any reduced arrays/text payloads

JSON example:

```json
{
  "schema_id": "wbs.context_bundle",
  "schema_version": "1.0",
  "generated_at": "2026-02-17T13:30:00.000000",
  "mode": "compact",
  "truncated": true,
  "limits": {
    "max_events": 5,
    "max_notes_bytes": 1024,
    "max_handovers": 10
  },
  "packet_id": "UPG-044",
  "packet_definition": {
    "id": "UPG-044",
    "wbs_ref": "10.1",
    "area_id": "10.0",
    "title": "Stabilize briefing and context output contracts",
    "scope": "Define versioned JSON/text schemas for briefing/context outputs..."
  },
  "runtime_state": {
    "status": "in_progress",
    "assigned_to": "codex",
    "started_at": "2026-02-17T13:07:16.590230",
    "completed_at": null,
    "notes": null
  },
  "dependencies": {
    "upstream": [],
    "downstream": [
      {
        "packet_id": "UPG-045",
        "status": "pending"
      }
    ]
  },
  "history": [
    {
      "packet_id": "UPG-044",
      "event": "started",
      "agent": "codex",
      "timestamp": "2026-02-17T13:07:16.590244",
      "notes": "Claimed by codex"
    }
  ],
  "handovers": [],
  "file_manifest": [
    {
      "path": "docs/codex-migration/briefing-context-schema.md",
      "exists": true
    }
  ],
  "truncation": {
    "history_dropped": 0,
    "notes_bytes_dropped": 0
  }
}
```

## Size and Truncation Rules

Default controls:

- `recent_events`: 10 for briefing
- `max_events`: 40 for context
- `max_notes_bytes`: 4000 for context
- `max_handovers`: 40 for context

Hard max guardrails:

- `recent_events <= 200`
- `max_events <= 200`
- `max_notes_bytes <= 32000`
- `max_handovers <= 200`

Truncation behavior:

- Preserve newest-first ordering.
- Drop oldest entries first when limits are exceeded.
- Set `truncated=true` when any payload section is reduced.
- Populate `truncation` counters to make dropped content explicit.

## Text Output Requirements

Text mode must be deterministic and sectioned:

- `Summary`
- `Ready Packets`
- `Blocked Packets`
- `Active Assignments`
- `Recent Events`

Context text mode must include:

- `Packet Definition`
- `Runtime State`
- `Dependencies`
- `History`
- `Handovers`
- `File Manifest`

## Compatibility and Consumer Expectations

- Consumers must match on `schema_id` and parse by `schema_version`.
- Unknown fields must be ignored.
- Missing required fields are contract violations and must fail tests.
- Any change to required keys must ship with a migration note in docs and tests.
