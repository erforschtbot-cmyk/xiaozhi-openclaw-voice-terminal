# Jarvis: Waveshare XiaoZhi als OpenClaw-Sprachterminal

Dieses private Repository enthält **alle projektspezifischen Dateien und Anleitungen**,
um das funktionierende Jarvis-System auf einem leeren Linux-/OpenClaw-Host exakt
wiederherzustellen — so, wie es am **2026-09-26** auf dem Referenzhost läuft.

## Was hier drin ist

| Bestandteil | Datei(en) |
|---|---|
| Firmware-Patches gegen den gepinnten Upstream | `firmware/patches/` |
| Bestätigte Firmware-Images (Wiederherstellungsanker) | `firmware/prebuilt/` |
| Aufgelöste Abhängigkeiten des Firmware-Builds | `firmware/dependencies.lock` |
| Bridge-Skript 1 (Python, WebSocket-Server) | `gateway/server.py` |
| Bridge-Skript 2 (Node, Gateway-Helper) | `gateway/openclaw-talk-realtime.mjs` |
| OpenClaw-`dist`-Patches für den Voice-Pfad | `scripts/apply-openclaw-voice-dist-patches.py` |
| systemd-Userdienst | `systemd/` |
| Bau-/Flash-/Installationsskripte | `scripts/` |
| Prüfsummen | `CHECKSUMS.sha256` |
| Verbindliche Versionen und Pins | `VERSIONS.md` |

Quellen und Anleitungen only — keine Laufzeitdaten, keine Zugangsdaten, keine
WLAN-Passwörter. Siehe „Sicherheitsgrenzen" weiter unten.

## Architektur

```text
Waveshare ESP32-S3-Touch-LCD-4B
  ├─ Wakeword (wn9_jarvis_tts), Mikrofon, Lautsprecher, Display, Geräte-MCP
  └─ WebSocket :8765
          ↓
Python-Bridge  (server.py, systemd: jarvis-realtime-bridge.service)
  ├─ Opus-Audio zum/vom Gerät, Nachhör-Fenster, OTA auf :8766
  └─ startet pro Äußerung: node openclaw-talk-realtime.mjs
          ↓
OpenClaw Gateway  (wss://127.0.0.1:18789)
  └─ Talk / OpenAI GPT-Live (gpt-live-1-codex, Stimme cove)
       ├─ beantwortet einfache Gesprächsanfragen direkt
       └─ ruft bei Werkzeugbedarf den OpenClaw-Agenten auf
          ↓
OpenClaw-Werkzeuge, Skills, Hostzugriff
```

**Zwei Skripte, klar getrennt:**

1. `gateway/server.py` — dauerhafter WebSocket-Server auf Port 8765/8766.
2. `gateway/openclaw-talk-realtime.mjs` — Kindprozess von `server.py`, wird **pro
   Äußerung** neu gestartet, verbindet zum Gateway.

Die Firmware enthält **keinen OpenAI-Schlüssel**. Anmeldung und Schlüssel bleiben
auf dem OpenClaw-Host.

## Neuinstallation in richtiger Reihenfolge

1. [`docs/01-HOST-INSTALLATION.md`](docs/01-HOST-INSTALLATION.md)
2. [`docs/02-FIRMWARE.md`](docs/02-FIRMWARE.md)
3. [`docs/03-OPENCLAW-PATCH.md`](docs/03-OPENCLAW-PATCH.md)
4. [`docs/04-TESTPLAN.md`](docs/04-TESTPLAN.md)
5. [`docs/05-FEHLERSUCHE.md`](docs/05-FEHLERSUCHE.md)
6. [`docs/06-BUILD-VERIFICATION.md`](docs/06-BUILD-VERIFICATION.md)

Für einen bereits eingerichteten Host genügt typischerweise:

```bash
./scripts/install-host.sh --public-host 192.168.178.143
./scripts/apply-openclaw-voice-dist-patches.py
./scripts/verify-host.sh
systemctl --user restart openclaw-gateway.service
```

## Bestätigte Firmware (Ist-Stand)

Aus dem Boot-Log und dem App-Deskriptor des Geräts gelesen:

| Merkmal | Wert |
|---|---|
| Project | `xiaozhi` |
| Version | `2.5.0` |
| Compile time | **Sep 23 2026 08:43:24** |
| ELF-SHA256 | `b6bf3e74cef7c701…` |
| ESP-IDF | `v6.1-803-g94639ab7251` |
| Board | `esp32-s3-touch-lcd-4b` |

Verwechslungsgefahr: Es existiert ein weiterer `xiaozhi 2.5.0`-Build vom
**22.09. 15:25** (ELF `dc80cd8c…`). Das ist **nicht** der laufende Stand.

## Wiederherstellungsanker

`firmware/prebuilt/` enthält zwei Dateien, die den laufenden Stand exakt abbilden:

| Datei | Inhalt | Schreibziel |
|---|---|---|
| `xiaozhi.bin` | Nur App-Partition (`ota_0`), byte-identisch zur laufenden App | `0x20000` |
| `merged-binary.bin` | Vollständiges 16-MiB-Image, **NVS auf 0xFF geleert** | `0x0` (nur Rettungsfall) |

Das NVS im Vollimage wurde bewusst geleert: Es enthält WLAN-Zugangsdaten im
Klartext. Ein geflashtes Gerät muss danach neu provisoniert werden.

## Sicherheitsgrenzen

- `firmware/prebuilt/xiaozhi.bin` wird bei `0x20000` geschrieben (nur App). NVS,
  WLAN und Assets bleiben erhalten.
- `firmware/prebuilt/merged-binary.bin` überschreibt das gesamte Flash und wird
  deshalb nur mit dem ausdrücklichen Schalter `--full-image-i-understand` geflasht.
- **Niemals** Zugangsdaten, `secrets.json`, OpenAI-/GitHub-Tokens oder
  WLAN-Passwörter in dieses Repository eintragen.
- Ein vollständiges Geräteimage enthält das NVS mit WLAN-Zugangsdaten. Vor jeder
  Veröffentlichung eines Rohimages prüfen: NVS-Bereich `0x9000`–`0xF000`.

## Referenzprüfsummen

Siehe [`CHECKSUMS.sha256`](CHECKSUMS.sha256).

## Herkunft

Der Aufbau entstand aus einer funktionierenden Basis; frühere vollständige
Neubauten konnten Mikrofon/Audio verlieren. Deshalb sind die Prebuilt-Images der
Recovery-Anker, und ein Neuaufbau muss erst den vollständigen Testplan bestehen.
Details: [`docs/06-BUILD-VERIFICATION.md`](docs/06-BUILD-VERIFICATION.md).
