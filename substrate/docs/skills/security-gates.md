# security-gates Skill Operation

## Purpose
Run Semgrep, Trivy, and Gitleaks checks as a unified gate.

## Local Workflow
```bash
./skills/security-gates/scripts/smoke.sh
./skills/security-gates/scripts/run.sh
```

## CI Workflow
- GitHub Actions job: `skills-security-gates-ci`
- Includes:
  - `returntocorp/semgrep-action`
  - `aquasecurity/trivy-action`
  - `gitleaks/gitleaks-action`

## Evidence Artifacts
- `docs/codex-migration/skills/security-gates-report.md`
- `docs/codex-migration/skills/security/`
