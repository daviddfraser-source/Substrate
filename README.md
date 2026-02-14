# Substrate

[![Tests](https://img.shields.io/badge/tests-python%20unittest-informational)](#testing)
[![Open in GitHub Codespaces](https://img.shields.io/badge/dev-GitHub%20Codespaces-24292f?logo=github)](https://codespaces.new/daviddfraser-source/Substrate)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Formal packet/state-machine orchestration for multi-agent software delivery, with dependency gating, file-backed state, and auditable lifecycle logs.

Constitutional governance baseline: `constitution.md`.

## Why This Exists

Teams using agentic workflows need deterministic coordination mechanics when multiple actors touch the same work graph.

This project provides a technical control plane for common failure modes:
- work drift between planned and delivered outcomes
- race conditions during packet claiming/completion
- weak audit trails for ownership, transitions, and evidence

The approach is intentionally simple and inspectable:
- explicit packet lifecycle (`pending`, `in_progress`, `done`, `failed`, `blocked`)
- dependency graph gating before execution
- file-based state in `.governance/wbs-state.json`
- append-only activity log entries on lifecycle events
- atomic writes and lock-aware update flows

## Get Started

**Option A: GitHub Codespaces**
Open in Codespaces using the badge above, then run:

```bash
python3 start.py
```

**Option B: Local**

```bash
python3 start.py
```

Requirements: Python 3.8+.

> [!NOTE]
> This is a **Template Repository**. The intended workflow is to **Clone and Own**: once you instantiate this template, you own the entire codebase, including the governance tools in `src/governed_platform`. You are free to modify them, but be aware that deviating from the core logic may affect future updates or standard tooling compatibility.


## How It Works

### Packet Lifecycle

```text
PENDING --claim--> IN_PROGRESS --done--> DONE
                      |                   |
                    fail             unblocks
                      v             downstream
                   FAILED ---> BLOCKED
```

### Runtime Architecture

```mermaid
flowchart LR
  A[Packet Definition\n.governance/wbs.json] --> B[State Machine\n.wbs_cli.py]
  B --> C[State Store\n.governance/wbs-state.json]
  B --> D[Activity Log\nstate.log[]]
  B --> E[Dependency Gate]
  E --> B
  B --> F[Dashboard/API\n.governance/wbs_server.py]
  C --> F
```

Locking and write safety:
- packet transitions write via temp file + atomic replace
- state mutations use lock-aware flows where supported
- CLI remains source-of-truth for lifecycle transitions

### Project Structure (Where to put your code)

This template separates **governance tooling** from **user code**:

- `src/governed_platform/`: Contains the core Substrate logic (CLI, Server, State Machine). **Do not modify** unless you are upgrading the governance system itself.
- `src/app/`: **[YOUR CODE HERE]**. This is where your application logic, business rules, and agent implementations should reside.
- `tests/`: Add your application tests here.


## Commands

```bash
python3 .governance/wbs_cli.py ready
python3 .governance/wbs_cli.py claim IMP-001 codex-lead
python3 .governance/wbs_cli.py done IMP-001 codex-lead "Implemented and tested"
python3 .governance/wbs_cli.py note IMP-001 codex-lead "Evidence: docs/path.md"
python3 .governance/wbs_cli.py status
```

## Agent Support

### Claude Code

Claude reads `CLAUDE.md` at project open.

```bash
scripts/cc-ready
scripts/cc-claim <PACKET_ID>
scripts/cc-done <PACKET_ID> "evidence"
scripts/cc-status
```

Guide: `docs/claude-code-guide.md`

### Gemini

Gemini reads `GEMINI.md` at project open.

```bash
scripts/gc-ready
scripts/gc-claim <PACKET_ID>
scripts/gc-done <PACKET_ID> "evidence"
scripts/gc-status
```

### Codex

Use the same governance CLI directly:

```bash
python3 .governance/wbs_cli.py ready
python3 .governance/wbs_cli.py claim <PACKET_ID> codex-lead
```

### Human Operators

```bash
python3 start.py
```

### Other LLM Agents

Any agent that can execute shell commands can use:

```bash
python3 .governance/wbs_cli.py <command>
```

## Skills

| Skill | Technical Purpose |
|---|---|
| [`skills/agent-eval`](skills/agent-eval) | Prompt/eval harness integration for regression checks |
| [`skills/security-gates`](skills/security-gates) | Static/security scanning gate patterns |
| [`skills/pr-review-automation`](skills/pr-review-automation) | Automated reviewdog-style PR review workflows |
| [`skills/precommit-governance`](skills/precommit-governance) | Pre-commit governance and repository checks |
| [`skills/ui-regression`](skills/ui-regression) | Playwright critical-path UI regression workflow |
| [`skills/observability-baseline`](skills/observability-baseline) | Baseline telemetry and trace pipeline setup |
| [`skills/skill-authoring`](skills/skill-authoring) | Scaffold and lint custom skill packages |
| [`skills/mcp-catalog-curation`](skills/mcp-catalog-curation) | Evaluate and curate MCP/tool catalog entries |

## Templates

| Template | Use Case |
|---|---|
| `templates/wbs-codex-minimal.json` | Fast Codex scaffold bootstrap |
| `templates/wbs-codex-full.json` | Full scaffold/governance setup |
| `templates/wbs-codex-refactor.json` | Full profile with migration compatibility |

```bash
scripts/init-scaffold.sh templates/wbs-codex-full.json
```

See `docs/template-usage.md` for scaffold onboarding flow.

## Troubleshooting

- `Packet viewer API unavailable (HTTP 404)`
  - You are likely on the wrong server/port or an outdated server process.
  - Start dashboard from repo root with `python3 start.py --dashboard --port 8090` or `python3 .governance/wbs_server.py 8090`.

- `Failed to execute 'json' on 'Response'` / `Unexpected end of JSON input`
  - API route returned non-JSON (often from stale server route handling).
  - Restart dashboard server and retry on the correct port.

- `Not initialized. Run: python3 .governance/wbs_cli.py init .governance/wbs.json`
  - Initialize state file before dashboard/CLI lifecycle commands.

- Dependency not met when claiming a packet
  - Run `python3 .governance/wbs_cli.py ready` and complete upstream dependencies first.

- State file appears inconsistent after interruption
  - Re-open status with `python3 .governance/wbs_cli.py status`.
  - Re-run `python3 .governance/wbs_cli.py validate` and inspect `.governance/wbs-state.json` + recent log entries.

## Architecture Notes

Additional architecture rationale is in `docs/architecture.md`.

## Testing

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT.
