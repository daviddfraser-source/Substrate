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

## Skills Harness

- `scripts/skills-smoke.sh`
  - Runs all `skills/*/scripts/smoke.sh` checks.
  - Writes report to `docs/codex-migration/skills-smoke-report.md`.

## Scaffold Bootstrap

- `scripts/init-scaffold.sh [template-path]`
  - Initializes `.governance/wbs.json` and `.governance/wbs-state.json` from template.
  - Default template path is `.governance/wbs.json` (clean baseline scaffold).
  - Runs governance validation and packet schema validation.

- `scripts/reset-scaffold.sh [template-path]`
  - Clears runtime scaffold artifacts (`wbs-state.json`, legacy activity log).
  - Re-initializes from the selected WBS source in one command.
  - Default template path is `.governance/wbs.json`.

## Skills Manifest

- `scripts/skills-manifest.sh list|enable|disable [skill-name]`
  - Lists and toggles optional skill modules declared in `skills/manifest.json`.

## Toolchain Setup

- `scripts/setup-tools.sh [--install]`
  - Records detected toolchain versions and optional install attempt output.

## Scaffold Verification

- `scripts/scaffold-check.sh`
  - One-command governance and scaffold contract verification.
  - Writes `docs/codex-migration/scaffold-check-report.md`.

- `scripts/template-integrity.sh`
  - Full template cleanliness validation including runtime tracking guard
    and isolated bootstrap smoke checks.

## Template Packaging

- `scripts/build-template-bundle.sh`
  - Builds a distributable scaffold template tarball under `dist/`.
  - Resets mutable WBS state in packaged output.
