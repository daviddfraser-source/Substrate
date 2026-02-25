# Substrate Core Mutation Log Schema (WBS 15.9)

## Required Structured Fields
Every PacketEngine mutation appends a lifecycle log entry with these query/export fields:
- `actor`
- `role`
- `source`
- `action`
- `packet`
- `timestamp`
- `result`
- `exit_state`

## Lifecycle Compatibility Fields Retained
For backward compatibility with existing viewers and exports, entries still include:
- `packet_id`
- `event`
- `agent`
- `notes`
- hash-chain metadata when enabled (`hash`, `hash_prev`, `hash_index`)

## Export Path
- Primary state/audit source: `.governance/wbs-state.json` (`log` array)
- Sample export artifact: `reports/substrate-core-log-export-sample.json`
- Existing CLI exporters remain valid (`export log-json`, `export log-csv`)

## Verification
- PacketEngine mutation calls (`claim`, `done`, `note`, `fail`, `block`, `reset`) route through a shared structured logger.
- API and embedded terminal mutation paths call PacketEngine directly, so logs share one schema across interfaces.
