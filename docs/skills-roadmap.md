# Codex Skills Roadmap (WBS 10.0)

## Scope
Build and operationalize eight custom Codex skills for WBS/packet governance, quality, security, review automation, UX regression, observability, and MCP curation.

## Delivery Order
1. `agent-eval`
2. `security-gates`
3. `pr-review-automation`
4. `precommit-governance`
5. `ui-regression`
6. `observability-baseline`
7. `skill-authoring`
8. `mcp-catalog-curation`

## Cross-Skill Definition of Done
- Skill exists in `skills/<skill-name>/SKILL.md`.
- `README.md` exists with install/use prerequisites.
- At least one executable script exists in `skills/<skill-name>/scripts/`.
- Skill has a smoke command and expected output documented.
- Skill has failure modes and fallback behavior documented.
- Skill emits evidence path(s) for WBS packet notes.

## Skill-Specific Acceptance Criteria
### agent-eval
- Uses `promptfoo` for reproducible eval runs.
- Baseline suite and regression suite commands documented.
- Produces machine-readable summary artifact.

### security-gates
- Runs `semgrep`, `trivy`, and `gitleaks` in one command.
- Supports fail-on-high-severity policy.
- Produces consolidated security report artifact.

### pr-review-automation
- Uses `reviewdog` for changed-lines feedback.
- Supports local dry-run and CI mode.
- Outputs review summary artifact.

### precommit-governance
- Provides `.pre-commit-config.yaml` template and install instructions.
- Enforces WBS/packet schema + docs checks before commit.
- Supports manual run across repo.

### ui-regression
- Uses Playwright for WBS/packet critical-path checks.
- Includes one command for headed local run and headless CI run.
- Produces test report artifact.

### observability-baseline
- Defines OpenTelemetry event schema for packet lifecycle.
- Provides collector config and sample emitter instructions.
- Produces trace/log sample artifact.

### skill-authoring
- Generates new skill scaffold from a standard template.
- Enforces required sections and example commands.
- Includes lint/check command for generated skill quality.

### mcp-catalog-curation
- Defines MCP allowlist and review checklist.
- Supports approve/reject workflow with rationale.
- Produces curation decision artifact.

## Execution Plan (Mapped to WBS 10.x)
- `10.1-10.3`: roadmap, template contract, smoke harness.
- `10.4-10.19`: build + validate each skill pair.
- `10.20`: end-to-end integration, readiness report, and closeout.

## Risks and Controls
- Tool availability drift: pin tool versions where feasible.
- CI runtime volatility: keep smoke checks lightweight, deep checks optional.
- Governance drift: use mandatory evidence references in packet notes.
- UX drift: keep Playwright critical path checks in CI.
