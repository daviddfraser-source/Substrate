from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Set, Tuple


def _adjacency(state: Dict[str, Any]) -> Dict[str, List[str]]:
    adj: Dict[str, List[str]] = {}
    for rel in state.get("relationships", []):
        if not isinstance(rel, dict):
            continue
        src = str(rel.get("source_entity_id") or "").strip()
        dst = str(rel.get("target_entity_id") or "").strip()
        if not src or not dst:
            continue
        adj.setdefault(src, []).append(dst)
        adj.setdefault(dst, []).append(src)
    return adj


def _reachable_entities(state: Dict[str, Any], scope_entity_id: str, depth: int) -> Set[str]:
    token = str(scope_entity_id or "").strip()
    if not token:
        return set()
    adj = _adjacency(state)
    visited: Set[str] = {token}
    q = deque([(token, 0)])
    while q:
        node, d = q.popleft()
        if d >= depth:
            continue
        for nxt in adj.get(node, []):
            if nxt in visited:
                continue
            visited.add(nxt)
            q.append((nxt, d + 1))
    return visited


def retrieve_scoped(
    state: Dict[str, Any],
    *,
    scope_entity_id: str,
    depth: int = 2,
    max_chunks: int = 10,
    max_tokens: int = 1200,
) -> Tuple[bool, str, Dict[str, Any]]:
    if not str(scope_entity_id or "").strip():
        return False, "scope_entity_id is required", {}
    if depth < 0:
        return False, "depth must be >= 0", {}
    if max_chunks <= 0 or max_tokens <= 0:
        return False, "max_chunks and max_tokens must be positive", {}

    allowed_entities = _reachable_entities(state, scope_entity_id, depth)
    docs = state.get("documents", [])
    retrieved: List[Dict[str, Any]] = []
    token_count = 0
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        entity = str(doc.get("entity_id") or "").strip()
        if entity not in allowed_entities:
            continue
        text = str(doc.get("content") or "").strip()
        if not text:
            continue
        words = text.split()
        if not words:
            continue
        chunk_words = words[: min(len(words), 80)]
        candidate_tokens = len(chunk_words)
        if token_count + candidate_tokens > max_tokens:
            break
        retrieved.append(
            {
                "document_id": doc.get("id"),
                "entity_id": entity,
                "chunk_text": " ".join(chunk_words),
                "token_count": candidate_tokens,
                "relevance_score": 1.0,
            }
        )
        token_count += candidate_tokens
        if len(retrieved) >= max_chunks:
            break

    trace = {
        "scope_entity_id": scope_entity_id,
        "depth": depth,
        "max_chunks": max_chunks,
        "max_tokens": max_tokens,
        "retrieved_count": len(retrieved),
        "retrieved_tokens": token_count,
        "timestamp": datetime.now().isoformat(),
        "documents": [{"document_id": x.get("document_id"), "entity_id": x.get("entity_id")} for x in retrieved],
    }
    state.setdefault("retrieval_log", []).append(trace)
    return True, "ok", {"chunks": retrieved, "trace": trace}


__all__ = ["retrieve_scoped"]
