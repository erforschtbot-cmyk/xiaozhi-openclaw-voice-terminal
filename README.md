# Jarvis: Waveshare XiaoZhi als OpenClaw-Sprachterminal

Dieses Repository enthält **alle projektspezifischen Dateien und Anleitungen**,
um das funktionierende Jarvis-System auf einem leeren Linux-/OpenClaw-Host exakt
wiederherzustellen — so, wie es am **2026-09-27** auf dem Referenzhost läuft.

> **Variante: Cloud (Realtime-Stimme).** Hören/Denken/Sprechen laufen über ein
> OpenAI-Realtime-Modell (`gpt-live-1-codex`, Stimme `cove`).
>
> Die **komplett lokale Variante** (Erkennung mit Whisper, Stimme mit Piper, kein
> Audio an die Cloud) steht in
> [`erforschtbot-cmyk/xiaozhi-openclaw-local-voice`](https://github.com/erforschtbot-cmyk/xiaozhi-openclaw-local-voice).
> Die **Firmware ist in beiden Repos identisch** — es unterscheidet sich nur die
> Host-Konfiguration.

Anleitung für Menschen und KI-Agenten (Aufbau, Test, Fehlersuche):
[Forum-Beitrag](https://www.erforscht.com/forum/index.php?thread/501-anleitung-xiaozhi-jarvis-als-openclaw-sprachterminal-cloud-lokal/).

## Was hier drin ist

| Bestandteil | Datei(en) |
|---|---|
| Firmware-Patches gegen den gepinnten Upstream | `firmware/patches/` |
| Board-spezifisches animiertes OpenClaw-Gesicht | im XiaoZhi-Patch unter `jarvis_face_display.*` |
| Wiederherstellungs-Watchdog (im Firmware-Patch) | `firmware/patches/xiaozhi-esp32-openclaw.patch` |
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
  └─ startet Helfer: node openclaw-talk-realtime.mjs (konstante Session-Schlüssel)
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
2. `gateway/openclaw-talk-realtime.mjs` — Kindprozess von `server.py`. Pro Äußerung
   wird ein Helfer gestartet/weiterverwendet; er verbindet zum Gateway. Der
   **Talk-Session-Schlüssel ist dabei konstant** (siehe unten), sodass alle
   Äußerungen in **derselben** OpenClaw-Session landen.

## Dauerhafte Talk-Sitzung (Ist-Stand 27.09.2026)

`server.py` setzt seit dem 27.09.2026 **konstante** Schlüssel:

```python
OPENCLAW_TALK_SESSION_KEY    = self.args.session_key        # agent:voice:xiaozhi-realtime-v5
OPENCLAW_TALK_CONSULT_SESSION_KEY = self.args.consult_session_key  # agent:allgemein:xiaozhi-realtime-v5
```

Vorher hing an beiden Schlüsseln eine UUID (`…-{turn_id}` bzw. `…-{session_id}`).
Damit wurde für **jede** Äußerung beziehungsweise **jeden** Werkzeug-Aufruf eine
frische Session aufgebaut.

Folgen des Wechsels auf konstante Schlüssel (belegt im Betrieb):

- **Werkzeug-Antworten kommen spürbar schneller** (näher an Alexa): die Sitzung
  bleibt warm, der Prompt-Cache greift (`cacheRead` in den Tool-Turns), es entfällt
  der Aufbau einer neuen Session pro Frage.
- **Kein `SqliteTranscriptMutationConflictError` mehr** auf frischen Transkripten,
  weil Zwischenansage und Consult nicht länger gegen ein neues Transkript laufen.
- **Kein Wachstum an `xiaozhi-realtime-v5-…`-Sessions pro Werkzeugfrage** durch den
  Session-Schlüssel selbst (neue Session-IDs entstehen nur noch über den
  Geräte-Reconnect, siehe `docs/05-FEHLERSUCHE.md`).

Zum Zurücksetzen des Experiments: in `server.py` die beiden Zuweisungen wieder auf
`f"{self.args.session_key}-{self.turn_id}"` und
`f"{self.args.consult_session_key}-{self.session_id}"` setzen.

Ergänzend wurde `is_interim_text()` von einem Präfix-Vergleich (`startswith`) auf
eine **geschlossene Liste reiner Zwischenansagen** umgestellt. Eine zu einer
Nachricht verwachsene Zwischenansage+Antwort („I’ll check that request. Es ist 01:02
Uhr.“) erhält dadurch korrekt `stream_end`; siehe `docs/05-FEHLERSUCHE.md`.

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
| Compile time | **Sep 28 2026 13:08:52** |
| ELF-SHA256 | `c30048b5f32545b3d596fb45089a0ab2e0db6b29d94cefdd724f023e11f937cd` |
| ESP-IDF | `v6.1` |
| Board | `esp32-s3-touch-lcd-4b` |
| Sprache | `de-DE` |

Dieser Stand enthält den **Wiederherstellungs-Watchdog**, das animierte,
board-spezifische OpenClaw-Gesicht (siehe `docs/02-FIRMWARE.md`) und den Eingriff,
dass das **Wachwort-Audio nicht mehr an den Server** geschickt wird
(`CONFIG_SEND_WAKE_WORD_DATA=n`). Mikrofon, Erkennung und Mithören sind davon
nicht betroffen.

Der Stand **vor** diesem Eingriff liegt als `firmware/prebuilt/previous/xiaozhi.bin`
(`Sep 27 2026 14:13:36`, ELF `77fd991a…`) — ein Befehl als Rückweg.

Verwechslungsgefahr: Es existieren weitere `xiaozhi 2.5.0`-Builds, u. a. der
vorherige bewährte Stand **23.09. 08:43** (ELF `b6bf3e74…`) und ein weiterer vom
**22.09. 15:25** (ELF `dc80cd8c…`). Weder Version noch Projektname unterscheiden
sie — nur Compile-Zeit und ELF-Hash.

## Wiederherstellungsanker

`firmware/prebuilt/` enthält den aktuellen, am Gerät bestätigten Stand:

| Datei | Inhalt | Schreibziel |
|---|---|---|
| `xiaozhi.bin` | Nur App-Partition (`ota_0`) des laufenden Builds (Wachwort-Audio abgeschaltet) | `0x20000` |
| `merged-binary.bin` | Vollständiges Image, **NVS auf `0xFF` geleert** | `0x0` (nur Rettungsfall) |
| `previous/xiaozhi.bin` | Stand **vor** dem Wachwort-Eingriff (`77fd991a…`) | `0x20000` |
| `previous-watchdog-smiley/xiaozhi.bin` | Vorheriger Watchdog-Stand mit statischem Smiley (`2d817b23…`) | `0x20000` |
| `previous-no-watchdog/xiaozhi.bin` | Vorheriger bewährter Stand (`b6bf3e74…`), ohne Watchdog | `0x20000` |
| `previous-face-v2-30fps/xiaozhi.bin` | Direkter Rückweg zum Gesicht vor der finalen LVGL-Optimierung | `0x20000` |

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
