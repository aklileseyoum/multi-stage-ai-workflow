#!/usr/bin/env bash
# End-to-end runner: Chat AI output (handoff/spec.json) -> gate -> CLI AI -> tests.
#
# Tool-agnostic: set AI_CLI to ANY non-interactive coding agent command that accepts a prompt.
#   AI_CLI='claude -p --permission-mode acceptEdits'  ./run_pipeline.sh   # Claude Code
#   AI_CLI='gemini -y -p'                               ./run_pipeline.sh   # Gemini CLI
#   AI_CLI='codex exec --full-auto'                     ./run_pipeline.sh   # OpenAI Codex CLI
#   AI_CLI='aider --yes --message'                      ./run_pipeline.sh   # aider (any model)
# If AI_CLI is unset, Stage 2 is skipped and the committed generated/ code is tested (replay mode).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
LOG="logs/run_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee "$LOG") 2>&1

echo "== [1/4] Gate: validating Stage 1 (chat) output: handoff/spec.json"
python3 tools/validate_spec.py handoff/spec.json

echo "== [2/4] Generating independent acceptance tests from the spec"
python3 tools/gen_acceptance_tests.py

if [[ -n "${AI_CLI:-}" ]]; then
  echo "== [3/4] Stage 2: invoking CLI agent: $AI_CLI"
  # shellcheck disable=SC2086
  $AI_CLI "$(cat prompts/stage2_cli_prompt.md)"
else
  echo "== [3/4] Stage 2 skipped (AI_CLI not set): replaying committed generated/validator.py"
fi

echo "== [4/4] Running acceptance + unit tests"
python3 -m pytest generated -q

echo "== Demo: validating a sample registration"
echo '{"full_name":"Sara","email":"s@u.edu","age":20,"ticket_type":"vip","promo_code":"SAVE10"}' \
  | python3 generated/validator.py || true
echo "== PIPELINE PASSED. Log: $LOG"
