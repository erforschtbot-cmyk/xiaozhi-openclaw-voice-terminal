---
name: "azeroth-gm-voice"
description: "Fast German voice control of local AzerothCore GM console for Priestilia, teleports, recall, lookup, and server commands."
---

# AzerothCore GM Voice

This skill is self-contained. Act directly; do not first search for connection details.

## Access — use exactly this

Everything runs on this Linux host; no SSH is needed.

- Character: `Priestilia` (the user's phrases `ich`, `mich`, `mir`, `mein Charakter` mean Priestilia).
- GM console wrapper: `/home/openclaw/.openclaw/workspace-allgemein/scripts/azeroth-console.sh`
- Call: `/home/openclaw/.openclaw/workspace-allgemein/scripts/azeroth-console.sh "COMMAND"`
- Commands passed to the wrapper have no leading dot.
- Wrapper already reads protected SOAP credentials from `/home/openclaw/azeroth-server/etc/.soap-credentials`; never read or reveal that file.
- MariaDB login: `mariadb -u acore -pacore -h 127.0.0.1`
- World DB: `acore_world_playerbot`
- Character DB: `acore_characters_playerbot`
- Auth DB: `acore_auth`
- Worldserver service: `azeroth-worldserver.service`
- Authserver service: `azeroth-authserver.service`

## Immediate language mapping

Mutating requests listed below as immediate must use the trusted wrapper. URL-
encode the complete GM console command as one argument:

```bash
/home/openclaw/.local/bin/openclaw-voice-skill-action \
  azeroth-gm-safe tele%20name%20Priestilia%20Dalaran
```

The wrapper accepts only positive `additem`, `tele name Priestilia`,
`recall Priestilia`, and `saveall`. It rejects negative item counts, level
changes, kick, restart/shutdown, database edits, shell syntax, and unknown GM
commands. Never bypass it with a direct console call for immediate Voice writes.

Execute reversible requests immediately:

- `gib mir N <item>` -> find local item ID, then `additem Priestilia ID N`.
- `entferne mir N <item>` -> confirm first, then `additem Priestilia ID -N`.
- `porte mich nach <place>` -> `tele name Priestilia TARGET`, wait, `saveall`, verify.
- `porte mich zurück`, `zurück`, `nach hier` -> `recall Priestilia`, wait, `saveall`, verify.
- `wo bin ich?` -> `pinfo Priestilia`.
- `speichern` -> `saveall`.
- `Serverstatus` -> `server info`.

Do not ask which character when the user says ich/mich/mir: always use Priestilia unless another character is explicitly named.

## Teleport and return

`tele name Priestilia TARGET` automatically saves the departure position in AzerothCore's recall slot. This recall slot is the user's conceptual temporary `hier`. Never create a literal teleport named `hier`.

- Return command: `recall Priestilia` (requires Priestilia online).
- Never logout or kick Priestilia after a successful online teleport.

Fixed aliases:

- SW/Sturmwind/Stormwind -> `Stormwind`
- SW zur Bank/Sturmwind zur Bank/Bank in SW -> `StormwindBank`
- Eisenschmiede -> `Ironforge`
- Darnassus -> `Darnassus`
- Exodar -> `TheExodar`
- Dalaran -> `Dalaran`
- Dalaran zur Bank -> `TheBankOfDalaran`
- Shattrath -> `Shattrath`
- Orgrimmar -> `Orgrimmar`
- Unterstadt -> `Undercity`
- Silbermond -> `SilvermoonCity`
- Donnerfels -> `ThunderBluff`

Unknown place: run `lookup tele SHORTTERM`; if needed query local DB before any web search.

### Teleport zu einem NPC (z. B. Boss) — allgemeine Methode

Der Befehl `teleport name Priestilia ORT` (nicht `tele name`) akzeptiert NUR Einträge aus der `game_tele`-Tabelle, keine rohen Koordinaten und keinen NPC-Namen. Um Priestilia direkt zu einem NPC zu portieren:

1. NPC-Position aus der DB holen (Map + Koordinaten):
   ```bash
   mariadb -u acore -pacore -h 127.0.0.1 -N -e "SELECT c.guid,c.id,c.map,c.position_x,c.position_y,c.position_z FROM acore_world_playerbot.creature c JOIN acore_world_playerbot.creature_template ct ON ct.entry=c.id WHERE LOWER(ct.name) LIKE LOWER('%NAME%') LIMIT 10;"
   ```
2. game_tele-Eintrag anlegen (id = MAX(id)+1, hier 10000; Spalten prüfen mit `SHOW COLUMNS FROM acore_world_playerbot.game_tele;` — nur id, position_x/y/z, orientation, map, name):
   ```bash
   mariadb -u acore -pacore -h 127.0.0.1 -e "INSERT INTO acore_world_playerbot.game_tele (id,position_x,position_y,position_z,orientation,map,name) VALUES (10000,<X>,<Y>,<Z>,0,<MAP>,'<NAME>');"
   ```
3. Reload + verifizieren:
   ```bash
   azeroth-console.sh "reload game_tele"
   azeroth-console.sh "lookup tele <NAME>"   # muss den Eintrag zeigen
   ```
4. Portieren, warten, speichern, verifizieren:
   ```bash
   azeroth-console.sh "teleport name Priestilia <NAME>"
   sleep 5; azeroth-console.sh "saveall"
   azeroth-console.sh "pinfo Priestilia"   # Map/Zone muss stimmen
   ```

Wichtig: `teleport name` ist der korrekte Befehl; `tele name` schlägt fehl. Der Eintrag bleibt dauerhaft in game_tele und kann wiederverwendet werden.

## Local-first lookup

Use this order: fixed mapping -> console lookup -> local MariaDB -> web fallback. Never start with the internet.

Console lookups:

- `lookup item NAME`
- `lookup tele NAME`
- `lookup creature NAME`
- `lookup quest NAME`
- `help COMMAND`

German item lookup in local DB:

```bash
mariadb -u acore -pacore -h 127.0.0.1 -N -e "SELECT it.entry,l.Name,it.name FROM acore_world_playerbot.item_template it JOIN acore_world_playerbot.item_template_locale l ON l.ID=it.entry AND l.locale='deDE' WHERE LOWER(l.Name) LIKE LOWER('%SEARCH%') ORDER BY it.entry LIMIT 30;"
```

Teleport lookup:

```bash
mariadb -u acore -pacore -h 127.0.0.1 -N -e "SELECT id,name,map,position_x,position_y,position_z FROM acore_world_playerbot.game_tele WHERE LOWER(name) LIKE LOWER('%SEARCH%') ORDER BY name LIMIT 50;"
```

NPC/position lookup: join `creature_template_locale(entry,locale,Name)` -> `creature_template(entry)` -> `creature(id,map,position_x,position_y,position_z)`. Quests use `quest_template_locale(ID,locale,Title)`. Gameobjects use `gameobject_template_locale(entry,locale,name)` plus their spawn table.

If local data is insufficient, use `https://wotlkdb.com/` first (3.3.5a), then `https://www.wowhead.com/wotlk/database`; verify any web ID/coordinates against the local DB before acting.

## Exact command map

- `server info`
- `saveall`
- `pinfo Priestilia`
- `tele name Priestilia LOCATION`
- `recall Priestilia`
- `tele name Priestilia $home`
- `lookup tele TEXT`
- `lookup item TEXT`
- `lookup creature TEXT`
- `lookup quest TEXT`
- `additem Priestilia ITEM_ID COUNT`
- `character level Priestilia LEVEL_OR_DELTA`
- `tele del NAME`
- `reload game_tele`
- `server restart DELAY`
- `server restart cancel`
- `kick CHARACTER REASON`

Ask before destructive/broad operations: negative item count, level change, kick, database/config edits, shutdown/restart. Normal give-item, teleport, recall, lookup, save, pinfo, and status requests execute immediately.

If syntax is missing, run only `help LIKELY_COMMAND` through the wrapper; do not browse general documentation first.

## Verification and spoken response

- Inspect SOAP `<result>` text, not only curl exit status.
- For teleport/recall: wait about 5 seconds, run `saveall`, verify with `pinfo Priestilia` and/or the character DB. Teleport completion can lag until client acknowledgement.
- For item grants: confirm SOAP result and, when practical, inventory state.
- For restart: verify both services active and journal markers `worldserver-daemon) ready...` plus `mod-dungeon-clear: registered...`.
- Reply in natural German with one short result sentence; no command explanation unless asked.
