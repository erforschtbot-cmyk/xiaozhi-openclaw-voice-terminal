# 6. Nachgewiesener Neuaufbau

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

Diese neu gebauten Images sind ein **Buildnachweis**, aber nicht automatisch der
Recovery-Anker. Das Gerät läuft mit den unter `firmware/prebuilt/` abgelegten,
praktisch bestätigten Images. Ein neu gebautes Image wird erst nach dem vollständigen
Hardware-Testplan zum neuen Recovery-Anker.

