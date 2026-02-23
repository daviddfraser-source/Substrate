# Codex Command Recipes

## Initialize
`python3 .governance/wbs_cli.py init templates/wbs-codex-refactor.json`

## Find next work
`python3 .governance/wbs_cli.py ready`

## Claim and complete
`python3 .governance/wbs_cli.py claim CDX-2-1 codex-lead`
`python3 .governance/wbs_cli.py done CDX-2-1 codex-lead "Delivered artifact: docs/codex-migration/command-map.md"`

## Update notes after done
`python3 .governance/wbs_cli.py note CDX-2-1 codex-lead "Added extra evidence: <path>"`

## Close out a Level-2 area with drift assessment
`python3 .governance/wbs_cli.py closeout-l2 2 codex-lead docs/codex-migration/drift-wbs2.md "Area complete and reviewed"`

## Report
`python3 .governance/wbs_cli.py status`
`python3 .governance/wbs_cli.py log 30`
