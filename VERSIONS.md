# Verbindliche Versionen

Diese Werte sind der **Ist-Stand vom 2026-09-28** auf dem Referenzhost.

| Komponente | Version / Pin |
|---|---|
| OpenClaw | `2026.9.6` (`eb377ac`) |
| Node.js | `26.7.0` auf dem Referenzhost |
| Python | `3.14.7` auf dem Referenzhost |
| XiaoZhi Upstream | `78/xiaozhi-esp32@4632dc51f0a5ad26e08542e131e6e48da41e4ff3` |
| uart-uhci Upstream | `78/uart-uhci@6ea5f576af84640209aa6b98e27be92b8ce418c5` |
| ESP-IDF Build-Image | `espressif/idf:v6.1` (Digest `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`) |
| Board | Waveshare ESP32-S3-Touch-LCD-4B |
| Bridge-Python-Pakete | `websockets==15.0.1`, `opuslib==3.0.1` |
| Realtime-Modell | `gpt-live-1-codex` |
| Stimme | `cove` |
| Talk-Session-Key | `agent:voice:xiaozhi-realtime-v5` (konstant, ohne UUID-Anhang) |
| Talk-Consult-Key | `agent:allgemein:xiaozhi-realtime-v5` (konstant, ohne UUID-Anhang) |

## Laufende Firmware (Geräte-Ist-Stand)

| Merkmal | Wert |
|---|---|
| Project | `xiaozhi` |
| Version | `2.5.0` |
| Compile time | `Sep 28 2026 13:08:52` (de-DE, Wachwort-Audio abgeschaltet) |
| ELF-SHA256 | `c30048b5f32545b3d596fb45089a0ab2e0db6b29d94cefdd724f023e11f937cd` |
| ESP-IDF | `v6.1` |
| Geräte-MAC | `94:a9:90:cc:8d:b4` |

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
