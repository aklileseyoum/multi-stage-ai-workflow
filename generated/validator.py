"""Validate event registrations using the rules in handoff/spec.json."""
import json
import re
import sys
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent.parent / "handoff" / "spec.json"
with SPEC_PATH.open(encoding="utf-8") as spec_file:
    SPEC = json.load(spec_file)

MESSAGES: dict[str, str] = {
    rule["code"]: rule["message"]
    for field in SPEC["fields"]
    for rule in field["rules"]
}
MESSAGES.update({rule["code"]: rule["message"] for rule in SPEC["cross_field_rules"]})


def _has_type(value, expected_type):
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return False


def _rule_matches(value, rule):
    params = rule["params"]
    kind = rule["kind"]
    if kind == "length":
        return params.get("min", 0) <= len(value) <= params.get("max", float("inf"))
    if kind == "range":
        return params.get("min", float("-inf")) <= value <= params.get("max", float("inf"))
    if kind == "enum":
        return value in params["values"]
    if kind == "pattern":
        return re.fullmatch(params["regex"], value) is not None
    return True


def _cross_rule_matches(rule, data):
    """Evaluate the spec's declarative conditional-presence cross-field rules."""
    match = re.fullmatch(
        r"If ([a-z_][a-z0-9_]*) is '([^']+)', "
        r"([a-z_][a-z0-9_]*) must (be present|not be present|be absent)\.",
        rule["description"],
    )
    if match is None:
        return False
    condition_field, condition_value, target_field, requirement = match.groups()
    if data.get(condition_field) != condition_value:
        return False
    if requirement == "be present":
        return target_field not in data
    return target_field in data


def validate(data: dict) -> list[str]:
    errors = []
    field_errors = {}

    for field in SPEC["fields"]:
        name = field["name"]
        rules = field["rules"]
        current_errors = []
        if name not in data:
            required_rule = next((rule for rule in rules if rule["kind"] == "required"), None)
            if field["required"] and required_rule is not None:
                current_errors.append(required_rule["code"])
        elif not _has_type(data[name], field["type"]):
            type_rule = next((rule for rule in rules if rule["kind"] == "type"), None)
            if type_rule is not None:
                current_errors.append(type_rule["code"])
        else:
            for rule in rules:
                if rule["kind"] not in ("required", "type") and not _rule_matches(data[name], rule):
                    current_errors.append(rule["code"])

        field_errors[name] = current_errors
        errors.extend(current_errors)

    ticket_type_valid = "ticket_type" in data and not field_errors.get("ticket_type")
    if ticket_type_valid:
        for rule in SPEC["cross_field_rules"]:
            if _cross_rule_matches(rule, data):
                errors.append(rule["code"])

    return sorted(errors)


if __name__ == "__main__":
    payload = json.load(sys.stdin)
    errs = validate(payload)
    if not errs:
        print("VALID")
    for code in errs:
        print(f"{code}: {MESSAGES[code]}")
    sys.exit(1 if errs else 0)
