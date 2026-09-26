# Drittquellen und Lizenzen

Dieses Repository enthält Patchdateien und Anleitungen gegen folgende Projekte:

- `78/xiaozhi-esp32`, MIT-Lizenz — Upstream wird nicht dupliziert; das Buildskript
  klont den in `VERSIONS.md` gepinnten Commit und wendet den Patch an.
- `78/uart-uhci`, Lizenz des jeweiligen Upstream-Repositories — ebenso gepinnt und
  gepatcht.
- OpenClaw — die `dist`-Patches verändern eine lokal installierte
  OpenClaw-Distribution. OpenClaw selbst wird hier nicht mitgeliefert; das
  Anwenden geschieht über `scripts/apply-openclaw-voice-dist-patches.py`.
- OpenAI GPT-Live (`gpt-live-1-codex`) — wird zur Laufzeit über OpenClaw genutzt,
  kein Code oder Schlüssel in diesem Repository.

## Enthaltene Binärdateien

`firmware/prebuilt/` enthält zwei vorbestätigte Images des Referenzgeräts. Sie sind
Recovery-Anker, keine Upstream-Quellen:

- `xiaozhi.bin` — enthält ausschließlich den App-/OTA-0-Bereich des selbst gebauten
  Firmware-Stands (XiaoZhi + OpenClaw-Anpassungen, siehe `firmware/patches/`).
- `merged-binary.bin` — vollständiges Flash-Abbild; der NVS-Bereich wurde geleert.

Die vollständigen Upstream-Quellen werden nicht dupliziert.
