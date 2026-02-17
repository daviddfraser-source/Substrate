# Git-Native Governance Rollout

## Scope

This playbook governs production rollout of Git-native governance features delivered in WBS `11.0`:
- structured commit protocol (`git-protocol`)
- optional lifecycle auto-commit (`git-governance-*`)
- event-to-commit linkage verification/export (`git-verify-ledger`, `git-export-ledger`)
- branch-per-packet helpers (`git-branch-open`, `git-branch-close`)
- closeout tags and history reconstruction (`git-reconstruct`)

## KPI Targets

| KPI | Target | Evidence Command | Owner | Cadence |
| --- | --- | --- | --- | --- |
| Protocol parse validity | 100% | `python3 .governance/wbs_cli.py git-protocol --json` | governance operator | each release |
| Ledger strict validity | 100% before strict mode enablement | `python3 .governance/wbs_cli.py --json git-verify-ledger --strict` | governance operator | daily during rollout |
| Auto-commit warning rate (advisory) | <= 5% of linked transitions | `python3 .governance/wbs_cli.py --json git-verify-ledger` | governance operator | daily |
| Closeout tag coverage (strict) | 100% for `closeout-l2` transitions | `python3 .governance/wbs_cli.py git-export-ledger <path>` | release manager | each closeout |
| Reconstruction fidelity | reconstructed records include all protocol commits in sample window | `python3 .governance/wbs_cli.py git-reconstruct --limit 500 --output <path>` | repository maintainer | weekly |

## Migration Sequence

### Phase 0: Preconditions

1. Confirm governance validation passes:
   - `python3 .governance/wbs_cli.py validate`
2. Confirm CI includes Git-native checks (workflow + tests).
3. Confirm operators know rollback commands in this document.

### Phase 1: Baseline (`disabled`, auto-commit off)

Commands:
- `python3 .governance/wbs_cli.py git-governance-mode disabled`
- `python3 .governance/wbs_cli.py git-governance-autocommit off`

Goals:
- verify no behavioral regression in baseline workflows.
- confirm `git-protocol` and `git-reconstruct` commands are operational.

Exit criteria:
- no lifecycle regressions from baseline.

### Phase 2: Advisory Enablement (`advisory`, auto-commit on)

Commands:
- `python3 .governance/wbs_cli.py git-governance-mode advisory`
- `python3 .governance/wbs_cli.py git-governance-autocommit on`

Goals:
- collect real warning telemetry without blocking work.
- tune `stage_files`, identity, and git environment assumptions.

Exit criteria:
- advisory warning rate at or below target.
- no unresolved systematic failure mode in warnings.

### Phase 3: Strict Pilot (`strict`, scoped operators)

Commands:
- `python3 .governance/wbs_cli.py git-governance-mode strict`

Goals:
- verify strict-mode transition blocking behavior under controlled load.
- ensure operators can recover cleanly from strict-mode failures.

Exit criteria:
- `git-verify-ledger --strict` valid for pilot scope.
- no unresolved strict-mode operational blockers.

### Phase 4: Strict General Availability

Commands:
- keep `strict` + auto-commit on for all operators.

Goals:
- enforce commit-linked lifecycle transitions as default execution path.

Exit criteria:
- release checklist fully satisfied for Git-native section.
- closeout tags and reconstruction reports are routinely generated.

## Rollback Plan

### Emergency rollback (all environments)

1. Disable strict blocking immediately:
   - `python3 .governance/wbs_cli.py git-governance-mode advisory`
2. If needed, disable auto-commit entirely:
   - `python3 .governance/wbs_cli.py git-governance-autocommit off`
3. Re-run baseline integrity checks:
   - `python3 .governance/wbs_cli.py validate`
   - `python3 .governance/wbs_cli.py --json verify-log`

### Mode-specific rollback notes

- `strict` -> `advisory`:
  - use when commit creation fails due transient git environment issues.
- `advisory` -> `disabled`:
  - use when warning volume blocks signal quality or causes operator confusion.
- branch helper rollback:
  - stop using `git-branch-open/close`; continue lifecycle transitions on mainline branch.

## Residual Risks

- repositories without reliable git identity/config may experience advisory warning spikes.
- strict mode can block execution if local git auth or branch protection is misconfigured.
- branch-per-packet helpers can add operational overhead for small or urgent patches.

## Ownership

- Governance operator: mode changes, daily ledger verification.
- Repository maintainer: CI integrity, reconstruction reports.
- Release manager: closeout tag coverage and release checklist sign-off.
