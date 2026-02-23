# Scaffold Configuration Contract

Primary config file: `scaffold.config.json`

## Purpose
Centralize scaffold defaults for bootstrap, wizard behavior, and runtime settings.

## Required Keys
- `project_name`
- `default_agent`
- `dashboard_port`
- `wbs_template`
- `wbs_file`
- `enable_skills`
- `ci_profile`

## Schema
- `.governance/scaffold-config.schema.json`

## Notes
- Use `ci_profile: minimal` for fast bootstrap projects.
- Use `ci_profile: full` for governance-heavy repositories.
