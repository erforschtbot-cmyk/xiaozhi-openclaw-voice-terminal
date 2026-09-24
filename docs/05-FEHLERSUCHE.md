# 5. Fehlersuche und bekannte Fehlwege

## Logs

```bash
journalctl --user -u xiaozhi-openclaw-gateway.service -f
journalctl --user -u openclaw-gateway.service -f
```

## „Ja“ wird gehört, aber erneut nach Bestätigung gefragt

1. Im XiaoZhi-Log prüfen, ob ein finales Nutzertranskript vorhanden ist.
2. Deutschen OpenClaw-Patch prüfen und erneut anwenden.
3. OpenClaw-Gateway neu starten.
4. Vollständigen Werkzeugtest wiederholen.

Nicht die Firmware ändern: Wenn `Ja, mache das` korrekt transkribiert wurde, liegt
die Freigabe im OpenClaw-Bestätigungsmatcher.

## Anzeige „Zuhören“, aber keine Folgeäußerung wird erkannt

Audio-Turn und Talk-Session dürfen nicht blind gekoppelt werden. Der bestätigte
Gatewaystand hält bei einer Werkzeug-Rückfrage dieselbe Talk-Session offen und
öffnet nach physischem `playback_drained` den Eingang erneut. Keine Timer auf
Verdacht ändern.

## „Sprechen“ bleibt hängen

- `stream_end` muss an das Gerät gesendet werden.
- Das Gerät meldet nach geleertem Puffer `playback_drained`.
- WebSocket-Close braucht `close_timeout=1`; das Board liefert nicht immer einen
  Close-Frame.

## Antwortanfang oder -ende abgeschnitten

Keine pauschalen Startpuffer oder langen Audio-Silence-Timer ergänzen. Frühere
Versuche mit 180 ms Startpuffer beziehungsweise 1,2 s Audio-Pause beschädigten den
funktionierenden Ablauf. Änderungen immer einzeln testen und rückrollbar halten.

## Firmware-Build verliert Mikrofon/Audio

Zuerst das verifizierte App-Image bei `0x20000` wiederherstellen. Nicht ungeprüft
das gesamte Flashlayout ersetzen. Assets bei `0x800000` und NVS erhalten.

## OpenClaw-Update

Nach Updates ist der deutsche `dist`-Patch wahrscheinlich überschrieben. Patch,
Verifikation, Gateway-Neustart und End-to-End-Werkzeugtest sind Pflicht.

