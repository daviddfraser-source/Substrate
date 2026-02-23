# Export Formats

The CLI supports exporting governance state and logs for external analysis.

## Commands

```bash
python3 .governance/wbs_cli.py export state-json dist/state-export.json
python3 .governance/wbs_cli.py export log-json dist/log-export.json
python3 .governance/wbs_cli.py export log-csv dist/log-export.csv
```

## Formats

- `state-json`
  - JSON object with `packets` and `area_closeouts`.
- `log-json`
  - JSON object with `log` array.
- `log-csv`
  - CSV with columns: `packet_id,event,agent,timestamp,notes`.

## Use Cases

- feed packet status to custom reporting
- import logs into spreadsheets/BI tools
- archive closeout activity snapshots
