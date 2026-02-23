---
name: red-team-review
description: Adversarial review that actively probes for governance gaps, circumvention paths, weak evidence, and security issues
allowed-tools: Bash(python3 substrate/.governance/wbs_cli.py *), Bash(python3 substrate/scripts/sandbox.py *), Read, Grep, Glob
argument-hint: "[packet-id | area-id | governance | security | evidence | general]"
---

# Red Team Review

You are operating in **adversarial mode**. Your job is NOT to validate that things work — it is to find where they break, can be bypassed, or where evidence is superficial. Assume the posture of a hostile reviewer.

## Inputs

The user will provide a **focus area** — a concern, a suspicion, a scope (packet id, area id, project, or keyword). If not provided, default to the full governance layer.

## Step 1: Establish Context

```bash
python3 substrate/.governance/wbs_cli.py status
python3 substrate/.governance/wbs_cli.py briefing --format json
```

Read:
- `substrate/docs/architecture.md`
- `constitution.md`
- `AGENTS.md`
- `substrate/.governance/wbs-mutation-policy.json` (if exists)

## Step 2: Scope the Attack Surface

Based on the user's focus, identify the attack surface:

| Scope type | What to read |
|-----------|-------------|
| Packet `<id>` | Packet definition in `wbs.json`, state in `wbs-state.json`, evidence notes |
| Area `<id>` | All packets in area, closeout record, drift assessment file |
| `governance` | `wbs_cli.py`, `wbs_common.py`, `paths.py`, `engine.py`, `state_manager.py` |
| `security` | All CLI arg parsing, env var handling, approval token validation |
| `evidence` | All completed packets — check notes for real paths vs vague claims |
| `general` | All of the above |

## Step 3: Run Adversarial Checks

For each area of focus, probe aggressively:

### Governance Integrity Checks
- Can any state transition be made **without** a valid approval token? Try to find code paths that skip `require_wbs_mutation_approval()`
- Are there CLI commands that mutate `wbs.json` or `wbs-state.json` without going through the engine?
- Can an agent mark a packet `done` that belongs to another agent? Is ownership enforced?
- Are dependency checks enforced? Can a packet be claimed if its dependencies aren't done?
- Does `apply_runtime_project()` fully isolate project state, or are there leakage paths?
- Can the sandbox/projects directory be used to bypass enforcements on the main project?

### Evidence Quality Checks
For every completed packet in scope:
- Read the `notes` field — does it cite real file paths, or is it vague ("did the thing")?
- Do cited file paths actually exist? Check each one
- Are validation check results documented (tests passed / hygiene passed)?
- Was `--risk` acknowledged with real reasoning, or just `--risk none` without justification?

### Code Security Checks
- Look for `os.system()`, `subprocess.run(shell=True)` — are inputs sanitized?
- Are file paths validated before write operations?
- Can env vars (`WBS_PROJECT`, `WBS_CHANGE_APPROVAL`) be injected to escalate privileges?
- Are there any hardcoded secrets, tokens, or paths?

### State File Integrity Checks
- Read `wbs-state.json` directly — are there packets in ambiguous states (started but no `started_at`)?
- Are log entries sequential and plausible?
- Is there any evidence of direct state file edits (look for `recovery: true` flags or unusual gaps)?

### Schema and Validation Checks
- Run `python3 substrate/.governance/wbs_cli.py validate` — does it pass?
- Are all packets schema-compliant? Run `validate-packet` if available
- Check for packets with missing `required_actions`, `exit_criteria`, or `halt_conditions`

## Step 4: Active Probing (Sandbox Mode)

> [!IMPORTANT]
> Run adversarial tests in the sandbox project to avoid corrupting real state.

```bash
# Create sandbox
python3 substrate/scripts/sandbox.py create

# Try to bypass approval in sandbox
python3 substrate/.governance/wbs_cli.py --project sandbox claim <packet_id> red-team-agent
python3 substrate/.governance/wbs_cli.py --project sandbox done <packet_id> red-team-agent "test" --risk none

# Check if enforcement fires
python3 substrate/.governance/wbs_cli.py --project sandbox add-area GUARD-TEST "Guard Test"
# Expect: WBS mutation approval required

# Teardown
python3 substrate/scripts/sandbox.py destroy
```

## Step 5: Report Findings

Output a structured report using this format:

```
## Red Team Review — [Scope] — [Date]

### Critical Findings (must fix before next packet completion)
| # | Finding | Location | Evidence |
|---|---------|----------|----------|

### Medium Findings (should fix in current area work)
| # | Finding | Location | Evidence |

### Low / Informational
| # | Finding | Location | Evidence |

### What Held Up
- List guardrails and controls that correctly blocked adversarial actions

### Recommendations
1. ...
2. ...

### Next Steps
- [ ] <action> — owner: <agent>
```

## Step 6: Optionally Log Findings as Break-Fix Entries

For Critical findings, offer to log them:
```bash
python3 substrate/.governance/wbs_cli.py break-fix-open RED-TEAM-<N> "claude" "<finding title>" --severity critical --note "<detail>"
```
