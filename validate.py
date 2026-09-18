#!/usr/bin/env python3
"""Validate the example intent records against the v0.1 JSON Schema.

Usage:
    python validate.py [example ...]

With no arguments every example file tracked in the repository is checked.
Exits non-zero if any example fails validation.
"""

import json
import pathlib
import sys

import jsonschema
import yaml

REPO = pathlib.Path(__file__).resolve().parent
SCHEMA = REPO / "prompt-intent-ir-v0.1.schema.json"
DEFAULT_EXAMPLES = [
    "example-current-request.intent.json",
    "example-current-request.intent.yaml",
]


def load(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def main(argv):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    names = argv or DEFAULT_EXAMPLES
    failures = 0

    for name in names:
        path = REPO / name
        if not path.exists():
            print(f"MISSING {name}")
            failures += 1
            continue

        errors = sorted(validator.iter_errors(load(path)), key=lambda e: e.path)
        if errors:
            failures += 1
            print(f"FAIL    {name}")
            for error in errors:
                location = "/".join(str(part) for part in error.path) or "<root>"
                print(f"        {location}: {error.message}")
        else:
            print(f"OK      {name}")

    if failures:
        print(f"\n{failures} file(s) failed validation.")
        return 1

    print(f"\nAll {len(names)} example(s) match the schema.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
