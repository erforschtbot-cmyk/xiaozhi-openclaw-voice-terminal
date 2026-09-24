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
| OTA data | `0xd000` | — |
| PHY init | `0xf000` | — |
| App OTA 0 | `0x20000` | 4032 KiB |
| App OTA 1 | `0x410000` | — |
| Assets | `0x800000` | 8 MiB |

## Empfohlener Wiederherstellungsweg

Der sichere Standard schreibt nur die App-Partition. WLAN/NVS und Assets bleiben
erhalten:

```bash
./scripts/flash-firmware.sh --port /dev/ttyACM0
```

Das Skript prüft nach dem Schreiben mit `verify-flash`. Wenn `/dev/ttyACM0`
verschwindet, USB einmal abziehen/einstecken und erneut prüfen.

## Vollständiges Rettungsimage

Nur bei leerem oder vollständig beschädigtem Flash:

```bash
./scripts/flash-firmware.sh --port /dev/ttyACM0 --full-image-i-understand
```

Das kann gespeichertes WLAN/NVS ersetzen. Anschließend kann eine erneute
WLAN-Provisionierung erforderlich sein.

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
- `stream_end`, damit „Sprechen“ erst nach geleertem Lautsprecher endet;
- IDF-6.1-Kompatibilität für `uart-uhci`;
- lokales OTA-/WebSocket-Ziel.

## Warum das Prebuilt-Image erhalten bleibt

Der bestätigte funktionierende Komplettstand wurde aus einer funktionierenden
Basis aufgebaut. Frühere vollständige Neubauten konnten Mikrofon/Audio verlieren.
Darum ist das verifizierte Image der Recovery-Anker; neue Builds müssen erst den
vollständigen Testplan bestehen.

