"""Turn the Stage 1 spec's examples into an independent pytest acceptance suite.

These tests come from the chat AI's spec, NOT from the coding AI, so the Stage 2 tool
cannot "grade its own homework". Regenerated on every pipeline run.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = json.loads((ROOT / "handoff" / "spec.json").read_text())

out = ROOT / "generated" / "test_acceptance.py"
out.write_text(
    '"""AUTO-GENERATED from handoff/spec.json by tools/gen_acceptance_tests.py. Do not edit."""\n'
    "import json\n"
    "import pytest\n"
    "from validator import validate\n\n"
    f"EXAMPLES = json.loads({json.dumps(json.dumps(spec['examples']))})\n\n\n"
    '@pytest.mark.parametrize("ex", EXAMPLES, ids=[e["name"] for e in EXAMPLES])\n'
    "def test_spec_example(ex):\n"
    '    assert validate(ex["input"]) == ex["expected_errors"]\n'
)
print(f"Wrote {out.relative_to(ROOT)} with {len(spec['examples'])} acceptance tests")
