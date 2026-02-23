# Optional Command Aliases

These wrappers provide portable shorthand around the WBS CLI.

- `scripts/wbs-status`
- `scripts/wbs-ready`
- `scripts/wbs-claim <packet_id> <agent>`
- `scripts/wbs-done <packet_id> <agent> <notes> [none|declared] [risk-file]`
- `scripts/wbs-note <packet_id> <agent> <notes>`
- `scripts/cc-ready`
- `scripts/cc-claim <packet_id>`
- `scripts/cc-done <packet_id> <evidence> [none|declared] [risk-file]`
- `scripts/cc-status`
- `scripts/gc-done <packet_id> <evidence> [none|declared] [risk-file]`

They are optional convenience commands. The source of truth is:
`python3 .governance/wbs_cli.py ...`

## New Project Quick Init

```bash
scripts/init-scaffold.sh templates/wbs-codex-minimal.json
python3 .governance/wbs_cli.py ready
```

Reset setup quickly:

```bash
scripts/reset-scaffold.sh templates/wbs-codex-minimal.json
```

## Skills Harness

- `scripts/skills-smoke.sh`
  - Runs all `skills/*/scripts/smoke.sh` checks.
  - Writes report to `docs/codex-migration/skills-smoke-report.md`.

## Scaffold Bootstrap

- `scripts/init-scaffold.sh [template-path]`
  - Copies selected template into resident `.governance/wbs.json`.
  - Initializes `.governance/wbs-state.json` from resident definition.
  - Default template path is `.governance/wbs.json` (clean baseline scaffold).
  - Runs governance validation and packet schema validation before init.
  - Prints `briefing` output after successful init.

- `scripts/reset-scaffold.sh [template-path]`
  - Clears runtime scaffold artifacts (`wbs-state.json`, legacy activity log, residual risk register).
  - Re-initializes from the selected WBS source in one command.
  - Default template path is `.governance/wbs.json`.
  - Prints `briefing` output after successful reset.

## Skills Manifest

- `scripts/skills-manifest.sh list|enable|disable [skill-name]`
  - Lists and toggles optional skill modules declared in `skills/manifest.json`.

## Toolchain Setup

- `scripts/setup-tools.sh [--install]`
  - Records detected toolchain versions and optional install attempt output.

## E2E Run Capture

- `scripts/e2e-run.py --suite <name> --cmd "<command>" [--agent <id>] [--packet-id <id>] [--trigger local|ci|manual]`
  - Executes an E2E command and appends normalized run output to `.governance/e2e-runs.json`.
  - Writes run logs under `reports/e2e/` for dashboard artifact preview.

## Break-Fix Mode (CLI)

- `python3 .governance/wbs_cli.py break-fix-open <actor> <title> <description> [--severity v] [--packet id]`
- `python3 .governance/wbs_cli.py break-fix-start <fix_id> <actor>`
- `python3 .governance/wbs_cli.py break-fix-note <fix_id> <actor> <note> [--evidence a,b] [--findings x|y]`
- `python3 .governance/wbs_cli.py break-fix-resolve <fix_id> <actor> <summary> --evidence a,b`
- `python3 .governance/wbs_cli.py break-fix-list [--status s]`

Workflow guide: `docs/break-fix-workflow.md`

## Optional PRD Ideation (CLI)

- `python3 .governance/wbs_cli.py prd --output docs/prd/my-feature-prd.md`
- `python3 .governance/wbs_cli.py prd --from-json docs/prd/spec.json --output docs/prd/my-feature-prd.md --to-wbs .governance/wbs-prd-draft.json`

Template: `templates/prd-template.md`

## Scaffold Verification

- `scripts/scaffold-check.sh`
  - One-command governance and scaffold contract verification.
  - Writes `docs/codex-migration/scaffold-check-report.md`.

- `scripts/check-root-hygiene.sh`
  - Verifies root contains only approved landing files/directories.
  - Useful before release and in CI.

- `scripts/template-integrity.sh`
  - Full template cleanliness validation including runtime tracking guard
    and isolated bootstrap smoke checks.

## Clone Profiles

- `scripts/clone-profile.sh list|show|preview|apply <profile>`
  - Applies root cleanup profiles from `templates/clone-profiles/`.
- `scripts/post-clone-cleanup.sh --profile <codex-only|minimal|all-agents> [--yes]`
  - One-command post-clone cleanup with root hygiene verification.

## Template Packaging

- `scripts/build-template-bundle.sh`
  - Builds a distributable scaffold template tarball under `dist/`.
  - Resets mutable WBS state in packaged output.

## Git-Ready Snapshot Publishing

- `scripts/publish-git-ready.sh <snapshot-name>`
  - Publishes `dist/git-ready/<snapshot-name>` from current repo state.
  - Excludes generated template artifacts (`templates/ai-substrate/node_modules`, `dist`, `.next`, `coverage`).
