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
- **Wiederherstellungs-Watchdog**, der hängende Gesprächszustände selbstständig
  nach Bereitschaft zurückführt (siehe `docs/02-FIRMWARE.md`);
- board-spezifisches animiertes OpenClaw-Gesicht mit Blinzeln, Blickbewegung,
  Atmung, Emotionsfarben und animierten Mundbalken beim Sprechen;
- Render-Cache für unveränderte Farben, Rotation und Geometrie, entfernte tote
  Lid-Objekte sowie LVGL auf Kern 1 mit 5-ms-Zeitbasis; Zustände und sichtbare
  50-ms-Gesichtsanimation bleiben unverändert;
- IDF-6.1-Kompatibilität für `uart-uhci`;
- **Wachwort-Audio wird nicht mehr an den Server geschickt**
  (`CONFIG_SEND_WAKE_WORD_DATA=n`, siehe unten);
- lokales OTA-/WebSocket-Ziel.

## Animiertes Gesicht ohne Architekturwechsel

Für das Waveshare-4B wird statt `RgbLcdDisplay` die davon abgeleitete Klasse
`JarvisFaceDisplay` instanziiert. Sie ersetzt ausschließlich die zentrale
Emoji-Darstellung durch LVGL-Objekte. Statusleiste, Untertitel, Touch, Helligkeit
und alle Gerätefunktionen bleiben die vorhandenen XiaoZhi-Komponenten.

Die Anzeige reagiert auf die bereits vorhandenen Aufrufe `SetStatus()` und
`SetEmotion()`:

- Bereitschaft: ruhiges Atmen, zufällige Blickbewegungen und Blinzeln;
- Zuhören: größere, aufmerksame Augen;
- Verbinden/Denken: violette, nachdenkliche Darstellung;
- Sprechen: drei animierte Mundbalken;
- Emotionen wie `happy`, `excited`, `sleepy` und `sad`: weiche Übergänge von
  Farbe, Augenform und Mundkurve.

Es wurden dafür keine Audio-, Wakeword-, Protokoll-, WLAN-, OTA- oder
Bridge-Funktionen verändert. Der Code liegt im Firmware-Patch als
`main/boards/waveshare/esp32-s3-touch-lcd-4b/jarvis_face_display.{h,cc}`.

## Bekannte Timer der Firmware (Ist-Stand)

Diese Werte sind aus dem gepinnten Quellbaum gelesen und erklären Hängeverhalten:

| Timer/Wert | Ort | Bedeutung |
|---|---|---|
| `kTimeoutSeconds = 120` | `main/protocols/protocol.cc` | Kanal gilt als tot, wenn 120 s nichts eingeht |
| Server-Hello 10 s | `main/protocols/websocket_protocol.cc` | Kein Server-Hello binnen 10 s → `SERVER_TIMEOUT` |
| Clock-Tick 1 s | `main/application.cc` | Statusleiste, Heap-Log **und der Wiederherstellungs-Watchdog** |
| Watchdog speaking 60 s | `HandleStuckWatchdog` | Kein Serveraudio seit 60 s im Zustand „Sprechen“ → Bereitschaft |
| Watchdog listening 120 s | `HandleStuckWatchdog` | Keine Serveraktivität seit 120 s im Zustand „Zuhören“ → Bereitschaft |
| Watchdog connecting 15 s | `HandleStuckWatchdog` | Audio-Kanal öffnet nicht binnen 15 s → Bereitschaft |

Der Upstream hat **keinen** Watchdog und keinen Keepalive. Ohne den Patch bleibt ein
hängender Zustand stehen, bis ein Socket-Abbruch von außen kommt. Mit dem Patch
kehrt das Gerät selbstständig nach Bereitschaft zurück.

### Wie der Watchdog arbeitet

`Protocol` merkt sich bei **jedem** eingehenden Paket (JSON *und* Audio) einen
Zeitstempel. Der Watchdog läuft im vorhandenen 1-Sekunden-Takt und wertet diesen
Zeitstempel aus:

- **Zustand „Sprechen“:** Antwortet der Server 60 s nicht, wird das Sprechen
  abgebrochen (`AbortSpeaking`) und der Kanal geschlossen → Bereitschaft.
- **Zustand „Zuhören“:** Seit 120 s keine Serveraktivität → Kanal schließen →
  Bereitschaft. Ein laufender Werkzeug-Consult streamt zwar nichts, hält die
  Verbindung aber offen; 120 s sind bewusst großzügig gewählt.
- **Zustand „Verbinden“:** Öffnet der Audio-Kanal nicht binnen 15 s → Bereitschaft.

Nicht angefasst werden `idle`, `wifi_configuring`, `activating`, `upgrading`,
`notifying` und `fatal_error`. Der Watchdog kann also keine Provisionierung oder
Oberflächen stören.

Jeder Eingriff wird geloggt:

```text
W (...) Application: Stuck watchdog: state=speaking in_state=61s idle=60s (no server audio while speaking) -> idle
```

**Schwellen anpassen:** Die Werte stehen als `constexpr` in
`Application::HandleStuckWatchdog` (`kSpeakingIdleTimeoutS`,
`kListeningIdleTimeoutS`, `kConnectingTimeoutS`). Nach jeder Anpassung den
vollständigen Testplan durchlaufen.

## Warum das Prebuilt-Image erhalten bleibt

Der bestätigte funktionierende Komplettstand wurde aus einer funktionierenden
Basis aufgebaut. Frühere vollständige Neubauten konnten Mikrofon/Audio verlieren.
Darum ist das verifizierte Image der Recovery-Anker; neue Builds müssen erst den
vollständigen Testplan bestehen.

Deshalb gilt bei **jeder** Firmware-Änderung: den bisherigen Stand nach
`firmware/prebuilt/previous/` verschieben, bevor er ersetzt wird, und den neuen
ELF-Hash in `VERSIONS.md` vermerken.

## Wachwort-Audio nicht mehr mitsenden

Einziger zusätzlicher Eingriff gegenüber dem Watchdog-Stand.

Das Gerät öffnet den Audiokanal erst nach dem Wachwort. Je nach Zeitpunkt liegen
die ersten Rahmen noch davor — das Wachwort steckt dann mit im Transkript
(„Jarvis.“, „Job es.“). Der Host filtert das zwar nachträglich, aber besser ist,
die Rahmen gar nicht erst zu verschicken.

Die Ursprungsfirmware sendet das Wachwort-Audio (`main/application.cc`):

```c
#if CONFIG_SEND_WAKE_WORD_DATA
    while (auto packet = audio_service_.PopWakeWordPacket()) {
        protocol_->SendAudio(std::move(packet));   // <- die stoerenden Rahmen
    }
    protocol_->SendWakeWordDetected(wake_word);
    SetListeningMode(GetDefaultListeningMode());
#else
    play_popup_on_listening_ = true;
    SetListeningMode(GetDefaultListeningMode());
#endif
```

Upstream-Standard ist `y`; deshalb sendete das Referenzgerät die Rahmen.

| Betroffen? | |
|---|---|
| Mikrofon | **nein** |
| I2S / Audio-Codec | **nein** |
| Wachwort-Erkennung (ESP-SR) | **nein** — läuft vor dem `#if`, in beiden Zweigen |
| Mithören (`SetListeningMode`) | **nein** — steht in beiden Zweigen |
| Gesendete Rahmen | **nur das** |

Der `#else`-Zweig ist ein vorgesehener Weg, kein Notbehelf. Der Host hängt nicht
an `SendWakeWordDetected`; die Bridge startet ihren Helfer über den
`listen`-Status.

Gesetzt wird der Schalter in der Board-Konfiguration im Patch
(`firmware/patches/xiaozhi-esp32-openclaw.patch`), über `sdkconfig_append`:

```json
"sdkconfig_append": [
    "CONFIG_USE_WECHAT_MESSAGE_STYLE=n",
    "CONFIG_USE_DEVICE_AEC=y",
    "CONFIG_OTA_URL=\"http://192.168.178.143:8766/xiaozhi/ota/\"",
    "CONFIG_SEND_WAKE_WORD_DATA=n"
]
```

### Prüfen

```bash
sudo python3 scripts/read-device-info.py --port /dev/ttyACM0
# erwartet: compile 13:08:52 Sep 28 2026
#           elf-sha256 c30048b5f32545b3d596fb45089a0ab2e0db6b29d94cefdd724f023e11f937cd
```

### Rückweg

```bash
esptool --chip esp32s3 --port /dev/ttyACM0 write-flash 0x20000 \
  firmware/prebuilt/previous/xiaozhi.bin
```

### Hinweis zu Build-Warnungen

Der Build meldet für einige Upstream-Kconfig-Optionen „`default False` is not a
valid bool value … Value is treated as 'n'". Das ist ein Schönheitsfehler der
Upstream-Dateien und hat keine Auswirkung — der Build läuft mit `exit_code 0`
durch.
