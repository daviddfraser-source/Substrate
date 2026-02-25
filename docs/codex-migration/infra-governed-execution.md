# Infrastructure as Governed Packets

## Principle
Infrastructure setup is not a prerequisite outside governance; it is executed and evidenced as packetized work.

## Recommended Packet Sequence
1. Build image baseline (`INFRA-1-1`)
2. Start compose stack (`INFRA-1-2`)
3. Validate Kubernetes manifests (`INFRA-1-3`)
4. Publish infra report and closeout (`INFRA-1-4`)

## Evidence Conventions
- Build evidence: `reports/infra/build.log`
- Compose evidence: `reports/infra/compose-health.log`
- K8s evidence: `reports/infra/k8s-validate.log`
- Closeout report: `docs/codex-migration/infra-validation-report.md`

## Validation Commands
```bash
python3 .governance/wbs_cli.py validate --strict
python3 .governance/wbs_cli.py validate-packet templates/wbs-infra-governed.json
python3 -m unittest tests/test_k8s_profile.py -v
```
