# Supervisor Authority Model

## Purpose
Introduce explicit authority separation so agents do not self-govern lifecycle transitions.

## Flow
Agent -> Supervisor -> Governance Engine -> State Manager

## Policy Baseline
- Agent identity required for mutating transitions.
- Completion transitions (`done`) require non-empty notes/evidence summary.

## Implementation
- `src/governed_platform/governance/supervisor.py`
  - `TransitionRequest`
  - `SupervisorInterface`
  - `SupervisorPolicy`
  - `DeterministicSupervisor`
