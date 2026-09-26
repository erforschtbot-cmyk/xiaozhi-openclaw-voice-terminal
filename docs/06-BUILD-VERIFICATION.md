# 6. Nachgewiesener Neuaufbau

## Firmware-Build

Am 24.09.2026 wurde `scripts/build-firmware.sh` auf einem sauberen Checkout
vollständig ausgeführt.

- Upstream XiaoZhi: `4632dc51f0a5ad26e08542e131e6e48da41e4ff3`
- Upstream uart-uhci: `6ea5f576af84640209aa6b98e27be92b8ce418c5`
- ESP-IDF: `v6.1-803-g94639ab7251`
- 74 Komponenten wurden aufgelöst
- 2.237 Kompilierschritte erfolgreich
- Appgröße: `0x2c5aa0`, 30 % der kleinsten App-Partition frei
- zweiter sauberer Kontrollbuild ebenfalls erfolgreich
- erzeugte `dependencies.lock` ist im Repository hinterlegt

Die Binärdateien enthalten Buildmetadaten und sind deshalb nicht zwingend
byteidentisch zwischen zwei erfolgreichen Neubauten. Maßgeblich sind die gepinnten
Quellen, die Lockdatei, ein fehlerfreier Build und anschließend der Hardware-Test.

## Patch-Anwendung (am 26.09.2026 erneut geprüft)

Beide Firmware-Patches wurden gegen den gepinnten Upstream verifiziert:

```text
xiaozhi-esp32-openclaw.patch
  = byte-identisch zum Ist-Differenzbild des gepinnten Arbeitsbaums
  = wendet sauber auf pristine Checkout an (git apply --check: OK)

uart-uhci-idf61.patch
  = wendet sauber auf uart-uhci@6ea5f576 an
```

## Verifikation der laufenden Firmware (26.09.2026)

Der Zustand des Geräts wurde rein lesend festgestellt:

| Quelle | Ergebnis |
|---|---|
| Boot-Log (seriell) | `xiaozhi 2.5.0`, compile `Sep 23 2026 08:43:24`, ELF `b6bf3e74…` |
| App-Deskriptor `read-flash 0x20020` | identisch zum Boot-Log |
| Geräte-MAC | `94:a9:90:cc:8d:b4` |

Damit ist der laufende Stand eindeutig auf die Prebuilt-Images in
`firmware/prebuilt/` abbildbar:

| Datei | Prüfsumme (SHA-256) | Bezug |
|---|---|---|
| `xiaozhi.bin` | `69672c442cdf5166f89e0bfc50e2d26854b0f669afac8c45e573f2b4de1f0fb8` | App-Partition `ota_0`, echte Länge 2.906.784 B |
| `merged-binary.bin` | `11c0a3cb24e4fcf66776ea20bff4d1fef78c832872a555928c613e04ac5abba3` | Volles 16-MiB-Image, NVS geleert |

Extraktion aus dem Voll-Image vom 25.09.2026
(`full-flash-before-official-openclaw.bin`, SHA-256
`034024a8c7d720c0ffcbe8470f3526b646eb8e3c28013752a5380b1ecdaece05`):
Partition `ota_0` bei `0x20000`, Länge `0x3f0000`, Daten bis zum letzten
Nicht-`0xFF`-Byte getrimmt.

## Geheimnisprüfung der veröffentlichten Images

Der komplette Flash-Speicher wurde partitionweise auf Zugangsdaten geprüft:

| Partition | Nicht-`FF`/`00`-Bytes | Zugangsdaten |
|---|---:|---|
| `nvs` | 1569 | **ja** (WLAN-SSID/Passwort im Klartext) |
| `otadata` | 6 | nein |
| `phy_init` | 0 | nein |
| `ota_0` (App) | 2532898 | nein |
| `ota_1` (leer) | 0 | nein |
| `assets` | 3623405 | nein |

Daraus folgt:

- `firmware/prebuilt/xiaozhi.bin` (nur `ota_0`) ist **frei** von Zugangsdaten.
- `firmware/prebuilt/merged-binary.bin` wurde mit **geleertem NVS**
  (`0x9000`–`0xF000` = `0xFF`) erzeugt, damit keine WLAN-Zugangsdaten
  mitveröffentlicht werden.

## Bridge-Skripte

Beide Skripte wurden am 26.09.2026 aus dem laufenden Stand übernommen und
byte-genau verifiziert:

| Datei | SHA-256 |
|---|---|
| `gateway/server.py` | `bf1bb17b03a1f5eeb5ec097240409d1c8b67574f4bede1ac106f914e04febbe3` |
| `gateway/openclaw-talk-realtime.mjs` | `430aa9205b5f275552c14e27aefbaa4f58990df892071bd173c3e9c55e1145c6` |

## OpenClaw-`dist`-Patches

Beide Patches wurden am 26.09.2026 als aktiv verifiziert:

| Marker | Datei |
|---|---|
| `voice-confirmation-disabled-by-owner-v1` | `dist/agent-tools.before-tool-call-*.mjs` |
| `voice-test-suppress-assistant-persist-v1` | `dist/handlers-*.mjs` |

`scripts/apply-openclaw-voice-dist-patches.py` ist idempotent geprüft (zweiter
Lauf meldet `already`, ohne eine Sicherung anzulegen).

## Was ein Neuaufbau noch beweisen muss

Die neu gebauten Images sind ein **Buildnachweis**, aber nicht automatisch der
Recovery-Anker. Das Gerät läuft mit den unter `firmware/prebuilt/` abgelegten,
praktisch bestätigten Images. Ein neu gebautes Image wird erst nach dem vollständigen
Hardware-Testplan (`04-TESTPLAN.md`) zum neuen Recovery-Anker.
