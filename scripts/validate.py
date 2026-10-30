#!/usr/bin/env python3
"""Validate dataset against schema and perform integrity checks."""
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

SCHEMA_PATH = Path("schema.json")
DATA_PATH = Path("data/users.json")


def compute_checksum(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    print("=== Dataset Validation ===")

    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema not found: {SCHEMA_PATH}", file=sys.stderr)
        return 1
    if not DATA_PATH.exists():
        print(f"ERROR: Data file not found: {DATA_PATH}", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA_PATH.read_text())
    data = json.loads(DATA_PATH.read_text())

    # Schema validation
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        print("Schema validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err.message} (path: {list(err.path)})", file=sys.stderr)
        return 1

    print("Schema validation: PASSED")

    # Extra integrity checks
    ids = [item["id"] for item in data]
    if len(ids) != len(set(ids)):
        print("ERROR: Duplicate IDs found", file=sys.stderr)
        return 1
    print("Uniqueness check: PASSED")

    checksum = compute_checksum(DATA_PATH)
    print(f"Data checksum (SHA-256): {checksum}")
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
