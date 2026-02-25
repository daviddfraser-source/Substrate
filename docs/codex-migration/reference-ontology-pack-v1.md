# Reference Ontology Pack v1 Contract

## Purpose

Define a stable ingestion contract for commercial/reference ontology packs so extension packs remain compatible with Substrate core typing and relationship invariants.

## Required Structure

```json
{
  "metadata": {
    "pack_id": "ontology.infrastructure.v1",
    "version": "1.0.0",
    "domain": "infrastructure-programme"
  },
  "entities": [
    {"id": "packet", "type": "Packet"}
  ],
  "relationships": [
    {"type": "depends_on", "source_type": "Packet", "target_type": "Packet"}
  ]
}
```

## Validation Rules

- `metadata.pack_id`, `metadata.version`, `metadata.domain` are required.
- `entities` must be non-empty and use built-in supported entity types.
- `relationships` must use supported relationship types and valid `(source_type, target_type)` pairs.
- Validation entrypoint: `substrate_core.ontology.validate_reference_ontology_pack`.

## Compatibility Notes

- Packs can add new entity records but cannot bypass core type checks.
- Relationship definitions must remain compatible with core relationship invariants.
- Incompatible packs are rejected at ingest/validation time.

## Sample Artifact

- `docs/codex-migration/reference-ontology-pack-v1-sample.json`
