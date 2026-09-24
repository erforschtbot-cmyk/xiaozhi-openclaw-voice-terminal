# 1. Host installieren

## Voraussetzungen

- Linux mit systemd-Userdiensten
- OpenClaw `2026.9.5`
- Node.js und npm
- Python 3 mit `venv`
- `libopus`
- funktionierender OpenClaw-Gateway auf `wss://127.0.0.1:18789`
- ein in OpenClaw angemeldeter OpenAI-Provider mit `gpt-live-1-codex`

Arduino IDE ist für dieses Projekt **nicht** erforderlich. Die Firmware ist ein
ESP-IDF-Projekt und wird reproduzierbar im Docker-Container gebaut.

Arch Linux:

```bash
sudo pacman -S --needed nodejs npm python python-pip opus docker git
```

Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y nodejs npm python3 python3-venv libopus0 docker.io git
```

OpenClaw installieren und anmelden:

```bash
npm install -g openclaw@2026.9.5
openclaw --version
openclaw models auth login --provider openai
openclaw gateway status
```

Die OpenClaw-Anmeldung ist interaktiv. Keine `secrets.json` von einem fremden Host
kopieren und keine Tokens ins Repository schreiben.

## Gateway installieren

Repository klonen und den tatsächlich im LAN erreichbaren Host angeben:

```bash
git clone git@github.com:erforschtbot-cmyk/xiaozhi-openclaw-voice-terminal.git
cd xiaozhi-openclaw-voice-terminal
./scripts/install-host.sh --public-host 192.168.178.143
```

Der Installer:

1. kopiert Gateway und Realtime-Helper nach
   `~/.local/share/xiaozhi-openclaw-gateway`;
2. erzeugt eine Python-Umgebung und installiert exakt `requirements.txt`;
3. installiert den systemd-Userdienst;
4. aktiviert und startet ihn;
5. verändert keine OpenClaw-Zugangsdaten.

Danach:

```bash
systemctl --user status xiaozhi-openclaw-gateway.service
journalctl --user -u xiaozhi-openclaw-gateway.service -n 100 --no-pager
ss -ltn | grep -E ':8765|:8766'
```

Ports:

- `8765/tcp`: XiaoZhi-WebSocket
- `8766/tcp`: lokale OTA-Konfiguration, die das Gerät auf Port 8765 verweist

Der Host muss aus dem WLAN des ESP32 unter der bei `--public-host` angegebenen
Adresse erreichbar sein.

