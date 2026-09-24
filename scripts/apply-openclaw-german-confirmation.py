#!/usr/bin/env python3
from __future__ import annotations

import datetime
import pathlib
import subprocess
import sys

OLD_REFUSAL = r"const REFUSAL_PATTERN = /\b(no|don't|do not|cancel|stop|never mind)\b/;"
NEW_REFUSAL = r"const REFUSAL_PATTERN = /\b(no|don't|do not|cancel|stop|never mind|nein|abbrechen|stopp)\b/;"
OLD_AFFIRM = r"/^(yes|yes do it|do it|confirm|confirmed|go ahead|proceed|send it|make the change|restart it)$/"
NEW_AFFIRM = r"/^(yes|yes do it|do it|confirm|confirmed|go ahead|proceed|send it|make the change|restart it|ja|ja mach das|ja mache das|mach das|mache das|ja führ das aus|ja führe das aus|führ das aus|führe das aus|bestätigen|bestätigt)$/"

def npm_root() -> pathlib.Path:
    result = subprocess.run(["npm", "root", "-g"], check=True, text=True, capture_output=True)
    return pathlib.Path(result.stdout.strip())

dist = npm_root() / "openclaw" / "dist"
files = sorted(dist.glob("agent-tools.before-tool-call-*.mjs"))
if not files:
    raise SystemExit(f"No OpenClaw confirmation bundle found under {dist}")

changed = 0
verified = 0
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
for path in files:
    text = path.read_text()
    if "client-voice-confirmation.ts" not in text:
        continue
    if NEW_REFUSAL in text and NEW_AFFIRM in text:
        verified += 1
        continue
    if OLD_REFUSAL not in text or OLD_AFFIRM not in text:
        raise SystemExit(f"Unsupported OpenClaw bundle layout: {path}")
    backup = path.with_name(path.name + f".bak-german-confirmation-{stamp}")
    backup.write_text(text)
    patched = text.replace(OLD_REFUSAL, NEW_REFUSAL, 1).replace(OLD_AFFIRM, NEW_AFFIRM, 1)
    path.write_text(patched)
    reread = path.read_text()
    if NEW_REFUSAL not in reread or NEW_AFFIRM not in reread:
        raise SystemExit(f"Verification after write failed: {path}")
    changed += 1

if changed + verified == 0:
    raise SystemExit("No client voice confirmation implementation found")
print(f"German confirmation ready: changed={changed}, already_patched={verified}")
print("Restart required: systemctl --user restart openclaw-gateway.service")

