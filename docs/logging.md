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

## Lifecycle Log Integrity Mode

Governance lifecycle events in `.governance/wbs-state.json` can run in:

- `plain`
  - default mode; standard append-only event records.
- `hash-chain`
  - tamper-evident mode; each new event includes `event_id`, `prev_hash`, and `hash`.

Enable hash-chain mode:

```bash
python3 .governance/wbs_cli.py log-mode hash-chain
```

Return to plain mode:

```bash
python3 .governance/wbs_cli.py log-mode plain
```

Verify integrity:

```bash
python3 .governance/wbs_cli.py verify-log
python3 .governance/wbs_cli.py --json verify-log
```

## Git Linkage Ledger

When git-native auto-commit is enabled, lifecycle log entries may include:
- `git_link_status` (`linked|warning`)
- `git_mode`
- `git_commit` (when linked)
- `git_event_id`
- `git_action`
- `git_actor`
- `git_link_error` (warning detail)

Verify linkage integrity:

```bash
python3 .governance/wbs_cli.py git-verify-ledger
python3 .governance/wbs_cli.py git-verify-ledger --strict
python3 .governance/wbs_cli.py --json git-verify-ledger
```

Export linkage snapshot:

```bash
python3 .governance/wbs_cli.py git-export-ledger reports/git-ledger.json
```
