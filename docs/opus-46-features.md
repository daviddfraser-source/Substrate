# Opus 4.6 Features for Substrate

This document covers Claude Opus 4.6 features integrated with Substrate governance.

## Overview

Substrate is configured to leverage Opus 4.6 capabilities:

| Feature | Configuration | Location |
|---------|--------------|----------|
| Agent Teams | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | `.claude/settings.json` |
| Adaptive Thinking | `thinking.type: "adaptive"` | `.claude/settings.json` |
| Effort Control | `thinking.effort: "high"` | `.claude/settings.json` |
| Team Hooks | `TeammateIdle`, `TaskCompleted` | `.claude/hooks.json` |

## Agent Teams

### What Are Agent Teams?

Agent Teams coordinate multiple Claude Code instances working together:
- **Team lead**: Coordinates work, assigns tasks, synthesizes results
- **Teammates**: Work independently in their own context windows
- **Shared task list**: Teammates claim and complete tasks
- **Direct messaging**: Teammates communicate without lead intermediation

### Agent Teams vs Subagents

| Feature | Subagents | Agent Teams |
|---------|-----------|-------------|
| Context | Results return to caller | Fully independent |
| Communication | Report to main agent only | Direct teammate messaging |
| Coordination | Main agent manages all | Self-coordination via shared list |
| Best for | Focused tasks | Complex collaborative work |
| Token cost | Lower | Higher |

### Integration with WBS Packets

Agent Teams map naturally to Substrate's packet-based governance:

| Agent Team Concept | Substrate Equivalent |
|--------------------|---------------------|
| Shared task list | WBS packets (`.governance/wbs.json`) |
| Task claiming | `wbs_cli.py claim <ID> <agent>` |
| Task completion | `wbs_cli.py done <ID> <agent> "evidence"` |
| Task dependencies | Packet dependencies |
| Quality gates | Hooks + evidence requirements |

### Team Formation for Packets

```
# Check which packets can run in parallel
python3 .governance/wbs_cli.py ready

# Example: 3 packets ready with no inter-dependencies
# UPG-001: Create lead prompt (docs)
# UPG-002: Create teammate prompt (docs)
# UPG-004: Create WBS template (templates)

# Spin up governed team
Create an agent team:
- Teammate "docs-1": Claim UPG-001
- Teammate "docs-2": Claim UPG-002
- Teammate "templates": Claim UPG-004

All teammates use governance CLI for state transitions.
```

### Hooks for Team Governance

Two hooks enforce governance during team execution:

**TeammateIdle Hook**
```json
{
  "matcher": { "event": "TeammateIdle" },
  "command": "python3 .governance/wbs_cli.py validate && python3 .governance/wbs_cli.py progress --json"
}
```
- Runs when a teammate finishes work
- Validates governance state
- Exit code 2 sends feedback to keep teammate working

**TaskCompleted Hook**
```json
{
  "matcher": { "event": "TaskCompleted" },
  "command": "python3 -c \"...check for in_progress packets...\""
}
```
- Runs when marking a task complete
- Checks for orphaned in_progress packets
- Prevents premature completion

## Adaptive Thinking

### What Is Adaptive Thinking?

Opus 4.6 introduces adaptive thinking where Claude dynamically decides when and how much to reason:

```python
# API configuration
response = client.messages.create(
    model="claude-opus-4-6",
    thinking={"type": "adaptive"},  # Claude decides
    # ...
)
```

### Effort Levels

| Level | Use Case | Token Cost |
|-------|----------|------------|
| `low` | Simple docs, config changes | Lowest |
| `medium` | Standard implementation | Moderate |
| `high` | Complex logic, multi-file changes (default) | Higher |
| `max` | Architecture decisions, security-critical | Highest |

### Effort by Packet Type

Match thinking effort to packet complexity:

| Packet Characteristics | Recommended Effort |
|------------------------|-------------------|
| Documentation updates | `low` |
| Single-file changes | `medium` |
| Multi-file implementation | `high` |
| New architecture/patterns | `max` |
| Security-sensitive code | `max` |
| Research/exploration | `high` + plan mode |

### Configuration

In `.claude/settings.json`:
```json
{
  "thinking": {
    "type": "adaptive",
    "effort": "high"
  }
}
```

Override per-session:
```bash
# For a complex architectural packet
claude --effort max

# For simple documentation
claude --effort low
```

## Context Compaction

### What Is Compaction?

Server-side context summarization for long conversations:
- Automatically summarizes older context as window fills
- Enables effectively infinite conversations
- Preserves key information while reducing tokens

### Benefits for Governance

- Long packet execution sessions don't hit context limits
- Evidence and decisions preserved in summaries
- Team lead can coordinate extended sprints

## 128K Output Tokens

Opus 4.6 supports up to 128K output tokens (doubled from 64K).

### Benefits for Governance

- Comprehensive evidence documentation
- Detailed implementation plans
- Full validation output capture
- Complete drift assessments

## Fast Mode (Research Preview)

2.5x faster output generation at premium pricing ($30/$150 per MTok).

### When to Use

- Time-sensitive packet execution
- Rapid prototyping sprints
- Live demonstrations

### Configuration

```python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    speed="fast",
    betas=["fast-mode-2026-02-01"],
    # ...
)
```

## Migration Notes

### Deprecated Features

| Deprecated | Replacement |
|------------|-------------|
| `thinking: {type: "enabled", budget_tokens: N}` | `thinking: {type: "adaptive"}` + effort |
| `interleaved-thinking-2025-05-14` beta header | Automatic with adaptive |
| `output_format` parameter | `output_config.format` |

### Breaking Changes

- **Prefill removal**: Assistant message prefills not supported
- **Tool parameter quoting**: Minor JSON escaping differences (standard parsers handle automatically)

## Best Practices

### For Team Leads

1. Use delegate mode for pure coordination
2. Set effort to `high` for monitoring
3. Validate teammate evidence before accepting
4. Run `wbs_cli.py progress` for synthesis

### For Teammates

1. Claim packet immediately upon spawn
2. Stay within packet scope
3. Include specific artifacts in evidence
4. Message lead when blocked

### For Complex Packets

1. Use plan mode before claiming
2. Set effort to `max` for architecture
3. Document decisions in evidence
4. Request human review for security-critical

## See Also

- [What's new in Claude 4.6](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6) - Official documentation
- [Agent Teams](https://code.claude.com/docs/en/agent-teams) - Claude Code documentation
- `.claude/skills/agent-teams/SKILL.md` - Governed team skill
- `docs/plan-mode-guide.md` - Plan mode integration
- `constitution.md` - Governance invariants

## Sources

- [Anthropic Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6)
- [TechCrunch: Agent Teams](https://techcrunch.com/2026/02/05/anthropic-releases-opus-4-6-with-new-agent-teams/)
- [Claude API Documentation](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6)
