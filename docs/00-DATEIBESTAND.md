# 0. Dateibestand — was existieren MUSS

Diese Datei ist für Agenten und Menschen, die das Repository **ohne jedes
Vorwissen** übernehmen. Sie beantwortet drei Fragen, die sonst nur mündlich
überliefert sind:

1. Welche Datei muss am Installationsort liegen?
2. Welche Datei entsteht beim Betrieb von selbst?
3. Welche Voraussetzung liegt außerhalb dieses Repositories?

Ist-Stand: **2026-10-19**, Referenzhost `cachyos-x8664`.

---

## Der Installationsort ist NICHT frei wählbar

```text
/home/openclaw/.local/share/jarvis-realtime-bridge
```

Grund: Der Gateway-Patch in `dist/handlers-*.mjs` importiert zwei Module per
**absolutem** Pfad:

```js
import { voiceTurnStorage, readVoiceBinding } from
  "file:///home/openclaw/.local/share/jarvis-realtime-bridge/voice-turn-context.mjs";
...
jarvisRouter = await import(
  "file:///home/openclaw/.local/share/jarvis-realtime-bridge/scoped-smart-home-router.mjs");
```

Ein anderer Pfad bricht den Schnellweg und die Raum-/Session-Bindung — **still**,
ohne Fehlermeldung: Die Sprachsteuerung funktioniert weiter, aber jeder
Schaltbefehl geht den langsamen KI-Weg. Wer den Ort ändert, muss die beiden
Importe im Handler mitziehen.

Deshalb ignoriert `scripts/install-host.sh --install-dir` zwar nicht, warnt aber
nicht: Der Parameter existiert nur für Tests. Im Betrieb bleibt der Pfad oben.

---

## Dateien, die am Installationsort liegen MÜSSEN

Alle stammen aus `gateway/` dieses Repositories. `install-host.sh` kopiert sie
vollständig; die Selbstprüfung am Ende bricht ab, wenn eine fehlt.

### Einstiegspunkte und Laufzeitcode

| Datei | Rolle | Wird importiert von |
|---|---|---|
| `server.py` | WebSocket-Server (8765) und OTA (8766); Einstiegspunkt | systemd |
| `room_command.py` | Raum-Map lesen, aktiven Raum veröffentlichen | `server.py` |
| `openclaw-talk-realtime.mjs` | Sprachhelfer als Kindprozess (Provider-Weg) | `server.py` |
| `voice-turn-context.mjs` | Session→Gerät→Raum-Bindung pro Verbindung | Helper **und** Gateway-Patch |
| `local-voice.mjs` | Sprachhelfer für den lokalen Weg (`--stt-local`) | `server.py` |
| `local_stt.mjs` | lokale Erkennung über Wyoming | `local-voice.mjs` |
| `piper_speaker.py` | lokale Sprachausgabe (`--tts-local`) | `server.py` |

### Weiche für Schaltbefehle

| Datei | Rolle | Wird importiert von |
|---|---|---|
| `smart-home-router.mjs` | Gerätekatalog, Klassifikation, Alexa-Aufruf | `scoped-smart-home-router.mjs`, `refresh-alexa-catalog.mjs` |
| `scoped-smart-home-router.mjs` | Weiche am Consult-Eingang (Marker `jarvis-safe-router-v1`) | **Gateway-Patch** (absoluter Pfad) |
| `room-command.mjs` | Raum-Voranstellung im JS-Pfad | `smart-home-router.mjs`, `scoped-smart-home-router.mjs` |
| `room-router.mjs` | eigenständige Raum-Voranstellung (nur Tests) | nur `test-room-router.mjs` |
| `refresh-alexa-catalog.mjs` | erzeugt den Gerätekatalog aus Alexa2 | systemd-Timer |

### Konfiguration (kein Laufzeitdatum!)

| Datei | Rolle | Fehlt sie, dann … |
|---|---|---|
| `room-map.json` | Raum pro Gerät (Schlüssel: MAC aus dem Handshake) | bekommt **kein** Gerät einen Raum; „Licht an" landet in keinem Raum |
| `disable-smart-home-fastpath` | **leere** Datei; ihre Existenz schaltet den alten Bridge-Direktpfad ab | schalten zwei Ausführer — Doppelausführung möglich |

`disable-smart-home-fastpath` ist bewusst eine **leere** Datei. Nicht löschen,
nicht mit Inhalt füllen. Sie ist der Schalter „genau ein Ausführer".

### Umschalter lokal ↔ realtime

| Datei | Rolle |
|---|---|
| `voice-mode` | Skript: kopiert das passende Profil, `daemon-reload`, Neustart |
| `profile-local.service` | Profil mit `--stt-local` und `--tts-local` |
| `profile-realtime.service` | Profil ohne lokale Erkennung/Stimme |

Beide Profile tragen denselben Session-Schlüssel (`…-v6`). `voice-mode` ersetzt
`~/.config/systemd/user/jarvis-realtime-bridge.service` durch das gewählte Profil.

### Python-Abhängigkeiten

```text
websockets==15.0.1
opuslib==3.0.1
```

`requirements.txt` liegt am Installationsort; `.venv/` wird von
`install-host.sh` erzeugt und gehört **nicht** ins Repository.

### Handler-Backup (nur zur Nachvollziehbarkeit)

| Datei | Rolle |
|---|---|
| `handlers-De0Uc7cE.mjs.before-safe-router` | Original der OpenClaw-Datei **vor** dem Weiche-Patch |

Diese Datei ist **kein** Bestandteil der Bridge. Sie dokumentiert, woraus der
gepatchte Handler entstand. Für einen Rollback wird **nicht** die ganze Datei
zurückgeschrieben, sondern nur der `jarvis-safe-router-v1`-Block entfernt —
spätere, unabhängige Änderungen dürfen nicht überschrieben werden.

---

## Dateien, die der Betrieb SELBST erzeugt

Diese Dateien gehören **nicht** ins Repository. Ihr Fehlen beim ersten Start ist
**normal** und kein Fehler.

| Datei | Entsteht durch | Inhalt | Verhalten wenn sie fehlt |
|---|---|---|---|
| `active-room.json` | `publish_active_room()` beim Sprechen | Raum des Geräts, `ts` in Sekunden, TTL 300 s | kein Raum bekannt → Befehl geht an die KI |
| `last-utterance.json` | `openclaw-talk-realtime.mjs` pro finalem Transkript | gesprochener Satz, `ts` in **Millisekunden**, TTL 120 s | Weiche lehnt ab (`no-spoken-utterance`) |
| `last-alexa-command.json` | `server.py` nach dem Senden | Dedupe-Schlüssel, `ts` in Sekunden, Fenster 8 s | kein Dedupe-Schutz |
| `voice-bindings/<uuid>.json` | `bindVoiceSession()` pro Verbindung | Session, Gerät, Raum, 24 h | Raum nicht pro Verbindung auflösbar |
| `alexa-device-catalog.json` | `refresh-alexa-catalog.mjs` (täglich) | 102 erkannt / 23 zugelassen | Direktweg aus, KI bleibt verfügbar |

**Zwei Zeitbasen, nicht verwechseln:** `active-room.json`, `last-alexa-command.json`
und `alexa-device-catalog.json` schreiben **Sekunden** (bzw. Millisekunden bei
`generatedAt`), `last-utterance.json` schreibt **Millisekunden**. Wer eine Datei
mit `< 1e12` sieht, hat eine Sekundenangabe vor sich und muss umrechnen, sonst
gilt jeder Eintrag sofort als abgelaufen.

Alle fünf sind gegen Verlust abgesichert: fehlt eine, fällt der jeweilige
Komfortweg aus, die Sprachsteuerung über die KI bleibt verfügbar.

---

## Voraussetzungen außerhalb des Repositories

| Voraussetzung | Pfad / Wert | Wofür | Fehlt sie, dann … |
|---|---|---|---|
| Gateway-Zertifikat | `~/.openclaw/ssl/gateway.crt` | TLS zum Gateway (`--gateway-ca`) | Helper verbindet nicht |
| Gateway | `openclaw-gateway.service` | Talk-Sessions, Agent, Werkzeuge | keine Antworten |
| Piper-Stimmen | `~/.local/share/piper-voices/` | nur `--tts-local` | lokaler Weg startet nicht |
| Wyoming-Whisper | `127.0.0.1:10303` | nur `--stt-local` | lokale Erkennung leer |
| ioBroker | `192.168.178.24:8087` | Alexa-Befehle, Gerätekatalog | Schaltbefehle und Katalog aus |
| Echo-Endpunkt | `alexa2.0.Echo-Devices.G6G2MM12449402WK.Commands.textCommand` | Ausführung | Schalten unmöglich |
| Node.js | `26.7.0` | Helper | Bridge startet nicht |
| Python | `3.14.7` | Bridge | Bridge startet nicht |

Der Echo-Endpunkt ist **fest verdrahtet**. Er bestimmt den Raum: `textCommand`
wird ausgeführt, als hätte *dieser* Echo gesprochen. Deshalb wird der Raum des
sprechenden Geräts vorangestellt — nicht der des Endpunkts.

---

## Prüfliste nach einer Installation

```bash
# 1. Alle Pflichtdateien vorhanden (install-host.sh bricht sonst ab)
ls -1 ~/.local/share/jarvis-realtime-bridge/{server.py,room_command.py,piper_speaker.py}
ls -1 ~/.local/share/jarvis-realtime-bridge/{openclaw-talk-realtime.mjs,local-voice.mjs,local_stt.mjs}
ls -1 ~/.local/share/jarvis-realtime-bridge/{voice-turn-context.mjs,room-command.mjs,room-router.mjs}
ls -1 ~/.local/share/jarvis-realtime-bridge/{smart-home-router.mjs,scoped-smart-home-router.mjs}
ls -1 ~/.local/share/jarvis-realtime-bridge/{refresh-alexa-catalog.mjs,requirements.txt}
ls -1 ~/.local/share/jarvis-realtime-bridge/{room-map.json,disable-smart-home-fastpath,voice-mode}

# 2. Unit entspricht dem Live-Stand
grep ExecStart ~/.config/systemd/user/jarvis-realtime-bridge.service

# 3. Pfade im Gateway-Patch zeigen auf diesen Ort
grep -o 'file:///home/openclaw/.local/share/jarvis-realtime-bridge/[a-z-]*\.mjs' \
  ~/.npm-global/lib/node_modules/openclaw/dist/handlers-*.mjs

# 4. Bridge laeuft und hoert
systemctl --user is-active jarvis-realtime-bridge.service
ss -ltn | grep -E ':8765|:8766'

# 5. Importkette intakt (Syntaxpruefung)
~/.local/share/jarvis-realtime-bridge/.venv/bin/python -m py_compile \
  ~/.local/share/jarvis-realtime-bridge/server.py \
  ~/.local/share/jarvis-realtime-bridge/room_command.py
node --check ~/.local/share/jarvis-realtime-bridge/openclaw-talk-realtime.mjs
node --check ~/.local/share/jarvis-realtime-bridge/smart-home-router.mjs
node --check ~/.local/share/jarvis-realtime-bridge/scoped-smart-home-router.mjs
```

Die Selbstprüfung in `install-host.sh` deckt Punkt 1 automatisch ab. Punkt 3 ist
der, der bei einem Umzug am häufigsten vergessen wird und still fehlschlägt.

---

## Was hier bewusst NICHT liegt

| Nicht im Repo | Grund |
|---|---|
| `*.bak-*`, `*.broken-*` | Zwischenstände, keine Wahrheit |
| `unit.before-local-20261014` | v5-Altstand, ersetzt durch `profile-local.service` |
| `unit.cloudswitch-backup-20260928-153356` | v5-Altstand mit `--stt-local --tts-local`, ersetzt durch `profile-local.service` |
| `unit.local-20260928-153356` | dito, gleicher Inhalt wie das Cloudswitch-Backup |
| `.venv/`, `__pycache__/` | aus `requirements.txt` reproduzierbar |
| `active-room.json`, `last-*.json`, `voice-bindings/` | Laufzeitdaten mit Zeitstempeln |
| `alexa-device-catalog.json` | aus ioBroker erzeugbar |
| `~/.openclaw/secrets.json` | Zugangsdaten |
| Logs | Laufzeitdaten |
| Firmware-Binaries der Geräte | in `firmware/prebuilt/` separat versioniert |

Die drei `unit.*`-Dateien sind **keine** fehlenden Bestandteile: Sie sind ältere
Fassungen der systemd-Unit, alle mit Session-Key **v5**. Der gültige Stand steckt
in `gateway/profile-local.service` (lokal) und `gateway/profile-realtime.service`
(realtime) — beide auf **v6**. Wer eine `unit.*`-Datei zurückkopiert, setzt den
funktionierenden Stand auf v5 zurück und bringt den Schnellweg durcheinander.

### Wenn die Laufzeitdateien trotzdem gebraucht werden

Sie lassen sich alle neu erzeugen, statt sie zu kopieren:

```bash
cd ~/.local/share/jarvis-realtime-bridge

# Geraetekatalog aus ioBroker (braucht erreichbares Alexa2)
node refresh-alexa-catalog.mjs

# Raum-Map ist Konfiguration und liegt im Repo (gateway/room-map.json)
# active-room.json, last-utterance.json, last-alexa-command.json und
# voice-bindings/ entstehen beim ersten Sprechen von selbst — nichts zu tun.
```

