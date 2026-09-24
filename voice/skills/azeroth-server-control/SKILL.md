---
name: "azeroth-server-control"
description: "Stop, start, and verify the local AzerothCore WoW server services (worldserver/authserver) via non-interactive sudo systemctl."
---

# AzerothCore Server Control

Use for spoken requests like "schalte den WoW-Server aus", "starte den WoW-Server", "läuft der Server?".

- Services: `azeroth-authserver.service`, `azeroth-worldserver.service` (both `Restart=on-failure`).
- Console wrapper: `/home/openclaw/.openclaw/workspace-allgemein/scripts/azeroth-console.sh "COMMAND"`
- Deeper diagnosis (crash, hang, lag, builds): skill `azeroth-wow-server`.

All service control goes through non-interactive sudo, e.g. `sudo -n systemctl stop <service>`.
Never plain `systemctl`, `pkexec`, or any path that can raise a graphical polkit password
dialog. If `sudo -n` fails, report the task as blocked; do not ask for a password.

## Vertrauenswürdige Voice-Aktionen

Für gesprochene Start-/Stop-Aufträge ausschließlich diese registrierten
Aktionen verwenden. Keine direkten `systemctl`-Befehle erzeugen:

```bash
/home/openclaw/.local/bin/openclaw-voice-skill-action wow-server-start
/home/openclaw/.local/bin/openclaw-voice-skill-action wow-server-stop
```

Der Wrapper führt die unten dokumentierte Reihenfolge aus und prüft den
Endzustand. Nur seine exakten Aktions-IDs sind ohne zusätzliche Voice-
Bestätigung zugelassen. Andere Server- oder Systemaktionen bleiben gesperrt.

## Stop

1. Der Wrapper stoppt den Worldserver zuerst sauber, damit Spielerdaten gespeichert werden.
2. Danach stoppt er den Authserver.
3. Keep that order — the worldserver unit depends on the authserver.

## Start

1. Der Wrapper startet `azeroth-authserver.service`.
2. Danach startet er `azeroth-worldserver.service`.

## Verify

- `systemctl is-active azeroth-authserver.service azeroth-worldserver.service` → both
  `active` after a start, both `inactive` after a stop.

## Pitfalls

- A stop may take a while: `TimeoutStopUSec` is 2 min (authserver) and 5 min (worldserver),
  and a worldserver stop can even remain in `deactivating`. Check progress with
  `systemctl is-active` instead of retrying or escalating early.
- If the worldserver stays stuck in `deactivating`, end it with
  `sudo -n systemctl kill -s SIGKILL azeroth-worldserver`.
- Do not kill the authserver (or worldserver) process directly while a non-interactive
  systemd stop is still possible. The earlier claim that the authserver "ignores systemctl"
  came from an expired command timeout, not a service defect;
  `sudo -n systemctl stop azeroth-authserver.service` works and shuts it down cleanly.
