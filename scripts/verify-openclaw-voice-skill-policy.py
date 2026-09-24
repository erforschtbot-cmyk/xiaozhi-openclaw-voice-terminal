#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import subprocess


root = pathlib.Path(subprocess.run(["npm", "root", "-g"], check=True, text=True, capture_output=True).stdout.strip())
files = sorted((root / "openclaw" / "dist").glob("agent-tools.before-tool-call-*.mjs"))
matching = []
for path in files:
    text = path.read_text()
    if "client-voice-confirmation.ts" not in text:
        continue
    matching.append(path)
    assert "xiaozhi-trusted-voice-skill-policy-v1" in text, f"Policy marker missing in {path}"
    assert "if (isPreauthorizedVoiceSkillAction(params)) return { allowed: true };" in text
    assert 'params.agentId !== "voice"' in text
    assert 'params.toolName.trim().toLowerCase() !== "exec"' in text
    assert "wow-server-(?:start|stop)" in text
    assert "alexa-smart-home|azeroth-gm-safe" in text
    assert '"command", "title", "timeout"' in text
    assert '(?:${payload}|"${payload}"|\'${payload}\')' in text
assert matching, "No OpenClaw voice confirmation bundle found"

wrapper = pathlib.Path.home() / ".local" / "bin" / "openclaw-voice-skill-action"
subprocess.run([str(wrapper), "--self-test"], check=True)

# Mirror the complete-string policy boundary with representative calls. This
# catches accidental widening to shell chaining or unregistered actions.
payload = r"[A-Za-z0-9._~%+-]+"
pattern = re.compile(
    rf"^{re.escape(str(wrapper))} "
    rf'(?:wow-server-(?:start|stop)|(?:alexa-smart-home|azeroth-gm-safe) (?:{payload}|"{payload}"|\'{payload}\'))$'
)
accepted = [
    f"{wrapper} wow-server-start",
    f"{wrapper} wow-server-stop",
    f"{wrapper} alexa-smart-home Licht%20an",
    f'{wrapper} alexa-smart-home "Licht%20an"',
    f"{wrapper} alexa-smart-home 'Licht%20an'",
    f"{wrapper} azeroth-gm-safe tele%20name%20Priestilia%20Dalaran",
]
rejected = [
    f"{wrapper} format-disk",
    f"{wrapper} wow-server-start; rm -rf /tmp/example",
    f"{wrapper} alexa-smart-home Licht%20an && id",
    f"{wrapper} alexa-smart-home 'Licht%20an' && id",
    f"sudo {wrapper} wow-server-start",
    "sudo -n systemctl start azeroth-worldserver.service",
]
assert all(pattern.fullmatch(value) for value in accepted)
assert not any(pattern.fullmatch(value) for value in rejected)
print("Trusted Voice skill policy verified:")
for path in matching:
    print(path)
