#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --public-host LAN_IP [--install-dir PATH]" >&2
  exit 2
}

public_host=""
install_dir="${XDG_DATA_HOME:-$HOME/.local/share}/xiaozhi-openclaw-gateway"
while (($#)); do
  case "$1" in
    --public-host) public_host="${2:-}"; shift 2 ;;
    --install-dir) install_dir="${2:-}"; shift 2 ;;
    *) usage ;;
  esac
done
[[ -n "$public_host" ]] || usage

for command_name in python3 node npm openclaw systemctl; do
  command -v "$command_name" >/dev/null || { echo "Missing command: $command_name" >&2; exit 1; }
done

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$install_dir" "$HOME/.config/systemd/user"
install -m 0644 "$repo_dir/gateway/server.py" "$install_dir/server.py"
install -m 0755 "$repo_dir/gateway/openclaw-talk-realtime.mjs" "$install_dir/openclaw-talk-realtime.mjs"
install -m 0644 "$repo_dir/gateway/requirements.txt" "$install_dir/requirements.txt"

python3 -m venv "$install_dir/.venv"
"$install_dir/.venv/bin/python" -m pip install --upgrade pip
"$install_dir/.venv/bin/python" -m pip install -r "$install_dir/requirements.txt"

unit_target="$HOME/.config/systemd/user/xiaozhi-openclaw-gateway.service"
python3 - "$repo_dir/systemd/xiaozhi-openclaw-gateway.service.in" "$unit_target" "$install_dir" "$public_host" <<'PY'
from pathlib import Path
import sys
source, target, install_dir, public_host = sys.argv[1:]
text = Path(source).read_text()
text = text.replace("@INSTALL_DIR@", install_dir).replace("@PUBLIC_HOST@", public_host)
Path(target).write_text(text)
PY

systemctl --user daemon-reload
systemctl --user enable --now xiaozhi-openclaw-gateway.service
systemctl --user is-active --quiet xiaozhi-openclaw-gateway.service
echo "Installed and active: xiaozhi-openclaw-gateway.service"

