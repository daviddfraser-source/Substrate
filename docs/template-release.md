# Template Release Packaging

## Local
```bash
./scripts/build-template-bundle.sh
```

Output:
- `dist/substrate-template-<timestamp>.tar.gz`

## CI Workflow
- `.github/workflows/template-release.yml`
- Triggers:
  - Manual (`workflow_dispatch`)
  - Tag push matching `template-v*`

## Packaging Notes
- Bundle includes scaffold files for template consumers.
- `.governance/wbs-state.json` is reset in the bundle to avoid shipping prior execution history.
