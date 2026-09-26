# 3. OpenClaw: Voice-Patches in `dist`

OpenClaw verändert für den Voice-Pfad zwei Verhaltensweisen. Beide liegen in
**kompilierten `dist`-Dateien** und werden von **jedem OpenClaw-Update
überschrieben**. Nach jedem Update erneut anwenden und verifizieren.

## Patch A — zusätzliche Talk-Sprachbestätigung deaktiviert

Datei: `dist/agent-tools.before-tool-call-*.mjs`
Funktion: `resolveClientVoiceToolConfirmationPolicy`
Marker: `voice-confirmation-disabled-by-owner-v1`

OpenClaw würde verändernde Voice-Werkzeugaktionen zusätzlich per gesprochenem
Ja/Nein absichern. Der Owner hat das ausdrücklich abgeschaltet. Der Patch setzt die
Funktion früh auf `{ allowed: true }` — **ohne** Text-, Befehls-, Satzzeichen- oder
Wortfilter.

## Patch B — User- und Assistant-Text getrennt, je einmal pro Turn

Datei: `dist/handlers-*.mjs`
Ort: `onTranscript`, `handleDelegationInput`, `onToolCall`, Forced-Consult
Marker: `voice-persist-split-v3`

Beide Seiten werden gespeichert, aber **getrennt** und **genau einmal pro Turn**:

| Fall | User-Text | Assistant-Antwort |
|---|---|---|
| **ohne Tool** | Relay (1×) | Relay (1×) |
| **mit Tool** | einmal | nur der Consult |

Verworfen wird ausschließlich die **Zwischenansage** („I'll check that request"),
weil sie der zweite Schreiber auf demselben Transkript war.

### Warum das nötig ist

Zwei getrennte Fehlerbilder, beide aus derselben Ursache:

1. **SQLite-Konflikt.** Zwischenansage (Voice-Pfad) und Consult schreiben in
dasselbe Transkript. Auf einem frischen Turn kollidieren beide Schreiber:

```text
SqliteTranscriptMutationConflictError:
SQLite transcript changed while preparing rewrite for <sessionId>
```

Sichtbare Folge: „Es hat leider nicht geklappt … soll ich es nochmal?" — obwohl die
Werkzeugantwort inhaltlich bereits erzeugt wurde. Im Transkript war die Sprache des
Nutzers in Tool-Turns **zweimal** als `role=user` abgelegt: einmal vom Voice-Relay,
einmal im Consult-Prompt.

2. **Doppelte Antwort.** Mit Werkzeug schreibt der Consult die Antwort **und** der
Voice-Relay dieselbe Antwort nochmal (`prov=None` und `prov=realtime_voice`,
identischer Text). Der Merker `assistantOwnedByConsult` verhindert das.

### Umsetzung

Fünf Teile in derselben Datei:

| Teil | Ort | Wirkung |
|---|---|---|
| Relay-Feld | Relay-Objekt | `assistantOwnedByConsult: false` |
| provider-direct-Haken | `handleDelegationInput` | Merker setzen, wenn echtes Consult (`outcome !== "control"`) |
| Tool-Call-Haken | `onToolCall` | Merker bei `openclaw_agent_consult` |
| Forced-Consult-Haken | `scheduleForcedAgentConsult` | Merker im erzwungenen Pfad |
| Transkript-Gate | `onTranscript` | Zwischenansage verwerfen; Assistant überspringen, wenn Merker gesetzt oder ein Agent-Run aktiv ist; Merker bei neuer User-Frage zurücksetzen |

**Wichtig:** `consultRouting` steht auf `provider-direct`. Der Consult kommt dort
**nicht** als `openclaw_agent_consult`-Tool-Call an — deshalb wirkt der
`handleDelegationInput`-Haken, nicht nur der Tool-Call-Haken.

## Anwenden und verifizieren

```bash
./scripts/apply-openclaw-voice-dist-patches.py
./scripts/verify-openclaw-voice-dist-patches.py
systemctl --user restart openclaw-gateway.service
```

Das Anwenden ist **idempotent**: Ist ein Patch schon aktiv, meldet das Skript
`already` und schreibt nichts. Vor jeder Änderung wird eine Sicherung
`<datei>.bak-<marker>-<zeitstempel>` angelegt.

Erwartete Ausgabe bei aktivem Stand:

```text
confirm:agent-tools.before-tool-call-<hash>.mjs: already
transcript:handlers-<hash>.mjs: already
Neustart noetig: systemctl --user restart openclaw-gateway.service
```

## Nach jedem OpenClaw-Update

```bash
./scripts/apply-openclaw-voice-dist-patches.py
./scripts/verify-openclaw-voice-dist-patches.py
systemctl --user restart openclaw-gateway.service
```

Danach muss der Werkzeugtest aus `04-TESTPLAN.md` real ausgeführt werden. Eine
erfolgreiche Syntax-/Markerprüfung allein beweist die Funktion nicht, und ein
`already` ohne Neustart bedeutet: der laufende Gateway hat noch den alten Code.

## Wenn sich das Bundle-Layout ändert

Die Skripte suchen ihre Ankerzeilen wörtlich. Findet ein Skript seinen Anker nicht,
bricht es mit klarer Meldung ab und schreibt nichts:

```text
<label>: Anker nicht gefunden in <pfad> — Layout hat sich geaendert.
```

Dann Ankerzeile im neuen `dist` suchen, Skriptkonstante anpassen, erneut prüfen.
Niemals blind patchen.
