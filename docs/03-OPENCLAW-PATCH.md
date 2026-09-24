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

## Vertrauenswürdige Skill-Aktionen ohne zweite Rückfrage

Die normale OpenClaw-Voice-Sperre bleibt aktiv. Nur Aufrufe des lokal
installierten Wrappers werden vorautorisiert:

```text
$HOME/.local/bin/openclaw-voice-skill-action
```

Der Core-Patch akzeptiert ausschließlich komplette `exec`-Befehle in diesen
Formen:

```text
openclaw-voice-skill-action wow-server-start
openclaw-voice-skill-action wow-server-stop
openclaw-voice-skill-action alexa-smart-home <URL-kodierter-Text>
openclaw-voice-skill-action azeroth-gm-safe <URL-kodierter-GM-Befehl>
```

Die Freigabe gilt nur für `agentId=voice`, das lokale `exec`-Werkzeug und eine
vollständige Übereinstimmung. Zusätzliche Shell-Operatoren, unbekannte Aktionen,
direkte `systemctl`-/`curl`-Befehle sowie andere Werkzeuge fallen weiterhin in
die normale Ja/Nein-Bestätigung.

Der Wrapper validiert die zweite Grenze selbst. `azeroth-gm-safe` akzeptiert nur
positive `additem`-Aufrufe, Teleport, Recall und `saveall`. Negative Itemzahlen,
Leveländerungen, Kick, Restart/Shutdown und Datenbankoperationen werden dort
blockiert.

Installation und Patch:

```bash
install -Dm0755 scripts/openclaw-voice-skill-action \
  "$HOME/.local/bin/openclaw-voice-skill-action"
./scripts/apply-openclaw-voice-skill-policy.py
./scripts/verify-openclaw-voice-skill-policy.py
systemctl --user restart openclaw-gateway.service
```

Nach jedem OpenClaw-Update müssen **beide** Patches erneut angewendet und
verifiziert werden:

```bash
./scripts/apply-openclaw-german-confirmation.py
./scripts/apply-openclaw-voice-skill-policy.py
./scripts/verify-openclaw-german-confirmation.py
./scripts/verify-openclaw-voice-skill-policy.py
systemctl --user restart openclaw-gateway.service
```
