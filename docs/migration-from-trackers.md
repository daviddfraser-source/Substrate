# Migration From External Trackers

This guide maps external work-item systems (Jira, Linear, Asana, etc.) into WBS packets.

## Goal

Preserve dependency intent and execution auditability while converting to packet-based lifecycle control.

## Mapping Model

| External Concept | Packet/WBS Target |
|---|---|
| Epic / Project | Work area (`<N>.0`) |
| Story / Task | Packet (`id`, `wbs_ref`, `title`, `scope`) |
| Blocked-by links | `dependencies` graph |
| Assignee | runtime `assigned_to` on claim |
| Done criteria | packet `scope` + completion notes + evidence |

## Recommended Steps

1. Export source tasks to CSV/JSON from your tracker.
2. Normalize fields into intermediate schema:
   - `external_id`, `area`, `title`, `scope`, `depends_on[]`
3. Generate `wbs.json` structure with:
   - `work_areas`
   - `packets`
   - `dependencies`
4. Validate with:
   - `python3 .governance/wbs_cli.py validate`
5. Initialize state:
   - `python3 .governance/wbs_cli.py init .governance/wbs.json`

## Bulk-Import Skeleton

```bash
# source.csv -> transformed-wbs.json (user script)
python3 scripts/transform_tracker_export.py source.csv > transformed-wbs.json
python3 .governance/wbs_cli.py init transformed-wbs.json
```

## Data Quality Checks

- no duplicate packet IDs
- no circular dependencies
- all packet area references valid
- each packet scope has clear output expectation

## Cutover Strategy

- freeze external tracker updates for cutover window
- import and validate WBS graph
- run first packet claim/done cycle
- archive import artifacts for traceability
