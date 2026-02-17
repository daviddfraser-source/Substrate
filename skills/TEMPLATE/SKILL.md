# Skill Name

## Purpose
One paragraph describing the problem this skill solves and when to use it.

## Inputs
- Required input 1
- Required input 2

## Outputs
- Primary artifact(s) produced
- Evidence artifact(s) for WBS packet notes

## Preconditions
- Tool/runtime prerequisites
- Required files or environment variables

## Workflow
1. Validate prerequisites.
2. Execute primary command(s).
3. Validate outputs.
4. Record evidence paths.

## Commands
```bash
# Primary run
./skills/<skill-name>/scripts/run.sh

# Smoke check
./skills/<skill-name>/scripts/smoke.sh
```

## Failure Modes and Fallbacks
- Failure mode 1: detection and mitigation
- Failure mode 2: detection and mitigation

## Validation
- Expected success signals
- Expected report/output locations

## Evidence Notes Template
`Evidence: <artifact-path-1>, <artifact-path-2>`

## References
- Upstream tool/documentation links
