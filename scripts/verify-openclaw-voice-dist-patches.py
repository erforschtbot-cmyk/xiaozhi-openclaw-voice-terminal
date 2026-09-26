#!/usr/bin/env python3
"""Prueft, dass beide Voice-dist-Patches aktiv sind (siehe apply-...-dist-patches.py)."""
import pathlib
import subprocess

root = pathlib.Path(subprocess.run(["npm", "root", "-g"], check=True, text=True,
                                   capture_output=True).stdout.strip())
dist = root / "openclaw" / "dist"

confirm = [p for p in sorted(dist.glob("agent-tools.before-tool-call-*.mjs"))
           if "client-voice-confirmation.ts" in p.read_text()]
assert confirm, "Kein Bewaestigungs-Bundle gefunden"
for path in confirm:
    assert "voice-confirmation-disabled-by-owner-v1" in path.read_text(), f"Patch A fehlt: {path}"

handlers = [p for p in sorted(dist.glob("handlers-*.mjs"))
            if "enqueueRelayVoiceTranscript" in p.read_text()]
assert handlers, "Kein Relay-Handler gefunden"
for path in handlers:
    assert "voice-persist-split-v3" in path.read_text(), f"Patch B fehlt: {path}"

print("Voice-dist-Patches verifiziert:")
for path in confirm + handlers:
    print(" ", path)
