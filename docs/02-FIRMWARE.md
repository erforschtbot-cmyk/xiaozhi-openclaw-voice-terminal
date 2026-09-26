# 2. Firmware bauen und flashen

## Hardware

- Waveshare ESP32-S3-Touch-LCD-4B
- Ziel: `esp32-s3-touch-lcd-4b`
- Sprache: `de-DE`
- Wakeword-Modell: `wn9_jarvis_tts`

Partitionen des bestätigten Geräts:

| Partition | Offset | Größe |
|---|---:|---:|
| NVS | `0x9000` | 16 KiB |
| OTA data | `0xd000` | 8 KiB |
| PHY init | `0xf000` | 4 KiB |
| App OTA 0 | `0x20000` | 4032 KiB |
| App OTA 1 | `0x410000` | 4032 KiB |
| Assets | `0x800000` | 8 MiB |

## Empfohlener Wiederherstellungsweg

Der sichere Standard schreibt nur die App-Partition. WLAN/NVS und Assets bleiben
erhalten:

```bash
./scripts/flash-firmware.sh --port /dev/ttyACM0
```

Das Skript prüft vorher die Prüfsumme aus `CHECKSUMS.sha256`, schreibt
`firmware/prebuilt/xiaozhi.bin` bei `0x20000` und prüft mit `verify-flash`.
Wenn `/dev/ttyACM0` verschwindet, USB einmal abziehen/einstecken und erneut prüfen.

## Vollständiges Rettungsimage

Nur bei leerem oder vollständig beschädigtem Flash:

```bash
./scripts/flash-firmware.sh --port /dev/ttyACM0 --full-image-i-understand
```

Dieses Image wurde mit **geleertem NVS** (`0x9000`–`0xF000` auf `0xFF`) abgelegt,
enthält also keine WLAN-Zugangsdaten des Referenzgeräts. Nach dem Flashen ist eine
erneute WLAN-Provisionierung erforderlich.

## Aus Quellen bauen

```bash
./scripts/build-firmware.sh --public-host 192.168.178.143
```

Der Build klont exakt die Pins aus `VERSIONS.md`, wendet beide Patchdateien an,
verwendet ESP-IDF 6.1 im Docker-Container und legt die Artefakte unter `build/` ab.

Die Firmware-Patches enthalten:

- 24/7: kein Display-/CPU-Schlaf, kein PMIC-Poweroff;
- WLAN: gespeicherte Netze endlos erneut versuchen, statt automatisch in
  Provisionierung zu wechseln;
- eindeutiges physisches Wiedergabeende (`playback_drained`);
- Gerätezustände über das XiaoZhi-Protokoll;
- `stream_end`, damit „Sprechen" erst nach geleertem Lautsprecher endet;
- IDF-6.1-Kompatibilität für `uart-uhci`;
- lokales OTA-/WebSocket-Ziel.

## Bekannte Timer der Firmware (Ist-Stand)

Diese Werte sind aus dem gepinnten Quellbaum gelesen und erklären Hängeverhalten:

| Timer/Wert | Ort | Bedeutung |
|---|---|---|
| `kTimeoutSeconds = 120` | `main/protocols/protocol.cc` | Kanal gilt als tot, wenn 120 s nichts eingeht. Wird **nicht** periodisch geprüft. |
| Server-Hello 10 s | `main/protocols/websocket_protocol.cc` | Kein Server-Hello binnen 10 s → `SERVER_TIMEOUT` |
| Clock-Tick 1 s | `main/application.cc` | Aktualisiert nur Statusleiste und Heap-Log |

**Wichtig:** Es gibt **keinen Watchdog und keinen Keepalive** im WebSocket-Pfad, und
keinen Selbstheilungs-Timer, der aus „Sprechen"/„Zuhören" nach „Bereitschaft"
zurückschaltet. Die Rückkehr nach Idle passiert ausschließlich reaktiv — durch
Socket-Abbruch, Fehlerereignis oder Playback-Ende. Deshalb hilft bei einem Hänger
der Neustart der Bridge (erzwingt den Abbruch), nicht ein Warten.

## Warum das Prebuilt-Image erhalten bleibt

Der bestätigte funktionierende Komplettstand wurde aus einer funktionierenden
Basis aufgebaut. Frühere vollständige Neubauten konnten Mikrofon/Audio verlieren.
Darum ist das verifizierte Image der Recovery-Anker; neue Builds müssen erst den
vollständigen Testplan bestehen.
