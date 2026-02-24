import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class AgentIdentity:
    agent_id: str
    tenant_id: str
    name: str
    mode: str
    created_at: float


@dataclass
class AgentActionLog:
    tenant_id: str
    agent_id: str
    action: str
    packet_id: str
    recorded_at: float


class AgentRegistry:
    def __init__(self, rate_limit_per_minute: int = 60):
        self._agents: Dict[Tuple[str, str], AgentIdentity] = {}
        self._keys: Dict[str, Tuple[str, str]] = {}
        self._logs: List[AgentActionLog] = []
        self._rate_limit_per_minute = rate_limit_per_minute

    def register_agent(self, tenant_id: str, name: str, mode: str) -> AgentIdentity:
        agent_id = f"agt_{secrets.token_hex(6)}"
        identity = AgentIdentity(agent_id=agent_id, tenant_id=tenant_id, name=name, mode=mode, created_at=time.time())
        self._agents[(tenant_id, agent_id)] = identity
        return identity

    def issue_api_key(self, tenant_id: str, agent_id: str) -> str:
        self._require_agent(tenant_id, agent_id)
        raw_key = secrets.token_urlsafe(24)
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        self._keys[key_hash] = (tenant_id, agent_id)
        return raw_key

    def rotate_api_key(self, tenant_id: str, agent_id: str) -> str:
        self._require_agent(tenant_id, agent_id)
        # Remove existing keys for this tenant+agent pair.
        stale = [hash_value for hash_value, pair in self._keys.items() if pair == (tenant_id, agent_id)]
        for hash_value in stale:
            del self._keys[hash_value]
        return self.issue_api_key(tenant_id, agent_id)

    def authenticate(self, tenant_id: str, api_key: str) -> str:
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        pair = self._keys.get(key_hash)
        if not pair:
            raise PermissionError("Invalid API key")
        key_tenant, agent_id = pair
        if key_tenant != tenant_id:
            raise PermissionError("Tenant isolation violation")
        return agent_id

    def log_action(self, tenant_id: str, agent_id: str, action: str, packet_id: str) -> AgentActionLog:
        self._require_agent(tenant_id, agent_id)
        self._enforce_rate_limit(tenant_id, agent_id)
        entry = AgentActionLog(
            tenant_id=tenant_id,
            agent_id=agent_id,
            action=action,
            packet_id=packet_id,
            recorded_at=time.time(),
        )
        self._logs.append(entry)
        return entry

    def claim_packet_endpoint(self, tenant_id: str, api_key: str, packet_id: str) -> Dict[str, str]:
        agent_id = self.authenticate(tenant_id, api_key)
        self.log_action(tenant_id, agent_id, "claim", packet_id)
        return {"ok": "true", "tenant_id": tenant_id, "agent_id": agent_id, "packet_id": packet_id, "action": "claim"}

    def action_logs(self, tenant_id: str = "") -> List[AgentActionLog]:
        if tenant_id:
            return [entry for entry in self._logs if entry.tenant_id == tenant_id]
        return list(self._logs)

    def _require_agent(self, tenant_id: str, agent_id: str) -> None:
        if (tenant_id, agent_id) not in self._agents:
            raise KeyError("Unknown agent identity")

    def _enforce_rate_limit(self, tenant_id: str, agent_id: str) -> None:
        now = time.time()
        floor = now - 60.0
        recent = [entry for entry in self._logs if entry.tenant_id == tenant_id and entry.agent_id == agent_id and entry.recorded_at >= floor]
        if len(recent) >= self._rate_limit_per_minute:
            raise PermissionError("Rate limit exceeded")
