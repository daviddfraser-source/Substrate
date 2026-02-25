from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


BUILTIN_ENTITY_TYPES: Set[str] = {
    "Packet",
    "Risk",
    "Policy",
    "Agent",
    "Model",
    "Scenario",
    "Asset",
    "RuleVersion",
}

RELATIONSHIP_RULES: Dict[str, Set[Tuple[str, str]]] = {
    "depends_on": {("Packet", "Packet")},
    "controls": {("Policy", "Packet"), ("Policy", "Model"), ("Policy", "Asset")},
    "invalidates": {("RuleVersion", "Policy"), ("Policy", "Policy"), ("Packet", "Packet")},
    "mitigates": {("Risk", "Packet"), ("Risk", "Asset"), ("Risk", "Model")},
    "produces": {("Packet", "Asset"), ("Packet", "Model"), ("Scenario", "Risk")},
}


def packet_entity_type(packet: Dict[str, Any]) -> str:
    value = str(packet.get("entity_type") or "Packet").strip()
    return value or "Packet"


def validate_entity_type(entity_type: str, allowed_types: Optional[Iterable[str]] = None) -> Tuple[bool, str]:
    allowed = set(allowed_types or BUILTIN_ENTITY_TYPES)
    if entity_type not in allowed:
        return False, f"Unsupported entity type: {entity_type}"
    return True, "ok"


def validate_relationship(source_type: str, relationship: str, target_type: str) -> Tuple[bool, str]:
    allowed_pairs = RELATIONSHIP_RULES.get(relationship)
    if not allowed_pairs:
        return False, f"Unsupported relationship: {relationship}"
    if (source_type, target_type) not in allowed_pairs:
        return (
            False,
            f"Invalid relationship: {source_type} -[{relationship}]-> {target_type}",
        )
    return True, "ok"


def validate_packet_dependency_ontology(
    packet_id: str,
    definition: Dict[str, Any],
    dependencies: Dict[str, List[str]],
) -> Tuple[bool, str]:
    packets = {str(p.get("id") or ""): p for p in definition.get("packets", []) if isinstance(p, dict)}
    source = packets.get(packet_id)
    if not source:
        return False, f"Packet {packet_id} not found in definition"

    source_type = packet_entity_type(source)
    ok, msg = validate_entity_type(source_type)
    if not ok:
        return False, msg

    for dep_id in dependencies.get(packet_id, []):
        target = packets.get(dep_id)
        if not target:
            return False, f"Dependency target not found in definition: {dep_id}"
        target_type = packet_entity_type(target)
        ok, msg = validate_entity_type(target_type)
        if not ok:
            return False, msg
        ok, msg = validate_relationship(source_type, "depends_on", target_type)
        if not ok:
            return False, msg
    return True, "ok"


def validate_reference_ontology_pack(pack: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(pack, dict):
        return False, "Ontology pack must be an object"
    metadata = pack.get("metadata", {})
    if not isinstance(metadata, dict):
        return False, "metadata must be an object"
    for key in ("pack_id", "version", "domain"):
        if not str(metadata.get(key) or "").strip():
            return False, f"metadata.{key} is required"

    entities = pack.get("entities", [])
    if not isinstance(entities, list) or not entities:
        return False, "entities must be a non-empty array"
    for entity in entities:
        if not isinstance(entity, dict):
            return False, "entity record must be an object"
        if not str(entity.get("id") or "").strip():
            return False, "entity.id is required"
        etype = str(entity.get("type") or "").strip()
        ok, msg = validate_entity_type(etype)
        if not ok:
            return False, msg

    rels = pack.get("relationships", [])
    if not isinstance(rels, list):
        return False, "relationships must be an array"
    for rel in rels:
        if not isinstance(rel, dict):
            return False, "relationship record must be an object"
        rtype = str(rel.get("type") or "").strip()
        src = str(rel.get("source_type") or "").strip()
        dst = str(rel.get("target_type") or "").strip()
        if not rtype or not src or not dst:
            return False, "relationship requires type/source_type/target_type"
        ok, msg = validate_relationship(src, rtype, dst)
        if not ok:
            return False, msg
    return True, "ok"


__all__ = [
    "BUILTIN_ENTITY_TYPES",
    "RELATIONSHIP_RULES",
    "packet_entity_type",
    "validate_entity_type",
    "validate_relationship",
    "validate_packet_dependency_ontology",
    "validate_reference_ontology_pack",
]
