from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Set, Tuple

from substrate_core.validation import detect_dependency_cycle


def reverse_dependencies(dependencies: Dict[str, List[str]]) -> Dict[str, List[str]]:
    rev: Dict[str, List[str]] = {}
    for target, sources in dependencies.items():
        for source in sources:
            rev.setdefault(source, []).append(target)
    return rev


def upstream_nodes(packet_id: str, dependencies: Dict[str, List[str]]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    queue = deque(dependencies.get(packet_id, []))
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        out.append(node)
        for nxt in dependencies.get(node, []):
            if nxt not in seen:
                queue.append(nxt)
    return out


def downstream_nodes(packet_id: str, dependencies: Dict[str, List[str]]) -> List[str]:
    rev = reverse_dependencies(dependencies)
    seen: Set[str] = set()
    out: List[str] = []
    queue = deque(rev.get(packet_id, []))
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        out.append(node)
        for nxt in rev.get(node, []):
            if nxt not in seen:
                queue.append(nxt)
    return out


def impact_analysis(packet_id: str, dependencies: Dict[str, List[str]]) -> List[str]:
    return downstream_nodes(packet_id, dependencies)


def critical_path(dependencies: Dict[str, List[str]], packet_ids: Iterable[str]) -> List[str]:
    cycle = detect_dependency_cycle(dependencies)
    if cycle:
        return []

    nodes = list(dict.fromkeys([*packet_ids, *dependencies.keys(), *[d for vals in dependencies.values() for d in vals]]))
    parents = {n: list(dependencies.get(n, [])) for n in nodes}
    children = reverse_dependencies(dependencies)
    indegree = {n: len(parents.get(n, [])) for n in nodes}
    queue = deque([n for n in nodes if indegree[n] == 0])
    topo: List[str] = []
    while queue:
        n = queue.popleft()
        topo.append(n)
        for c in children.get(n, []):
            indegree[c] -= 1
            if indegree[c] == 0:
                queue.append(c)

    dist: Dict[str, int] = {n: 0 for n in nodes}
    prev: Dict[str, str] = {}
    for n in topo:
        for c in children.get(n, []):
            cand = dist[n] + 1
            if cand > dist.get(c, -1):
                dist[c] = cand
                prev[c] = n

    if not dist:
        return []
    end = max(dist, key=lambda k: dist[k])
    path = [end]
    while end in prev:
        end = prev[end]
        path.append(end)
    path.reverse()
    return path


def postgres_recursive_cte_queries() -> Dict[str, str]:
    return {
        "upstream": (
            "WITH RECURSIVE up AS ("
            " SELECT source_id, target_id FROM graph_edges WHERE target_id = %(packet_id)s"
            " UNION"
            " SELECT e.source_id, e.target_id FROM graph_edges e"
            " JOIN up ON e.target_id = up.source_id"
            ") SELECT DISTINCT source_id FROM up;"
        ),
        "downstream": (
            "WITH RECURSIVE down AS ("
            " SELECT source_id, target_id FROM graph_edges WHERE source_id = %(packet_id)s"
            " UNION"
            " SELECT e.source_id, e.target_id FROM graph_edges e"
            " JOIN down ON e.source_id = down.target_id"
            ") SELECT DISTINCT target_id FROM down;"
        ),
        "cycle_check": (
            "WITH RECURSIVE walk AS ("
            " SELECT source_id, target_id, ARRAY[source_id, target_id] AS path FROM graph_edges"
            " UNION ALL"
            " SELECT w.source_id, e.target_id, w.path || e.target_id FROM walk w"
            " JOIN graph_edges e ON e.source_id = w.target_id"
            " WHERE NOT e.target_id = ANY(w.path)"
            ") SELECT 1 FROM walk WHERE source_id = target_id LIMIT 1;"
        ),
    }


__all__ = [
    "reverse_dependencies",
    "upstream_nodes",
    "downstream_nodes",
    "impact_analysis",
    "critical_path",
    "postgres_recursive_cte_queries",
]
