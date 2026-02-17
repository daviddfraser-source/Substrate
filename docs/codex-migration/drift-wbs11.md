# Drift Assessment: WBS 11.0 Git-Native Governance

## Scope Reviewed
- Level-2 area: `11.0`
- Packet range: `UPG-052` through `UPG-059`
- Included streams: Git-native contract, commit protocol, auto-commit modes, linkage verification/export, branch helpers, CI enforcement, reconstruction, and rollout hardening docs
- Excluded: upstream non-Git governance streams (`1.0`-`10.0`) except where referenced for compatibility

## Expected vs Delivered
- Expected outcomes:
  - formal Git-native governance contract with compatibility model
  - structured commit protocol helpers and parser validation
  - optional auto-commit transitions with disabled/advisory/strict behavior
  - event-to-commit linkage metadata and verification/export commands
  - branch-per-packet helper workflow (opt-in)
  - CI integration for protocol/linkage checks
  - closeout tag convention and reconstruction tooling
  - rollout metrics, migration sequence, and rollback runbook
- Delivered outcomes:
  - all expected outcomes implemented and documented across CLI/module/tests/docs
  - CI workflow now executes Git-native governance checks
  - rollout and release checklist include Git-native evidence and rollback commands
- Variance summary:
  - no packet-level scope expansion beyond `11.0`
  - reconstruction command correctly errors in non-git worktrees (documented behavior), validated fully in temp-repo tests

## Drift Assessment
- Process drift observed: low
  - packet transitions tracked through CLI lifecycle updates and dependency order was preserved.
- Requirements drift observed: low
  - findings-driven Git-native packet set was implemented as defined in WBS.
- Implementation drift observed: low to medium
  - strict-mode rollback semantics for post-commit tag failures remain warning-based due immutable commit boundary; behavior is explicit and documented.
- Overall drift rating: low

## Evidence Reviewed
- Governance evidence:
  - `.governance/wbs-state.json` transition history for `UPG-052`..`UPG-059`
  - `.governance/wbs.json` packet definitions/dependencies for area `11.0`
- Core artifacts reviewed:
  - `src/governed_platform/governance/git_ledger.py`
  - `.governance/wbs_cli.py`
  - `.governance/git-governance.json`
  - `.github/workflows/test.yml`
  - `docs/codex-migration/git-native-governance.md`
  - `docs/codex-migration/git-native-rollout.md`
  - `docs/governance-workflow-codex.md`
  - `docs/release-checklist-codex.md`
  - `docs/logging.md`
- Test/validation evidence:
  - `pytest -q tests/test_git_commit_protocol.py tests/test_git_auto_commit.py tests/test_git_ledger_linkage.py tests/test_git_branch_packet_flow.py tests/test_git_ci_governance.py tests/test_git_reconstruction.py tests/test_governance_policy.py` (passing during execution; subsets executed per packet)
  - `python3 .governance/wbs_cli.py validate` (passed after each packet close)

## Residual Risks
- Repositories without stable git identity/config can produce elevated advisory warnings.
- Strict mode can block lifecycle progress during transient git auth/protection outages.
- Branch-per-packet workflow may increase operational overhead if adopted indiscriminately.

## Immediate Next Actions
- Pilot `advisory + auto-commit on` in a real git-backed operator repo and monitor warning rate against rollout targets.
- Promote to strict only after sustained `git-verify-ledger --strict` pass results.
- Capture first production reconstruction snapshot (`git-reconstruct`) and closeout-tag evidence in release records.

## Notes
- Cryptographic hashing beyond existing log hash-chain mode is not required for this assessment.
