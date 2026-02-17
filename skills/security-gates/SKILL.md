# security-gates

## Purpose
Run baseline security gates in one workflow using Semgrep, Trivy, and Gitleaks.

## Inputs
- Repository source tree
- Optional policy env vars:
  - `SECURITY_FAIL_ON_SEMGREP`
  - `SECURITY_FAIL_ON_TRIVY`
  - `SECURITY_FAIL_ON_GITLEAKS`

## Outputs
- `docs/codex-migration/skills/security-gates-report.md`
- `docs/codex-migration/skills/security/semgrep.json`
- `docs/codex-migration/skills/security/trivy.json`
- `docs/codex-migration/skills/security/gitleaks.json`

## Preconditions
- `semgrep`, `trivy`, `gitleaks` on PATH.

## Workflow
1. Verify required tools.
2. Run all scanners and capture output.
3. Consolidate summary report.
4. Enforce fail policy.

## Commands
```bash
./skills/security-gates/scripts/smoke.sh
./skills/security-gates/scripts/run.sh
```

## Failure Modes and Fallbacks
- Missing tool: fail fast and report install gap.
- Scanner returns findings: report and fail based on configured policy.

## Validation
- All three output files exist.
- Consolidated report includes PASS/FAIL per tool.

## Evidence Notes Template
`Evidence: docs/codex-migration/skills/security-gates-report.md`

## References
- https://github.com/semgrep/semgrep
- https://github.com/aquasecurity/trivy
- https://github.com/gitleaks/gitleaks
