# Agent Integration Contract

Date: 2026-02-24
Packet: PRD-5-1

## Capabilities Delivered

- Agent identity registry (`register_agent`)
- API key issuance and rotation (`issue_api_key`, `rotate_api_key`)
- Claim endpoint contract (`claim_packet_endpoint`)
- Action logging (`log_action`, `action_logs`)
- Tenant isolation and per-agent rate limiting

Implementation file: `src/app/agents.py`.

## Security Controls

- API keys are stored as SHA-256 hashes
- Tenant mismatch during authentication raises permission error
- Claim/action path is rate-limited per tenant+agent per minute

## Validation

Run:

- `python3 -m unittest tests/test_agents_registry.py`
