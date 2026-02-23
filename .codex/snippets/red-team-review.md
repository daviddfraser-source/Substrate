# Red Team Review — Codex Snippet

Activate this when asked to perform an adversarial review of governance, evidence, or security.
Assume the posture of a hostile reviewer. Your goal is to find gaps, bypass paths, and weak evidence
— NOT to confirm that things work.

## Focus Areas (user specifies one)

| Scope | What to examine |
|-------|----------------|
| `packet <id>` | Packet definition, state entry, evidence notes |
| `area <id>` | All packets in area, closeout, drift assessment |
| `governance` | `wbs_cli.py`, `wbs_common.py`, `paths.py`, `engine.py`, `state_manager.py` |
| `security` | CLI arg parsing, env var handling, approval token validation |
| `evidence` | All completed packets — real paths vs vague claims |
| `general` | All of the above |

## Step 1: Context

```bash
python3 substrate/.governance/wbs_cli.py status
python3 substrate/.governance/wbs_cli.py briefing --format json
```

Also read: `substrate/docs/architecture.md`, `constitution.md`, `AGENTS.md`

## Step 2: Governance Integrity Checks

- Can state transitions bypass `require_wbs_mutation_approval()`? Find code paths that skip it.
- Are there CLI commands that write `wbs.json` / `wbs-state.json` directly without going through the engine?
- Can an agent complete a packet owned by another agent? Is ownership enforced at `done`?
- Are precondition/dependency checks enforced at `claim` time?
- Are there env var injection paths via `WBS_PROJECT` or `WBS_CHANGE_APPROVAL`?
- Can the `projects/sandbox` directory be used to escape main-project enforcement?

## Step 3: Evidence Quality Checks

For every completed packet in scope:
```bash
python3 substrate/.governance/wbs_cli.py log 50
python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json
```

- Does the `notes` field cite specific file paths? Or is it vague ("implemented the thing")?
- Do cited paths actually exist on disk?
- Is `--risk none` used with no justification, or is there real reasoning?
- Are validation check results stated (e.g. "10/10 tests pass")?

## Step 4: Code Security Checks

Search for dangerous patterns:
```bash
grep -rn "shell=True" substrate/.governance/
grep -rn "os.system(" substrate/.governance/
grep -rn "subprocess.run.*shell" substrate/.governance/
```

- Are file paths validated before write operations?
- Any hardcoded secrets, tokens, or absolute paths?

## Step 5: State Integrity Check

```bash
python3 substrate/.governance/wbs_cli.py validate
```

Read `substrate/.governance/wbs-state.json` directly:
- Packets in `in_progress` with no `started_at`?
- Log entries with implausible timestamps or gaps?
- Any `recovery: true` flags or direct-edit fingerprints?

## Step 6: Active Probing in Sandbox

Run adversarial tests in the sandbox — never against real state:

```bash
# Spin up isolated sandbox
python3 substrate/scripts/sandbox.py create

# Attempt bypass: claim without approval
python3 substrate/.governance/wbs_cli.py --project sandbox claim <packet_id> red-team-codex

# Attempt structure mutation without token
python3 substrate/.governance/wbs_cli.py --project sandbox add-area GUARD-TEST "Guard Test"
# Expect: WBS mutation approval required

# Teardown
python3 substrate/scripts/sandbox.py destroy
```

## Step 7: Report

```
## Red Team Review — [Scope] — [Date]

### Critical Findings (block next packet completion)
| # | Finding | Location | Evidence |

### Medium Findings (fix in current area)
| # | Finding | Location | Evidence |

### Low / Informational
| # | Finding | Location | Evidence |

### What Held Up
- Controls and guardrails that correctly blocked adversarial actions

### Recommendations
1. ...

### Next Steps
- [ ] <action> — owner: <agent>
```

## Step 8: Log Critical Findings (optional)

```bash
python3 substrate/.governance/wbs_cli.py break-fix-open RED-TEAM-<N> "codex" "<finding title>" --severity critical --note "<detail>"
```
