# 3. OpenClaw: deutsche Voice-Bestätigung

## Ursache

OpenClaw schützt verändernde Voice-Werkzeugaktionen. Der Aufruf wird zunächst
blockiert und an `agentId + voiceSessionId` gebunden. Erst eine spätere gesprochene
Bestätigung gibt genau diesen Werkzeugaufruf frei.

OpenClaw `2026.9.5` akzeptierte im installierten Bestätigungsmatcher englische
Formulierungen wie `yes`, `confirm`, `no` und `cancel`. GPT-Live sprach die
Rückfrage zwar auf Deutsch aus, aber `Ja, mache das` wurde nicht als Bestätigung
erkannt. Das führte zu einer erneuten Rückfrage oder zum Ablauf der Aktion.

## Patch anwenden

```bash
./scripts/apply-openclaw-german-confirmation.py
./scripts/verify-openclaw-german-confirmation.py
systemctl --user restart openclaw-gateway.service
```

Akzeptierte Bejahungen:

- `ja`
- `ja mach das`
- `ja mache das`
- `mach das` / `mache das`
- `ja führ das aus` / `ja führe das aus`
- `führ das aus` / `führe das aus`
- `bestätigen` / `bestätigt`

Akzeptierte Ablehnungen zusätzlich zu Englisch:

- `nein`
- `abbrechen`
- `stopp`

## Update-Regel

Der Patch liegt in kompilierten OpenClaw-`dist`-Dateien. Jedes OpenClaw-Update
kann diese ersetzen. Deshalb nach **jedem** Update:

```bash
./scripts/apply-openclaw-german-confirmation.py
./scripts/verify-openclaw-german-confirmation.py
systemctl --user restart openclaw-gateway.service
```

Danach muss der Werkzeugtest aus `04-TESTPLAN.md` real ausgeführt werden. Eine
erfolgreiche Syntaxprüfung allein beweist die Funktion nicht.

