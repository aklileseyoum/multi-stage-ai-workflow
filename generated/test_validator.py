"""Extra edge-case tests written by the Stage 2 CLI agent (beyond spec examples)."""
import json
from pathlib import Path

import pytest
from validator import MESSAGES, validate

SPEC = json.loads((Path(__file__).resolve().parent.parent / "handoff" / "spec.json").read_text())
BASE = {"full_name": "Abebe Kebede", "email": "a@b.com", "age": 30, "ticket_type": "standard"}


def with_(**kw):
    d = dict(BASE)
    d.update(kw)
    return d


def test_messages_cover_every_spec_code():
    codes = {r["code"] for f in SPEC["fields"] for r in f["rules"]}
    codes |= {r["code"] for r in SPEC["cross_field_rules"]}
    assert set(MESSAGES) == codes


@pytest.mark.parametrize("name,ok", [("A" * 2, True), ("A" * 60, True), ("A" * 61, False), ("", False)])
def test_name_length_boundaries(name, ok):
    assert (validate(with_(full_name=name)) == []) is ok


@pytest.mark.parametrize("age,ok", [(16, True), (120, True), (15, False), (121, False), (0, False), (-5, False)])
def test_age_boundaries(age, ok):
    assert (validate(with_(age=age)) == []) is ok


def test_unknown_fields_are_ignored():
    assert validate(with_(newsletter=True)) == []


def test_empty_strings_fail_value_rules():
    assert validate(with_(email="")) == ["email.format"]
    assert validate(with_(ticket_type="")) == ["ticket_type.enum"]
    assert validate(with_(student_id="")) == ["student_id.format"]
    assert validate(with_(promo_code="")) == ["promo_code.format"]


def test_student_id_needs_exact_six_digits():
    base = with_(ticket_type="student")
    assert validate({**base, "student_id": "STU1234567"}) == ["student_id.format"]
    assert validate({**base, "student_id": "stu123456"}) == ["student_id.format"]


def test_promo_length_boundaries():
    assert validate(with_(promo_code="ABCDE")) == []
    assert validate(with_(promo_code="ABCDEFGHIJ")) == []
    assert validate(with_(promo_code="ABCD")) == ["promo_code.format"]
    assert validate(with_(promo_code="ABCDEFGHIJK")) == ["promo_code.format"]


def test_no_cross_field_rule_when_ticket_invalid():
    assert validate(with_(ticket_type="platinum", promo_code="SAVE10")) == ["ticket_type.enum"]


def test_empty_payload_reports_all_required():
    assert validate({}) == ["age.required", "email.required", "full_name.required", "ticket_type.required"]


def test_result_is_sorted():
    errs = validate({"full_name": "", "email": "x", "age": 1, "ticket_type": "nope"})
    assert errs == sorted(errs)
