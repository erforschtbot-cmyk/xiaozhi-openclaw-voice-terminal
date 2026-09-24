#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
voice_workspace="${OPENCLAW_VOICE_WORKSPACE:-$HOME/.openclaw/workspace-voice}"
voice_agent_dir="${OPENCLAW_VOICE_AGENT_DIR:-$HOME/.openclaw/agents/voice/agent}"

mkdir -p \
  "$HOME/.local/bin" \
  "$voice_workspace/skills/alexa-smart-home" \
  "$voice_workspace/skills/azeroth-gm-voice" \
  "$voice_agent_dir/workshop-skills/azeroth-server-control"

install -m 0755 "$repo_dir/scripts/openclaw-voice-skill-action" \
  "$HOME/.local/bin/openclaw-voice-skill-action"
install -m 0644 "$repo_dir/voice/AGENTS.md" "$voice_workspace/AGENTS.md"
install -m 0644 "$repo_dir/voice/skills/alexa-smart-home/SKILL.md" \
  "$voice_workspace/skills/alexa-smart-home/SKILL.md"
install -m 0644 "$repo_dir/voice/skills/azeroth-gm-voice/SKILL.md" \
  "$voice_workspace/skills/azeroth-gm-voice/SKILL.md"
install -m 0644 "$repo_dir/voice/skills/azeroth-server-control/SKILL.md" \
  "$voice_agent_dir/workshop-skills/azeroth-server-control/SKILL.md"

"$HOME/.local/bin/openclaw-voice-skill-action" --self-test
"$repo_dir/scripts/apply-openclaw-german-confirmation.py"
"$repo_dir/scripts/apply-openclaw-voice-skill-policy.py"
"$repo_dir/scripts/verify-openclaw-german-confirmation.py"
"$repo_dir/scripts/verify-openclaw-voice-skill-policy.py"

echo "Voice policy installed and verified. Restart openclaw-gateway.service to activate it."
