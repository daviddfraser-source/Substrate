import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.ontology import (  # noqa: E402
    validate_entity_type,
    validate_packet_dependency_ontology,
    validate_reference_ontology_pack,
    validate_relationship,
)


class OntologyTests(unittest.TestCase):
    def test_validate_builtin_entity_type(self):
        ok, msg = validate_entity_type("Packet")
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

    def test_reject_unknown_entity_type(self):
        ok, msg = validate_entity_type("Ticket")
        self.assertFalse(ok)
        self.assertIn("Unsupported entity type", msg)

    def test_dependency_relationship_requires_packet_to_packet(self):
        ok, msg = validate_relationship("Packet", "depends_on", "Packet")
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

        ok, msg = validate_relationship("Risk", "depends_on", "Packet")
        self.assertFalse(ok)
        self.assertIn("Invalid relationship", msg)

    def test_validate_packet_dependency_ontology(self):
        definition = {
            "packets": [
                {"id": "A", "entity_type": "Packet"},
                {"id": "B", "entity_type": "Packet"},
            ],
            "dependencies": {"B": ["A"]},
        }
        ok, msg = validate_packet_dependency_ontology("B", definition, definition["dependencies"])
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

    def test_reject_invalid_dependency_entity_pair(self):
        definition = {
            "packets": [
                {"id": "A", "entity_type": "Risk"},
                {"id": "B", "entity_type": "Packet"},
            ],
            "dependencies": {"B": ["A"]},
        }
        ok, msg = validate_packet_dependency_ontology("B", definition, definition["dependencies"])
        self.assertFalse(ok)
        self.assertIn("Invalid relationship", msg)

    def test_validate_reference_ontology_pack(self):
        pack = {
            "metadata": {
                "pack_id": "ontology.infrastructure.v1",
                "version": "1.0.0",
                "domain": "infrastructure-programme",
            },
            "entities": [
                {"id": "packet", "type": "Packet"},
                {"id": "risk", "type": "Risk"},
            ],
            "relationships": [
                {"type": "depends_on", "source_type": "Packet", "target_type": "Packet"},
                {"type": "mitigates", "source_type": "Risk", "target_type": "Packet"},
            ],
        }
        ok, msg = validate_reference_ontology_pack(pack)
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

    def test_reject_invalid_reference_ontology_pack(self):
        pack = {
            "metadata": {"pack_id": "x", "version": "1.0.0", "domain": "infrastructure-programme"},
            "entities": [{"id": "bad", "type": "Ticket"}],
            "relationships": [],
        }
        ok, msg = validate_reference_ontology_pack(pack)
        self.assertFalse(ok)
        self.assertIn("Unsupported entity type", msg)


if __name__ == "__main__":
    unittest.main()
