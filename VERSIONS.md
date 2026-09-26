# Verbindliche Versionen

Diese Werte sind der **Ist-Stand vom 2026-09-26** auf dem Referenzhost.

| Komponente | Version / Pin |
|---|---|
| OpenClaw | `2026.9.6` (`eb377ac`) |
| Node.js | `26.7.0` auf dem Referenzhost |
| Python | `3.14.7` auf dem Referenzhost |
| XiaoZhi Upstream | `78/xiaozhi-esp32@4632dc51f0a5ad26e08542e131e6e48da41e4ff3` |
| uart-uhci Upstream | `78/uart-uhci@6ea5f576af84640209aa6b98e27be92b8ce418c5` |
| ESP-IDF Build-Image | `espressif/idf:release-v6.1` |
| Board | Waveshare ESP32-S3-Touch-LCD-4B |
| Bridge-Python-Pakete | `websockets==15.0.1`, `opuslib==3.0.1` |
| Realtime-Modell | `gpt-live-1-codex` |
| Stimme | `cove` |
| Talk-Session-Key | `agent:voice:xiaozhi-realtime-v5` |
| Talk-Consult-Key | `agent:allgemein:xiaozhi-realtime-v5` |

## Laufende Firmware (Geräte-Ist-Stand)

| Merkmal | Wert |
|---|---|
| Project | `xiaozhi` |
| Version | `2.5.0` |
| Compile time | `Sep 26 2026 19:10:55` (mit Watchdog) |
| ELF-SHA256 (Präfix) | `2d817b23a349060d` |
| ESP-IDF | `v6.1-803-g94639ab7251` |
| Geräte-MAC | `94:a9:90:cc:8d:b4` |

Rückweg ohne Watchdog: `Sep 23 2026 08:43:24`, ELF `b6bf3e74cef7c701`
(`firmware/prebuilt/previous-no-watchdog/xiaozhi.bin`).

**Nicht verwechseln:** Es gibt weitere `xiaozhi 2.5.0`-Builds, u. a. vom
`Sep 22 2026 15:25:48` (ELF `dc80cd8c5e42d81b`). Version und Projektname sind
identisch — nur Compile time und ELF-Hash unterscheiden die Builds.

Neuere Versionen sind nicht automatisch gleichwertig. Erst nach einem vollständigen
End-to-End-Test dürfen Pins aktualisiert werden.
