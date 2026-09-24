#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m py_compile "$repo_dir/gateway/server.py"
node --check "$repo_dir/gateway/openclaw-talk-realtime.mjs"
"$repo_dir/scripts/verify-openclaw-german-confirmation.py"
systemctl --user is-active openclaw-gateway.service
systemctl --user is-active xiaozhi-openclaw-gateway.service
ss -ltn | grep -E ':8765|:8766'
echo "Host verification passed"

