"""Quality gate between Stage 1 and Stage 2.

Checks that the chat AI's output is valid JSON, matches the schema, and is internally
consistent (unique codes, examples only reference known codes, all codes exercised).
Exit code 0 = OK to hand off; 1 = send the errors back to the chat AI.
"""
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent


def check(spec_path: Path) -> list[str]:
    problems = []
    try:
        spec = json.loads(spec_path.read_text())
    except json.JSONDecodeError as e:
        return [f"Not valid JSON: {e}"]

    schema = json.loads((ROOT / "schema" / "spec.schema.json").read_text())
    for err in jsonschema.Draft202012Validator(schema).iter_errors(spec):
        loc = "/".join(map(str, err.absolute_path)) or "<root>"
        problems.append(f"Schema: {loc}: {err.message}")
    if problems:
        return problems

    codes = [r["code"] for f in spec["fields"] for r in f["rules"]]
    codes += [r["code"] for r in spec["cross_field_rules"]]
    dupes = {c for c in codes if codes.count(c) > 1}
    if dupes:
        problems.append(f"Duplicate error codes: {sorted(dupes)}")

    known, used = set(codes), set()
    for ex in spec["examples"]:
        exp = ex["expected_errors"]
        unknown = set(exp) - known
        if unknown:
            problems.append(f"Example '{ex['name']}' uses unknown codes {sorted(unknown)}")
        if exp != sorted(exp):
            problems.append(f"Example '{ex['name']}': expected_errors not sorted")
        used |= set(exp)

    if not any(not ex["expected_errors"] for ex in spec["examples"]):
        problems.append("No fully valid example provided")
    untested = known - used
    if untested:
        problems.append(f"Codes never exercised by an example: {sorted(untested)}")
    return problems


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "handoff" / "spec.json"
    issues = check(path)
    if issues:
        print("SPEC REJECTED. Paste these back into the chat AI to fix:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    spec = json.loads(path.read_text())
    print(f"SPEC OK: {len(spec['fields'])} fields, "
          f"{len(spec['cross_field_rules'])} cross-field rules, {len(spec['examples'])} examples")
