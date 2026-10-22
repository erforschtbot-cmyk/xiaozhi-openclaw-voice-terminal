# Verbindliche Versionen

Diese Werte sind der **Ist-Stand vom 2026-10-20** auf dem Referenzhost.

| Komponente | Version / Pin |
|---|---|
| OpenClaw | `2026.10.5` (`1b58cb9`) |
| Gateway-Patchsatz | `patches/openclaw-2026.10.5/` (versionsgebunden, siehe unten) |
| Node.js | `26.7.0` auf dem Referenzhost |
| Python | `3.14.7` auf dem Referenzhost |
| XiaoZhi Upstream | `78/xiaozhi-esp32@4632dc51f0a5ad26e08542e131e6e48da41e4ff3` |
| uart-uhci Upstream | `78/uart-uhci@6ea5f576af84640209aa6b98e27be92b8ce418c5` |
| ESP-IDF Build-Image | `espressif/idf:v6.1` (Digest `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`) |
| Board | Waveshare ESP32-S3-Touch-LCD-4B |
| Zweites Gerät | Waveshare ESP32-S3-AUDIO-Board (SKU 32184/32185), kein Display, 7 RGB-Ring-LEDs |
| Audio-Board-Boardziel | `waveshare/esp32-s3-audio-board` (im selben Upstream-Pin enthalten) |
| Bridge-Python-Pakete | `websockets==15.0.1`, `opuslib==3.0.1` |
| Realtime-Modell | `gpt-realtime-2.1` (Vorgabe in `gateway/openclaw-talk-realtime.mjs`; per `OPENCLAW_REALTIME_MODEL` überschreibbar) |
| Stimme | `cove` |
| Talk-Session-Key | `agent:voice:xiaozhi-realtime-v6` (konstant, ohne UUID-Anhang) |
| Talk-Consult-Key | `agent:voice:xiaozhi-consult-v6` (konstant, ohne UUID-Anhang) |
| Sprechbeginn-Erkennung | `PROVIDER_SPEECH_PEAK=60`, Rueckhaltefenster 120 ms (belegt 2026-10-19) |
| Schnellweg Schaltbefehle | Gateway-Weiche `jarvis-safe-router-v1` + `jarvis-direct-completion-v2`; erkannt bis Alexa **7-51 ms** (belegt 2026-10-18) |
| Schnellweg-Sessions | `agent:voice:xiaozhi-realtime-v5` **und** `…-v6` (Muster `^agent:voice:xiaozhi-realtime-v\d+$`) |
| Alexa-Geraeteliste | aus `alexa2.0.Smart-Home-Devices.*`, 102 erkannt / 23 zugelassen, taeglich per Timer, fail-closed nach 48 h |

## Laufende Firmware (Geräte-Ist-Stand)

| Merkmal | Wert |
|---|---|
| Project | `xiaozhi` |
| Version | `2.5.0` |
| Compile time | `Sep 28 2026 13:08:52` (de-DE, Wachwort-Audio abgeschaltet) |
| ELF-SHA256 | `c30048b5f32545b3d596fb45089a0ab2e0db6b29d94cefdd724f023e11f937cd` |
| ESP-IDF | `v6.1` |
| Geräte-MAC | `94:a9:90:cc:8d:b4` |

## Zweites Gerät: Audio-Board

Dasselbe Bridge-, Gateway- und Host-Setup wie oben; es unterscheidet sich nur die
Firmware. Vollständige Anleitung: `docs/07-AUDIO-BOARD.md`.

| Merkmal | Wert |
|---|---|
| Gerät | Waveshare ESP32-S3-AUDIO-Board (SKU 32184/32185) |
| Chip | ESP32-S3R8, 16 MB Flash, 8 MB PSRAM |
| Audio | ES8311 (DAC), ES7210 (Dual-Mic) |
| Anzeige | **kein Display** — 7 RGB-Ring-LEDs (WS2812, GPIO 38) |
| Boardziel | `waveshare/esp32-s3-audio-board` |
| Patch | `firmware/patches/jarvis-audio-board-ring.patch`, danach `firmware/patches/jarvis-audio-board-persistent-standby.patch` (Reihenfolge zwingend, siehe [docs/14-DAUERVERBINDUNG.md](docs/14-DAUERVERBINDUNG.md)) |
| Sprache / Wakeword | `de-DE` / `wn9_jarvis_tts` (wie 4B) |
| Geräte-MAC | `90:70:69:eb:1e:b4` |
| Laufende Firmware | `xiaozhi 2.5.0`, gebaut `Oct 22 2026 13:02` (Tasten, Ring-Anzeige, Kennlinie, playback_drained, Weiß-Blitz bei Kameraaufnahme, **dauerhafte Geräteverbindung im Standby**) |
| Geflasht auf | Gerät `90:70:69:eb:1c:0c` (Wohnzimmer), App-Partition `0x20000`, NVS erhalten |
| App-SHA256 (Ist-Stand) | `a220b30a25519aef722921f62b726e208fe751a876a4d5327a44fad25acb8200` (2.834.448 B, Flash 2026-10-22 13:09, Hash verifiziert) |
| Standby-Beleg | 2026-10-22 13:14:57: Gerät verbunden, Verbindung über 60 s **durchgehend offen**, dabei **keine** OpenAI-Sitzung. Vollständiger Sprach-Turn mit diesem Stand noch nicht bestätigt. |
| Veröffentlichter Anker | `firmware/prebuilt/audio-board/xiaozhi.bin` (App-Partition, 2.833.056 B) |
| Anker-SHA256 | `acf864c5001638ee18eb7c7439ab555b7d09f4a16a93c2baa6842246e7a6b4bc` |
| Anker-Status | **Am Gerät bestätigt (2026-10-20, 18:08).** Foto-Lauf protokolliert: Auslösung 18:08:06, Upload fertig 18:08:07, korrekte Bildbeschreibung, gesprochen. Der Blitz war rund eine Sekunde an. Der Anker ist der **Rückfall** für den Persistent-Standby-Stand vom 22.10.; dieser ist selbst noch nicht als Sprach-Turn abgenommen. |
| Vorheriger Anker | `firmware/prebuilt/audio-board/previous-vor-kamera-blitz/xiaozhi.bin` (`eb8671648ec85ebce…`, Stand ohne Blitz) |

Der Anker ist die **App-Partition** (2.833.056 B), nicht das Vollimage. Er
enthält **keine** Zugangsdaten — WLAN-Name und -Passwort liegen ausschließlich in
der NVS, die nicht im Repo ist. Das Image wird bei `0x20000` geschrieben, dann
bleiben NVS und Assets unangetastet.

Dieser Stand liegt als `firmware/prebuilt/xiaozhi.bin` im Repo. Er enthält
zusätzlich den Eingriff, dass das **Wachwort-Audio nicht mehr an den Server**
geschickt wird (`CONFIG_SEND_WAKE_WORD_DATA=n`, siehe `docs/02-FIRMWARE.md`).
Mikrofon, Erkennung und Mithören sind davon nicht betroffen.

Direkter Rückweg — der Stand **vor** diesem Eingriff:
`Sep 27 2026 14:13:36`, ELF `77fd991a4856c6bef3c0dd3aa08d3f3ef650b06c74bd23087bb4aad553c91362`
(`firmware/prebuilt/previous/xiaozhi.bin`).

Direkter Rückweg zum vorherigen Watchdog-Stand mit statischem Smiley:
`Sep 26 2026 19:10:55`, ELF `2d817b23a349060d`
(`firmware/prebuilt/previous-watchdog-smiley/xiaozhi.bin`).

Rückweg ohne Watchdog: `Sep 23 2026 08:43:24`, ELF `b6bf3e74cef7c701`
(`firmware/prebuilt/previous-no-watchdog/xiaozhi.bin`).

**Nicht verwechseln:** Es gibt weitere `xiaozhi 2.5.0`-Builds, u. a. vom
`Sep 22 2026 15:25:48` (ELF `dc80cd8c5e42d81b`). Version und Projektname sind
identisch — nur Compile time und ELF-Hash unterscheiden die Builds.

Neuere Versionen sind nicht automatisch gleichwertig. Erst nach einem vollständigen
End-to-End-Test dürfen Pins aktualisiert werden.
