# Jarvis: Waveshare XiaoZhi als OpenClaw-Sprachterminal

Dieses private Repository enthält **alle projektspezifischen Dateien und Änderungen**,
um das funktionierende Jarvis-System auf einem leeren Linux-/OpenClaw-Host wiederherzustellen.

## Bewiesene Funktionen

- Wakeword **Jarvis**
- Mikrofon und unmittelbare GPT-Live-Sprachausgabe
- OpenClaw-Voice-Agent mit Werkzeugen
- mehrteilige Werkzeugbestätigung: Auftrag → Rückfrage → deutsches „Ja“ → Ausführung
- eng vorautorisierte lokale Skill-Aktionen ohne redundante zweite Rückfrage
- direkte Geräte-MCP-Befehle für Lautstärke und Displayhelligkeit
- Folgefragen ohne neues Wakeword
- Displayzustände Bereitschaft / Zuhören / Sprechen
- 24/7-Betrieb ohne automatischen Schlaf oder PMIC-Abschaltung
- dauerhaftes WLAN-Reconnect mit gespeicherten Netzen

## Architektur

```text
Waveshare ESP32-S3
  ├─ Wakeword, Mikrofon, Lautsprecher, Display, Geräte-MCP
  └─ WebSocket :8765
          ↓
Python-Gateway auf dem OpenClaw-Host
          ↓
OpenClaw Talk / OpenAI GPT-Live
  ├─ beantwortet einfache Gesprächsanfragen direkt
  └─ ruft bei Werkzeugbedarf den OpenClaw-Voice-Agenten auf
          ↓
OpenClaw-Werkzeuge / Skills / Hostzugriff
```

Die Firmware enthält **keinen OpenAI-Schlüssel**. Anmeldung und Schlüssel bleiben auf
dem OpenClaw-Host.

## Neuinstallation in richtiger Reihenfolge

1. [`docs/01-HOST-INSTALLATION.md`](docs/01-HOST-INSTALLATION.md)
2. [`docs/02-FIRMWARE.md`](docs/02-FIRMWARE.md)
3. [`docs/03-OPENCLAW-PATCH.md`](docs/03-OPENCLAW-PATCH.md)
4. [`docs/04-TESTPLAN.md`](docs/04-TESTPLAN.md)
5. [`docs/05-FEHLERSUCHE.md`](docs/05-FEHLERSUCHE.md)
6. [`docs/06-BUILD-VERIFICATION.md`](docs/06-BUILD-VERIFICATION.md)
7. [`docs/07-VOICE-SKILL-POLICY.md`](docs/07-VOICE-SKILL-POLICY.md)

Für einen bereits eingerichteten Host genügt typischerweise:

```bash
./scripts/install-host.sh --public-host 192.168.178.143
./scripts/install-voice-policy.sh
./scripts/verify-host.sh
```

## Wichtige Sicherheitsgrenzen

- `firmware/prebuilt/xiaozhi.bin` wird bei `0x20000` geschrieben und erhält NVS,
  WLAN sowie die Jarvis-Assets.
- `firmware/prebuilt/merged-binary.bin` ist ein vollständiges Rettungsimage. Es kann
  NVS/WLAN überschreiben und wird deshalb nur mit dem ausdrücklichen Schalter
  `--full-image-i-understand` geflasht.
- Niemals Zugangsdaten, `secrets.json`, OpenAI-/GitHub-Tokens oder WLAN-Passwörter
  in dieses Repository eintragen.

## Referenzprüfsummen

Siehe [`CHECKSUMS.sha256`](CHECKSUMS.sha256). Das bestätigte Komplettimage hat:

```text
b5249aa28f936a6cae816b4b756363f81aaec33c7611efb826001708ccaa858b
```
