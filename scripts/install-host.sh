#!/usr/bin/env bash
# Installiert die Jarvis-Bridge vollstaendig aus diesem Repository.
#
# WICHTIG: Das Installationsverzeichnis ist NICHT frei waehlbar. Der
# Gateway-Patch (dist/handlers-*.mjs) importiert zwei Module per absolutem
# Pfad aus /home/openclaw/.local/share/jarvis-realtime-bridge/. Ein anderer
# Pfad bricht den Schnellweg und die Raum-/Session-Bindung.
set -euo pipefail

usage() {
  echo "Usage: $0 --public-host LAN_IP [--install-dir PATH]" >&2
  echo "" >&2
  echo "  --public-host  LAN-Adresse des Bridge-Rechners (Rueckfall fuer die OTA-URL)" >&2
  echo "  --install-dir  Standard: \$HOME/.local/share/jarvis-realtime-bridge" >&2
  echo "                 Muss dem Pfad in dist/handlers-*.mjs entsprechen." >&2
  exit 2
}

public_host=""
install_dir="${XDG_DATA_HOME:-$HOME/.local/share}/jarvis-realtime-bridge"
while (($#)); do
  case "$1" in
    --public-host) public_host="${2:-}"; shift 2 ;;
    --install-dir) install_dir="${2:-}"; shift 2 ;;
    *) usage ;;
  esac
done
[[ -n "$public_host" ]] || usage
[[ "$install_dir" == /home/openclaw/.local/share/jarvis-realtime-bridge ]] || {
  echo "This baseline requires /home/openclaw/.local/share/jarvis-realtime-bridge; see docs/00-START-HIER.md" >&2
  exit 1
}

for command_name in python3 node systemctl; do
  command -v "$command_name" >/dev/null || { echo "Missing command: $command_name" >&2; exit 1; }
done

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$install_dir" "$HOME/.config/systemd/user"

# --- Laufzeitcode: ALLE Module, nicht nur das Einstiegsprogramm ------------
# server.py importiert room_command; openclaw-talk-realtime.mjs importiert
# voice-turn-context.mjs; smart-home-router.mjs importiert room-command.mjs;
# der Gateway-Patch importiert scoped-smart-home-router.mjs und
# voice-turn-context.mjs. Fehlt eine dieser Dateien, startet die Bridge nicht
# oder der Schnellweg faellt still aus.
install -m 0644 "$repo_dir/gateway/server.py"                  "$install_dir/server.py"
install -m 0644 "$repo_dir/gateway/room_command.py"            "$install_dir/room_command.py"
install -m 0644 "$repo_dir/gateway/piper_speaker.py"           "$install_dir/piper_speaker.py"
install -m 0755 "$repo_dir/gateway/openclaw-talk-realtime.mjs" "$install_dir/openclaw-talk-realtime.mjs"
install -m 0644 "$repo_dir/gateway/local-voice.mjs"            "$install_dir/local-voice.mjs"
install -m 0644 "$repo_dir/gateway/local_stt.mjs"              "$install_dir/local_stt.mjs"
install -m 0644 "$repo_dir/gateway/voice-turn-context.mjs"     "$install_dir/voice-turn-context.mjs"
install -m 0644 "$repo_dir/gateway/room-command.mjs"           "$install_dir/room-command.mjs"
install -m 0644 "$repo_dir/gateway/room-router.mjs"            "$install_dir/room-router.mjs"
install -m 0644 "$repo_dir/gateway/smart-home-router.mjs"      "$install_dir/smart-home-router.mjs"
install -m 0644 "$repo_dir/gateway/scoped-smart-home-router.mjs" "$install_dir/scoped-smart-home-router.mjs"
install -m 0644 "$repo_dir/gateway/refresh-alexa-catalog.mjs"  "$install_dir/refresh-alexa-catalog.mjs"
# Foto-Weg: Bild-Consult zum Agenten (Kamera in der Firmware bereits enthalten).
install -m 0755 "$repo_dir/gateway/photo-consult.mjs"          "$install_dir/photo-consult.mjs"
install -m 0644 "$repo_dir/gateway/requirements.txt"           "$install_dir/requirements.txt"

# --- Konfiguration, die vorhanden sein MUSS -------------------------------
# room-map.json ist keine Laufzeitdatei: ohne sie bekommt kein Geraet einen
# Raum und "Licht an" landet in keinem Raum. Sie gehoert ins Repo.
# Preserve a deployment's own MAC/room configuration on repeated installs.
if [[ ! -e "$install_dir/room-map.json" ]]; then
  install -m 0644 "$repo_dir/gateway/room-map.json" "$install_dir/room-map.json"
fi
# Verification scripts depend on these offline tests being installed too.
for test_file in "$repo_dir"/gateway/test-*.mjs "$repo_dir"/gateway/test_*.py; do
  install -m 0644 "$test_file" "$install_dir/"
done
# Install the optional catalog units, but do not contact the reference ioBroker.
# Enable the timer only after configuring the user's own endpoint.
install -m 0644 "$repo_dir/systemd/jarvis-alexa-catalog.service" "$HOME/.config/systemd/user/"
install -m 0644 "$repo_dir/systemd/jarvis-alexa-catalog.timer" "$HOME/.config/systemd/user/"

# Modus-Schalter: Existenz der Datei schaltet den alten Bridge-Direktpfad AUS.
# Sie muss vorhanden sein, damit genau EIN Ausfuehrer (die Gateway-Weiche)
# schaltet. Leere Datei ist korrekt.
install -m 0644 "$repo_dir/gateway/disable-smart-home-fastpath" "$install_dir/disable-smart-home-fastpath"

# --- Umschalter lokal <-> realtime ----------------------------------------
install -m 0755 "$repo_dir/gateway/voice-mode"                 "$install_dir/voice-mode"
install -m 0644 "$repo_dir/gateway/profile-local.service"      "$install_dir/profile-local.service"
install -m 0644 "$repo_dir/gateway/profile-realtime.service"   "$install_dir/profile-realtime.service"

# --- Python-Umgebung -------------------------------------------------------
python3 -m venv "$install_dir/.venv"
"$install_dir/.venv/bin/python" -m pip install --upgrade pip
"$install_dir/.venv/bin/python" -m pip install -r "$install_dir/requirements.txt"

# --- systemd-Unit ---------------------------------------------------------
unit_target="$HOME/.config/systemd/user/jarvis-realtime-bridge.service"
python3 - "$repo_dir/systemd/jarvis-realtime-bridge.service.in" "$unit_target" "$install_dir" "$public_host" <<'PY'
from pathlib import Path
import sys
source, target, install_dir, public_host = sys.argv[1:]
text = Path(source).read_text()
text = text.replace("@INSTALL_DIR@", install_dir).replace("@PUBLIC_HOST@", public_host)
Path(target).write_text(text)
PY

systemctl --user daemon-reload
systemctl --user enable --now jarvis-realtime-bridge.service
systemctl --user is-active --quiet jarvis-realtime-bridge.service

# --- Selbstpruefung: jede Datei, die eine Importkette braucht --------------
missing=0
for required in server.py room_command.py piper_speaker.py openclaw-talk-realtime.mjs \
                local-voice.mjs local_stt.mjs voice-turn-context.mjs room-command.mjs \
                room-router.mjs smart-home-router.mjs scoped-smart-home-router.mjs \
                refresh-alexa-catalog.mjs photo-consult.mjs requirements.txt room-map.json \
                disable-smart-home-fastpath voice-mode; do
  if [[ ! -e "$install_dir/$required" ]]; then
    echo "MISSING: $install_dir/$required" >&2
    missing=1
  fi
done
if (( missing )); then
  echo "Installation unvollstaendig — siehe docs/00-DATEIBESTAND.md" >&2
  exit 1
fi

# --- Noch nicht vorhandene, aber erwartete Laufzeitdateien ----------------
# Werden beim ersten Betrieb automatisch erzeugt; hier nur benennen, damit
# niemand sie fuer vergessen haelt.
cat <<EOF
Installed and active: jarvis-realtime-bridge.service

Automatisch erzeugt (noch nicht vorhanden ist normal):
  $install_dir/active-room.json          Raum des zuletzt sprechenden Geraets
  $install_dir/last-utterance.json        gesprochener Satz fuer die Weiche
  $install_dir/last-alexa-command.json    Dedupe-Fenster (8 s)
  $install_dir/voice-bindings/            Session-zu-Geraet-Bindung
  $install_dir/alexa-device-catalog.json  erst nach refresh-alexa-catalog.mjs

Noch einzurichten (externe Voraussetzungen):
  $HOME/.openclaw/ssl/gateway.crt         Gateway-Zertifikat
  $HOME/.local/share/piper-voices/        Piper-Stimmen (nur fuer --tts-local)
  Gateway-dist-Patches                    scripts/apply-openclaw-voice-dist-patches.py
EOF
