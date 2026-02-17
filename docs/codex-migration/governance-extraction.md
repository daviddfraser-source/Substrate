# Governance Extraction Notes

WBS: `12.3`

## What Was Extracted
- Lifecycle state transitions into `src/governed_platform/governance/engine.py`:
  - `claim`
  - `done`
  - `note`
  - `fail` (with dependency block cascade)
  - `reset`
  - `ready`
  - `closeout_l2`
- State persistence abstraction:
  - `src/governed_platform/governance/state_manager.py`
- Governance interface contract:
  - `src/governed_platform/governance/interfaces.py`

## Goal
Move governance policy and state mutation out of CLI entrypoints so execution adapters can remain thin and replaceable.
