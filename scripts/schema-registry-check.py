#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from governed_platform.governance.schema_registry import SchemaRegistry


def main():
    registry_path = ROOT / ".governance" / "schema-registry.json"
    reg = SchemaRegistry.from_registry_file(registry_path, root=ROOT)
    required = [("packet", "1.0"), ("scaffold_config", "1.0")]
    for name, version in required:
        if not reg.validate_version(name, version):
            print(f"Schema version mismatch for {name}")
            return 1
        schema = reg.load_schema(name)
        if not isinstance(schema, dict):
            print(f"Invalid schema payload for {name}")
            return 1
    print("Schema registry validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
