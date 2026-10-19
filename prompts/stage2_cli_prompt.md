# Stage 2 Prompt: CLI / IDE AI agent (spec → code + tests)

**Use with:** any agentic coding tool that can read and write files: Claude Code CLI, Gemini CLI,
Codex CLI, aider, or the agent/chat mode in VS Code + Copilot / Cursor.
`run_pipeline.sh` sends this prompt automatically when `AI_CLI` is set.

---

Read `handoff/spec.json`. It is a machine-readable spec produced by an earlier AI stage and
validated against `schema/spec.schema.json`. Treat it as the single source of truth.

Create exactly two files:

1. `generated/validator.py`
   - Python 3.9+, standard library only.
   - Expose `validate(data: dict) -> list[str]` that returns a SORTED list of error codes taken
     ONLY from the spec (`fields[].rules[].code` and `cross_field_rules[].code`). Empty list = valid.
   - Also expose `MESSAGES: dict[str, str]` mapping every code to its `message`.
   - Semantics:
     * Missing required field → only `<field>.required` for that field.
     * Wrong type → only `<field>.type` for that field. `bool` is NOT an integer.
     * Optional fields that are absent are skipped.
     * `pattern` regexes are full-match (`re.fullmatch`).
     * Evaluate every field and every cross-field rule; collect ALL errors, do not stop early.
     * Cross-field rules apply only when `ticket_type` itself is valid.
   - Include a docstring and a `__main__` block that reads JSON from stdin and prints the errors
     with their messages.

2. `generated/test_validator.py`
   - pytest unit tests for edge cases NOT already in `spec.examples` (boundaries, empty strings,
     extra unknown fields ignored, MESSAGES covers every code).

Do not modify `handoff/`, `schema/`, `tools/` or `generated/test_acceptance.py`.
When done, run `python -m pytest generated -q` and fix any failures in your own files.
