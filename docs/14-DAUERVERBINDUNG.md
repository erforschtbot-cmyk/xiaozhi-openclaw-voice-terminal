# 14. Dauerhafte Geräteverbindung im Standby

Stand: 22.10.2026. **Am Gerät geflasht und im Standby belegt; ein vollständiger
Sprach-Turn mit dieser Firmware ist noch nicht bestätigt.**

## Das Problem

Der XiaoZhi-Upstream ist ein Cloud-Dienst. Dort **ist** die WebSocket-Verbindung
die Gesprächssitzung: Verbindung auf = Abrechnung beginnt, Verbindung zu =
Gespräch beendet.

Der Original-Code schließt sie deshalb am Gesprächsende — an sieben Stellen in
`main/application.cc`, alle aus dem Upstream (Commit `4632dc5`), keine davon von
uns hinzugefügt:

```bash
git show 4632dc51f0a5ad26e08542e131e6e48da41e4ff3:main/application.cc \
  | grep -n CloseAudioChannel
```

Für ein Always-On-Gerät ist das die falsche Grundannahme: Jeder Wake baut
Verbindung und Cloud-Sitzung neu auf. Das kostet Sekunden und erzeugt
Fehlerstellen.

## Drei Verbindungen, nicht eine

| Verbindung | Kosten | Lebensdauer |
|---|---|---|
| WLAN: Gerät ↔ Router | keine | dauerhaft |
| WebSocket: Gerät ↔ Bridge | keine (lokales Netz) | **soll dauerhaft sein** |
| OpenAI-Sitzung: Bridge ↔ OpenAI | **kostet, solange offen** | nur während des Gesprächs |

Dauerhaft verbunden heißt also **nicht** dauerhaft kostenpflichtig. Genau diese
Trennung stellt der Patch her.

## Was der Patch ändert

`firmware/patches/jarvis-audio-board-persistent-standby.patch` — setzt den
Ring-Patch voraus, muss danach angewendet werden.

Vier Dateien:

| Datei | Änderung |
|---|---|
| `main/application.cc` | `standby`-Nachricht annehmen; Wiederverbindung im Hintergrund; Sprachbeginn melden |
| `main/application.h` | Zustand für die Hintergrund-Wiederverbindung |
| `main/protocols/protocol.{cc,h}` | `SendSpeechActivity`, `KeepConnectionInStandby` |
| `main/protocols/websocket_protocol.{cc,h}` | `persistent_standby: true` im `hello` |

### 1. Standby trennt Sprachsitzung von Transport

Neuer Nachrichtentyp vom Server:

```json
{"type": "standby", "reason": "follow-up timeout"}
```

Das Gerät geht auf Bereitschaft, **behält aber die Verbindung**. Nur der
Cloud-Helfer in der Bridge wird beendet.

### 2. Wiederverbindung ohne Alarm und ohne Blockade

Bricht die Verbindung, versucht das Gerät sie im Hintergrund wiederherzustellen:

- Abstände 2, 4, 8, 16, 30 Sekunden, danach dauerhaft alle 30
- eigener Task, damit `Connect()` (bis ~10 s) den Hauptablauf nicht blockiert
- **kein hörbarer Alarm** bei Fehlschlag im Standby — sonst piept das Gerät
  endlos, wenn die Bridge aus ist

Echte Fehler beim Waken melden weiterhin wie bisher.

### 3. Sprachbeginn wird gemeldet

```json
{"type": "device", "event": "speech_activity", "active": true}
```

Damit kann die Bridge das 5-Sekunden-Nachhörfenster anhalten, wenn in dieser
Zeit weitergesprochen wird.

## Rückwärtskompatibel

Das Gerät meldet die Fähigkeit selbst:

```json
{"type": "hello", "features": {"mcp": true, "persistent_standby": true}}
```

Die Bridge schaltet nur dann auf den neuen Modus. Ein Gerät ohne diese Meldung
verhält sich unverändert.

## Bridge-Seite

`gateway/server.py`:

- `persistent_standby` wird aus dem `hello` gelesen
- beim `hello` **kein** Vorwärmen der Cloud-Sitzung mehr (keine Kosten im Standby)
- Nachhörfenster 5 s statt 10 s, wird bei `speech_activity` abgebrochen
- `return_to_standby()` beendet den Helfer und sendet `standby`, **ohne** die
  Geräteverbindung zu schließen

## Grenzen

- **Nicht am Gerät als vollständiger Sprach-Turn bestätigt.** Belegt ist: Gerät
  bootet, verbindet, hält die Verbindung, und es läuft dabei keine
  OpenAI-Sitzung.
- Die genaue Abrechnung von `gpt-live-1-codex` ist nicht aus offiziellen
  OpenAI-Dokumenten belegt. Sicher ist nur: offene Sitzung kostet, geschlossene
  nicht.
- Der Alarm beim fehlgeschlagenen **OTA-Check** (Bridge aus) ist weiterhin
  aktiv. Das ist derselbe Fehlertyp, aber an anderer Stelle.

## Bauen

```bash
bash scripts/build-firmware-audio-board.sh 192.168.178.143
```

Das Skript wendet beide Patches in der richtigen Reihenfolge an. Zur Kontrolle
der Kette:

```bash
cd /tmp && rm -rf pcheck && mkdir pcheck && cd pcheck && git init -q .
# Ring-Patch, dann Persistent-Patch anwenden; Ergebnis muss dem gebauten
# Quellbaum bytegleich entsprechen.
```
