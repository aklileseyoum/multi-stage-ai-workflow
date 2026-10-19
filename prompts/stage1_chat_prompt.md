# Stage 1 Prompt: Chat AI (requirements → structured spec)

**Use with:** any chat assistant (ChatGPT, Gemini, Claude.ai, Copilot Chat, etc.)
**How:** paste this prompt, then paste the contents of `input/requirements.md` under it.
Save the JSON reply as `handoff/spec.json`.

---

You are a requirements analyst. Convert the requirements below into a single JSON
object that conforms EXACTLY to this structure. Output ONLY the JSON, with no prose
and no markdown fences.

```
{
  "spec_version": "1.0",
  "name": "<snake_case name of the validator>",
  "description": "<one sentence>",
  "fields": [
    {
      "name": "<field name>",
      "type": "string | integer",
      "required": true | false,
      "rules": [
        { "code": "<field>.<rule>", "kind": "required|type|length|range|enum|pattern",
          "params": { ... }, "message": "<human readable>" }
      ]
    }
  ],
  "cross_field_rules": [
    { "code": "<field>.<rule>", "description": "<plain English condition>",
      "message": "<human readable>" }
  ],
  "examples": [
    { "name": "<short label>", "input": { ... },
      "expected_errors": ["<code>", "..."] }
  ]
}
```

Rules for you:
1. Every error code must be unique and use the form `field.rule`.
2. `params` per kind: length → {"min","max"}; range → {"min","max"};
   enum → {"values":[...]}; pattern → {"regex":"..."} (full-match regex); required/type → {}.
3. If a required field is missing, ONLY `<field>.required` is expected for that field.
   If a value has the wrong type, ONLY `<field>.type` is expected for that field.
4. Write at least 10 examples: 1+ fully valid (empty `expected_errors`), at least one per
   error code, and one that triggers several errors at once. Sort `expected_errors` alphabetically.
5. Do not invent requirements that are not stated.

REQUIREMENTS:
