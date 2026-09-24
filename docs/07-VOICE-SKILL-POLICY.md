# 7. Voice-Skill-Policy

## Vertrauensmodell

Eine klare gesprochene Anweisung ist nur dann ohne zweite Ja/Nein-Rückfrage
vorautorisiert, wenn der zuständige lokale Skill exakt den installierten Wrapper
aufruft:

```text
$HOME/.local/bin/openclaw-voice-skill-action <registrierte Aktion> [Payload]
```

Eine beliebige Skill- oder Markdown-Datei ist keine Autorität. Der Agent darf
keine freien Befehle als vorautorisiert kennzeichnen. Der OpenClaw-Patch prüft
den endgültigen vollständigen `exec`-Aufruf; der Wrapper validiert anschließend
die konkrete Aktion und alle variablen Werte.

## Aktionsregister

| Aktions-ID | Quelle | Zulässige Wirkung |
|---|---|---|
| `wow-server-start` | `azeroth-server-control` | Nur Authserver und Worldserver in fester Reihenfolge starten und prüfen |
| `wow-server-stop` | `azeroth-server-control` | Nur Worldserver sauber, danach Authserver stoppen und prüfen |
| `alexa-smart-home` | `alexa-smart-home` | Nur Text an den festen ioBroker-`textCommand`-Datenpunkt senden |
| `azeroth-gm-safe` | `azeroth-gm-voice` | Nur positive Items, Teleport, Recall und `saveall` |

Nicht registriert und weiterhin bestätigungspflichtig sind insbesondere freie
Shell-Befehle, Datei-/Datenträgeroperationen, Nachrichten, Publikationen,
Serverlöschung, negative Items, Leveländerung, Kick, Neustart/Shutdown und
Datenbankänderungen.

## Einbau in den Agenten `voice`

Vollständige Wiederherstellung auf dem Zielhost:

```bash
./scripts/install-voice-policy.sh
systemctl --user restart openclaw-gateway.service
```

Das Skript installiert den Wrapper, die versionierten Agenten-/Skill-Dateien,
beide OpenClaw-Patches und führt alle statischen Verifikationen aus.

Die dauerhafte Agentenregel lautet:

```text
Nur eine vom passenden Skill ausdrücklich über
$HOME/.local/bin/openclaw-voice-skill-action registrierte Aktion ist ohne zweite
Voice-Bestätigung erlaubt. Direkte exec-Aufrufe, freie Herleitungen und bloße
MD-Erwähnungen bleiben unter der normalen OpenClaw-Bestätigung.
```

Die drei Skill-Aufrufformen:

```bash
$HOME/.local/bin/openclaw-voice-skill-action wow-server-start
$HOME/.local/bin/openclaw-voice-skill-action wow-server-stop
$HOME/.local/bin/openclaw-voice-skill-action alexa-smart-home Licht%20an
$HOME/.local/bin/openclaw-voice-skill-action azeroth-gm-safe tele%20name%20Priestilia%20Dalaran
```

Payloads müssen vollständig URL-kodiert sein. Niemals Shell-Operatoren,
Substitutionen, Umleitungen oder Zusatzbefehle anhängen.

## Neue Aktion ergänzen

1. Implementiere und validiere die Aktion in
   `scripts/openclaw-voice-skill-action`; fertig, wenn ungültige Parameter vor
   jeder Wirkung abgewiesen werden.
2. Ergänze ausschließlich die konkrete Aktionsform im vollständigen Regex von
   `scripts/apply-openclaw-voice-skill-policy.py`; fertig, wenn keine Präfix-
   oder Shell-Verkettung passt.
3. Ergänze positive und negative Fälle in Wrapper-Selbsttest und
   `verify-openclaw-voice-skill-policy.py`; fertig, wenn unbekannte sowie
   erweiterte Befehle abgewiesen werden.
4. Verweise im zuständigen vertrauenswürdigen Skill auf die exakte Wrapper-
   Form; fertig, wenn der Agent keinen direkten mutierenden Ersatzweg erhält.
5. Patch anwenden, Gateway neu starten und einen echten positiven sowie einen
   bestätigungspflichtigen negativen Sprachtest durchführen.
