#!/usr/bin/env python3
import pathlib
import subprocess

root = pathlib.Path(subprocess.run(["npm", "root", "-g"], check=True, text=True, capture_output=True).stdout.strip())
files = sorted((root / "openclaw" / "dist").glob("agent-tools.before-tool-call-*.mjs"))
matching = []
for path in files:
    text = path.read_text()
    if "client-voice-confirmation.ts" in text:
        matching.append(path)
        assert "nein|abbrechen|stopp" in text, f"German refusal missing in {path}"
        assert "ja mache das" in text, f"German affirmation missing in {path}"
assert matching, "No OpenClaw voice confirmation bundle found"
print("German OpenClaw voice confirmation verified:")
for path in matching:
    print(path)

