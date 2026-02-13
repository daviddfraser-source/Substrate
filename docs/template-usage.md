# Substrate Template Usage

## 1. Choose a Profile
- `templates/wbs-codex-minimal.json`: fast startup, minimal governance footprint.
- `templates/wbs-codex-full.json`: comprehensive scaffold setup.
- `templates/wbs-codex-refactor.json`: full profile with migration compatibility.

## 2. Bootstrap
```bash
scripts/init-scaffold.sh templates/wbs-codex-full.json
python3 .governance/wbs_cli.py ready
```

Or use guided onboarding:
```bash
python3 start.py --wizard-scaffold
```

## 3. Execute Lifecycle
```bash
python3 .governance/wbs_cli.py claim <packet_id> <agent>
python3 .governance/wbs_cli.py done <packet_id> <agent> "summary + evidence"
python3 .governance/wbs_cli.py note <packet_id> <agent> "updated evidence"
```

## 4. Verify Scaffold Health
```bash
scripts/scaffold-check.sh
```

## 5. Close Out Level-2 Areas
```bash
python3 .governance/wbs_cli.py closeout-l2 <area_id|n> <agent> docs/codex-migration/drift-wbs<area>.md "closeout note"
```

Use `docs/codex-migration/drift-assessment-template.md` for drift assessment structure.
