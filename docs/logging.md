# Logging Configuration

The dashboard server supports configurable logging verbosity and output format.

## Environment Variables

- `WBS_LOG_LEVEL`
  - Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Default: `INFO`

- `WBS_LOG_FORMAT`
  - Values: `text`, `json`
  - Default: `text`

## Examples

Text logs with debug verbosity:

```bash
WBS_LOG_LEVEL=DEBUG python3 .governance/wbs_server.py 8090
```

JSON logs for ingestion:

```bash
WBS_LOG_LEVEL=INFO WBS_LOG_FORMAT=json python3 .governance/wbs_server.py 8090
```

## Notes

- API route misses are logged at warning level.
- Handler exceptions are logged with stack context.
- Access log lines are emitted through server logger.
