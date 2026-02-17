# Skill Execution Permission Model

Policy file:
- `.governance/skill-permissions.json`

Loader:
- `src/governed_platform/skills/policy.py`

Model:
- `src/governed_platform/skills/permissions.py`

## Policy Scope
- `allowed_roots`: filesystem roots where skill execution may run.
- `allowed_commands`: executable allowlist for sandbox launches.
