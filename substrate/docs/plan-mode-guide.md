# Using Plan Mode with Substrate Governance

Constitutional authority: `constitution.md`

## Overview

Claude Code's **plan mode** integrates naturally with Substrate's packet-based governance. Use plan mode for complex packets requiring architectural decisions before execution.

## When to Use Plan Mode

Use plan mode when a packet involves:

- **Multiple implementation approaches** - Need to evaluate trade-offs
- **Architectural decisions** - Component structure, patterns, dependencies
- **Multi-file changes** - Touching 3+ files with interconnected changes
- **Unclear scope boundaries** - Need clarification before proceeding
- **High-risk changes** - Security, API contracts, data migrations

## Workflow Integration

### 1. Identify Complex Packet

```bash
python3 .governance/wbs_cli.py ready
python3 .governance/wbs_cli.py scope <PACKET_ID>
```

Review `required_actions`, `exit_criteria`, and `halt_conditions`. If scope is complex or ambiguous, use plan mode.

### 2. Enter Plan Mode

Tell Claude: "Let's plan the approach for packet X before claiming it"

Claude will:
- Explore relevant codebase areas
- Identify existing patterns to follow
- Draft implementation approach
- Present plan for approval

### 3. Review and Approve Plan

Before approving, verify:
- [ ] Plan addresses all `required_actions`
- [ ] Approach satisfies `exit_criteria`
- [ ] No `halt_conditions` are triggered
- [ ] Evidence collection strategy is clear

### 4. Claim and Execute

After plan approval:

```bash
python3 .governance/wbs_cli.py claim <PACKET_ID> claude
```

Execute the approved plan. The plan provides structure for:
- Implementation sequence
- File-by-file changes
- Validation checkpoints
- Evidence to collect

### 5. Complete with Evidence

```bash
python3 .governance/wbs_cli.py done <PACKET_ID> claude "Evidence: [artifacts + validation]"
```

## Example Session

```
User: Let's plan UPG-005 before starting

Claude: [Enters plan mode]
        [Reads packet scope]
        [Explores codebase for patterns]
        [Identifies affected files]
        [Drafts implementation approach]
        [Presents plan for review]

User: [Reviews plan, requests adjustments]

Claude: [Updates plan]
        [Exits plan mode with approved approach]

User: Claim and execute

Claude: python3 .governance/wbs_cli.py claim UPG-005 claude
        [Executes plan step-by-step]
        [Collects evidence]
        python3 .governance/wbs_cli.py done UPG-005 claude "Created X, validated Y"
```

## Plan Mode + Constitutional Rules

Plan mode respects constitutional constraints:

| Constitution Article | Plan Mode Behavior |
|---------------------|-------------------|
| Article I (Scope) | Plan must stay within packet `required_actions` |
| Article II (Transitions) | Claim only after plan approval |
| Article III (Evidence) | Plan includes evidence collection strategy |
| Article IV (Protected Resources) | Plan cannot modify governance files |
| Article VI (Human Authority) | Human approves plan before execution |

## Anti-Patterns

**Don't:**
- Claim packet before planning complex work
- Plan beyond packet scope boundaries
- Skip plan approval for significant changes
- Ignore halt conditions during planning

**Do:**
- Use plan mode proactively for complex packets
- Include validation steps in plan
- Document assumptions for human review
- Exit plan mode cleanly before claiming

## Task List Integration

For complex packets, Claude may create task items during planning:

```
Plan for UPG-005:
[ ] Update API schema (src/api/schema.py)
[ ] Add validation middleware (src/middleware/validate.py)
[ ] Write unit tests (tests/test_validation.py)
[ ] Update API documentation (docs/api.md)
```

These tasks track execution progress within the packet scope.

## Troubleshooting

### Plan exceeds packet scope
Re-read `required_actions`. If genuine scope expansion needed, request human clarification per Article I Section 3.

### Plan conflicts with existing patterns
Document the conflict and recommend approach. Human decides whether to follow existing patterns or establish new ones.

### Multiple valid approaches
Present options with trade-offs. Human selects approach before execution.

## See Also

- `CLAUDE.md` - Claude Code operating instructions
- `AGENTS.md` - Agent operating contract
- `constitution.md` - Constitutional governance rules
- `docs/PLAYBOOK.md` - Error recovery procedures
