# Agent Team Patterns (CLI-Oriented)

## Pattern 1: Lead + Specialists
Use for 10+ packets with clear domains.

Lead coordinates with:
- Frontend operator
- Backend operator
- Test/reliability operator

## Pattern 2: Parallel Workers
Use for many independent packets.

Lead manages queue distribution and rebalancing.

## Pattern 3: Pipeline
Use for strict phased work (`1.x -> 2.x -> 3.x ...`).

Each phase completes before next starts.

## Pattern 4: Solo + Assist
Use for small sets (<10 packets) with occasional helper support.

## Suggested Team Size by Project Scale

| Project Size | Typical Packet Count | Suggested Agents | Default Pattern |
|---|---:|---:|---|
| Small | 1-10 | 1-2 | Solo + Assist |
| Medium | 10-30 | 3-5 | Lead + Specialists |
| Large | 30+ | 5-8 | Parallel Workers + Pipeline |

Notes:
- Start with fewer agents, then scale only when ready queue depth supports parallel execution.
- Keep one lead responsible for dependency/risk decisions.

## Command Rhythm
Lead:
- `python3 .governance/wbs_cli.py ready`
- `python3 .governance/wbs_cli.py status`

Teammate:
- `claim` -> execute -> `done` -> optional `note`

## Anti-Patterns
- Too many operators for tiny packet sets
- No lead ownership for failure handling
- Missing evidence in packet notes
