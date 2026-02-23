# mcp-catalog-curation

## Purpose
Curate MCP servers through a controlled allowlist and explicit risk review workflow.

## Inputs
- Candidate MCP server name
- Candidate URL/repository
- Review decision (`approve` or `reject`)
- Reviewer rationale

## Outputs
- Allowlist: `skills/mcp-catalog-curation/assets/allowlist.json`
- Decision records: `docs/codex-migration/skills/mcp-curation/*.md`

## Preconditions
- Reviewer has validated source authenticity and security posture.

## Workflow
1. Run smoke check for config presence.
2. Review candidate against checklist.
3. Record decision with rationale.
4. Update allowlist only for approved candidates.

## Commands
```bash
./skills/mcp-catalog-curation/scripts/smoke.sh
./skills/mcp-catalog-curation/scripts/decide.sh approve example-server https://example.org/repo "approved rationale"
./skills/mcp-catalog-curation/scripts/decide.sh reject risky-server https://example.org/risky "rejected rationale"
```

## Failure Modes and Fallbacks
- Missing rationale: reject command.
- Unknown decision type: reject command.

## Validation
- Decision file created for each review.
- Allowlist only changes on `approve`.

## Evidence Notes Template
`Evidence: skills/mcp-catalog-curation/assets/allowlist.json, docs/codex-migration/skills/mcp-curation/<decision-file>.md`

## References
- https://github.com/wong2/awesome-mcp-servers
