# skill-authoring

## Purpose
Generate new skill scaffolds that comply with the repository skill contract.

## Inputs
- New skill name (kebab-case)
- Optional purpose text

## Outputs
- `skills/<new-skill>/SKILL.md`
- `skills/<new-skill>/README.md`
- `skills/<new-skill>/scripts/smoke.sh`
- `skills/<new-skill>/scripts/run.sh`

## Preconditions
- Shell and file permissions to create directories/files.

## Workflow
1. Validate skill name.
2. Copy template scaffold.
3. Replace placeholders.
4. Run scaffold lint.

## Commands
```bash
./skills/skill-authoring/scripts/smoke.sh
./skills/skill-authoring/scripts/new-skill.sh demo-skill "Demo purpose"
./skills/skill-authoring/scripts/lint-skill.sh skills/demo-skill/SKILL.md
```

## Failure Modes and Fallbacks
- Skill already exists: fail fast and require explicit overwrite decision.
- Invalid skill name: reject and request kebab-case.

## Validation
- New folder contains required files.
- Lint script validates required sections.

## Evidence Notes Template
`Evidence: skills/<new-skill>/SKILL.md, skills/<new-skill>/README.md`
