# Skills Manifest

Manifest file: `skills/manifest.json`

## Purpose
Enable scaffold users to run minimal or full skill sets without deleting skill packages.

## Commands
```bash
scripts/skills-manifest.sh list
scripts/skills-manifest.sh disable ui-regression
scripts/skills-manifest.sh enable ui-regression
```

## Notes
- Manifest controls enablement state only.
- Skill directories remain in repository even when disabled.
