# Claude Compatibility Notice

## Current Support Model
- Primary workflow is CLI-first and agent-neutral.
- Codex, Claude, and other agents can operate through `python3 .governance/wbs_cli.py`.

## Legacy Claude Assets
- `.claude/skills/` and `.claude/settings.json` remain available as optional legacy integrations.
- They are not required for core WBS execution.

## Recommended Usage
- Prefer direct CLI commands for portability and auditability.
- Keep packet evidence in notes using `note` command if updates are needed post-completion.
