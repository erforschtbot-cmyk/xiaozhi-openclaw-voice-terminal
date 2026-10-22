# 15. Dünner Audio-Client (thin-webrtc)

Stand: 22.10.2026. **Auf dem Gerät im Betrieb; ein vollständiger, belastbarer
Dauerbetrieb ist noch nicht abgenommen.**

## Warum es diesen Weg gibt

Der bisherige Helfer (`openclaw-talk-realtime.mjs`) lief über
`talk.session.create` mit `transport: "gateway-relay"`. Dabei gehört die
Medienverbindung dem Gateway, das sie intern an OpenAI weiterreicht. In dieser
Zwischenschicht saßen alle belegten Ausfälle:

- `Unknown Talk session`
- „Realtime provider output has no live response owner"
- Sitzungsverlust nach langen Pausen
- Verbindungsabbruch im 123-Sekunden-Takt

OpenClaw dokumentiert für genau diesen Fall einen anderen Weg
(`docs/nodes/talk/realtime-sessions.md`, Abschnitt „Thin audio clients"):

```json
capabilities: ["gateway-control-v1"]
```

Antwort des Gateways:

```json
{"transport":"webrtc","offerUrl":"/plugins/openai/realtime/calls",
 "clientControl":{"owner":"gateway"},"clientSecret":"…","voiceSessionId":"…"}
```

Der Client schickt **nur ein Audio-SDP-Angebot**. Die Medien laufen direkt
zwischen Client und OpenAI. Der Gateway behält Werkzeuge, Transkripte,
Steuerung und Aufräumen.

## Der neue Helfer

`gateway/openclaw-thin-client.mjs`, gestartet von `server.py` über `--helper`.

Ablauf:

1. Gateway-Verbindung (`GatewayClient`).
2. `talk.client.create` mit `capabilities: ["gateway-control-v1"]`.
3. `OpenAIQuicksilverAudioPeer` erzeugen (aus OpenClaws eigenem `dist`).
4. SDP-Angebot als `application/sdp` an `offerUrl` senden, Antwort anwenden.
5. PCM 24 kHz mono von stdin in den Peer, Peer-Audio nach stdout.
6. `talk.client.close` beim Beenden.

Es werden **keine neuen Abhängigkeiten** installiert: OpenClaw bringt `werift`
(WebRTC) und `libopus` selbst mit — dieselben Bibliotheken, die der
Browser-Weg intern nutzt.

## Belegter Ablauf (22.10.2026)

```
1076 ms  gateway_ready
1129 ms  call_created   (transport=webrtc, owner=gateway)
2487 ms  session.ready
2496 ms  peer_ready     → Ring grün
5051 ms  turn.started
12498 ms transcript.done
21990 ms output.text.done
```

Ein Turn zurück: 238.066 Bytes Audio (5,0 s, Peak 8749).

Ein echter Schaltbefehl lief durch: Transkript 21:16:15, im gleichen Moment
stand `Schalte den Monitor an` am Alexa-Datenpunkt.

## Grenzen, die offen sind

- **Sätze brechen mitten ab.** In der Instanz stehen abgeschnittene Einträge
  („Kannst du die ganzen Sätze sehen, die bei dir in der"), ebenso bei
  Antworten („Mhm. Bisher kamen an"). Ursache nicht behoben.
- **Kein Live-Ticker in der Instanz.** Ein Transkript-Eintrag wird über
  `voice:<voiceSessionId>:<entryId>` eindeutig identifiziert. Mehrfaches
  Schreiben mit derselben ID behält den ersten Stand; Schreiben pro Wort
  erzeugt hunderte Einträge. Das Wort-für-Wort-Ticken in der GUI ist die
  Live-Anzeige der Browser-Sitzung und wird nie gespeichert.
- **Zwei getrennte Sitzungen.** Browser-Mikrofon und Gerät schreiben in
  verschiedene Sitzungen. Wer in einer schaut, sieht nur die Hälfte.
- **Keine Sprachvorgabe.** `talk.client.create` ist ein `closedObject` und
  lehnt `language` ab (`unexpected property 'language'`). `talk.speechLocale`
  gilt nur für Geräte-Nodes und die iOS-Systemstimme, nicht für diesen Pfad.
  Die Transkription rät die Sprache pro Äußerung.

## Rückfall

Der bisherige Helfer bleibt liegen
(`openclaw-talk-realtime.mjs.before-20261022-offline-fix`). Der Dienst lässt
sich durch Entfernen von `--helper …` in der Unit wieder auf den alten Weg
stellen.

## Prüfen

```bash
node --check ~/.local/share/jarvis-realtime-bridge/openclaw-thin-client.mjs
node --test ~/.local/share/jarvis-realtime-bridge/test_realtime_offline.mjs

# Belege eines Turns
ls -t ~/.local/share/jarvis-realtime-bridge/logs/thin-*.jsonl | head -1
```
