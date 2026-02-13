# Skill Sandbox Abstraction

## Implemented Modes
- `SubprocessSandbox` (baseline minimum isolation)
- `ContainerSandbox` (interface placeholder for hardened runtime rollout)

## Module
- `src/governed_platform/skills/sandbox.py`

## Design
- All skill execution goes through `SandboxInterface`.
- Permission checks run before command execution.
- Additional sandbox backends can be added without changing governance logic.
