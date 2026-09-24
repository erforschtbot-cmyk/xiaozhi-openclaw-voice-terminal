# 4. Vollständiger Testplan

Ein Neuaufbau gilt erst als fertig, wenn alle Punkte bestanden sind.

## A. Infrastruktur

```bash
./scripts/verify-host.sh
systemctl --user is-active openclaw-gateway.service
systemctl --user is-active xiaozhi-openclaw-gateway.service
```

Im Journal müssen nach Geräteverbindung `XiaoZhi connected`, `Device MCP initialized`
und ein `ready`-Ereignis erscheinen.

## B. Schnelle direkte Antwort

Sprich: **„Jarvis, erzähle einen Witz.“**

Erwartet: unmittelbare gesprochene Antwort, danach Zuhören/Bereitschaft; kein
OpenClaw-Werkzeug erforderlich.

## C. Geräte-MCP

Sprich: **„Jarvis, Lautstärke auf 50 Prozent.“**

Erwartet: sofortige Änderung, Anzeige `Lautstärke: 50 %`, keine Voice-Bestätigung.

Sprich: **„Jarvis, Helligkeit auf 40 Prozent.“**

Erwartet: sofortige Änderung und Anzeige.

## D. OpenClaw-Lesewerkzeug

Sprich eine Anfrage, die eine Websuche verlangt.

Erwartet: Tool-Aufruf im OpenClaw-Gateway-Journal und anschließend gesprochene
inhaltliche Antwort.

## E. Veränderndes Werkzeug mit deutscher Bestätigung

1. Zielzustand vorher prüfen.
2. Sprich: **„Jarvis, schalte den WoW-Server an.“**
3. Warte auf die Bestätigungsfrage.
4. Sprich: **„Ja, mache das.“**

Bestanden nur, wenn alle vier Beweise vorliegen:

- zweites Nutzertranskript enthält `Ja, mache das`;
- Werkzeug wird wirklich ausgeführt;
- Jarvis spricht das endgültige Ergebnis;
- realer Zielzustand ist korrekt (Authserver und Worldserver `active/running`).

Am 24.09.2026 wurde genau dieser Ablauf vollständig bestätigt.

## F. Ablehnung

Eine testweise ausstehende Aktion mit **„Nein“** beantworten. Die Aktion darf nicht
ausgeführt werden und muss danach verworfen sein.

## G. 24/7 und Reconnect

- länger als fünf Minuten warten: kein PMIC-Off/Standby;
- WLAN kurz unterbrechen: Gerät muss gespeicherte Netze selbstständig erneut
  verbinden;
- Wakeword danach erneut testen.

