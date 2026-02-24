# Governance Rule Versioning and Rollback

Date: 2026-02-24
Packet: PRD-5-4

## Lifecycle

- `proposed` (created)
- `active` (approved)

## Controls

- Version creation requires rationale
- Approval is explicit and actor-attributed
- Rollback creates a new version using prior active content
- Rollback requires rationale and explicit approval step

## Validation

- `python3 -m unittest tests/test_rule_versions.py`
