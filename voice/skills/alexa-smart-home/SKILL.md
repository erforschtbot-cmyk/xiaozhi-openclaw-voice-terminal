---
name: "alexa-smart-home"
description: "Haus-, Licht-, Schalter-, Jalousie- und Gerätesteuerung per Sprache an Alexa weitergeben (ioBroker simple-api). Trigger: Licht an/aus, Jalousie, Steckdose, schalte X ein, mach X an, dimme, Gerät steuern."
metadata:
  author: openclaw
  version: "1.0"
---

# Smart Home über Alexa

Haussteuerung läuft **nicht** über eigene ioBroker-Logik, sondern als wörtlicher
Sprachbefehl an Alexa. Das ist 1:1 wie „Alexa, &lt;Befehl&gt;" sagen — Alexa führt
exakt denselben Befehl aus.

## Ausführen

Ein einziger Aufruf über die vertrauenswürdige Voice-Aktion. Den gesprochenen
Befehl wörtlich übernehmen und nur URL-kodieren:

```bash
/home/openclaw/.local/bin/openclaw-voice-skill-action \
  alexa-smart-home schalte%20das%20licht%20im%20arbeitszimmer%20an
```

Nur dieser Wrapper ist für die bestätigungsfreie Voice-Ausführung zugelassen.
Nie direkt `curl` verwenden und keine Shell-Operatoren anhängen.

- Ziel: `alexa2.0.Echo-Devices.G6G2MM12449402WK.Commands.textCommand` (Echo Arbeitszimmer)
- Instanz: ioBroker simple-api auf `192.168.178.24:8087`
- `value` = gesprochener Befehl **ohne** „Alexa" davor
- Leerzeichen als `%20`; Umlaute kodieren (ä=`%C3%A4`, ö=`%C3%B6`, ü=`%C3%BC`, ß=`%C3%9F`)
- Wrapper-Ausgabe `OK alexa-smart-home http=200` = angenommen. Der Datenpunkt
  ist `write:true`, `read:false` — kein `/get`.

## Beispiele

| Äußerung | value |
|---|---|
| schalte das licht im arbeitszimmer an | `schalte%20das%20licht%20im%20arbeitszimmer%20an` |
| mach das licht im wohnzimmer aus | `mach%20das%20licht%20im%20wohnzimmer%20aus` |
| jalousie im wohnzimmer runter | `jalousie%20im%20wohnzimmer%20runter` |
| steckdose sofa aus | `steckdose%20sofa%20aus` |

## Verhalten

1. Befehl wörtlich übernehmen, nur URL-kodieren. Nicht umformulieren, nicht
   Gerätenamen raten, nicht in Teile zerlegen.
2. Ein Aufruf. Danach **eine** Kontrolle (HTTP 200) und eine kurze deutsche
   Bestätigung. Keine zweite Prüfung, keine Technik-Rückfrage.
3. Ist der Befehl unklar, genau eine kurze Rückfrage stellen und den Turn beenden.

## Festes Ziel

Immer denselben Datenpunkt des Echo Arbeitszimmer verwenden, auch wenn der
gesprochene Befehl einen anderen Raum oder ein anderes Gerät nennt. Der gesamte
Befehl wird wörtlich an Alexa übergeben; Alexa bestimmt daraus das Zielgerät.
Keine Echo-Serial suchen oder wechseln.

## Fehlerbilder

- `422` ohne `value` → nur der Wert fehlt; Link ist korrekt aufgebaut.
- Alexa antwortet „das habe ich nicht verstanden" → der Befehl ist in der
  Alexa-App nicht als Aktion/Gerät vorhanden. Nicht lokal weiterarbeiten; das ist
  eine Alexa-Konfigurationssache.
- Kein Ton vom Echo → falsche Serial oder Gerät offline.
