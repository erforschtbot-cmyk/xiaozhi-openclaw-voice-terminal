#!/usr/bin/env python3
from __future__ import annotations

import datetime
import pathlib
import subprocess


MARKER = "xiaozhi-trusted-voice-skill-policy-v1"
ANCHOR = "function resolveClientVoiceToolConfirmationPolicy(params, consume) {\n"
PATCH = r'''// xiaozhi-trusted-voice-skill-policy-v1
function isPreauthorizedVoiceSkillAction(params) {
	if (params.agentId !== "voice" || params.toolName.trim().toLowerCase() !== "exec") return false;
	if (!params.toolParams || typeof params.toolParams !== "object" || Array.isArray(params.toolParams)) return false;
	const keys = Object.keys(params.toolParams);
	if (keys.some((key) => !["command", "title", "timeout", "yieldMs", "yield_time-ms", "maxOutputChars"].includes(key))) return false;
	const command = params.toolParams.command;
	if (typeof command !== "string") return false;
	const wrapper = path.join(os.homedir(), ".local", "bin", "openclaw-voice-skill-action");
	const escaped = wrapper.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
	const payload = "[A-Za-z0-9._~%+-]+";
	return new RegExp(`^${escaped} (?:wow-server-(?:start|stop)|(?:alexa-smart-home|azeroth-gm-safe) (?:${payload}|"${payload}"|'${payload}'))$`).test(command);
}
'''


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
    if MARKER in text:
        verified += 1
        continue
    if ANCHOR not in text:
        raise SystemExit(f"Unsupported OpenClaw bundle layout: {path}")
    backup = path.with_name(path.name + f".bak-voice-skill-policy-{stamp}")
    backup.write_text(text)
    patched = text.replace(ANCHOR, PATCH + ANCHOR, 1)
    policy_gate = (
        ANCHOR
        + "\tif (!params.agentId || !params.voiceSessionId) return { allowed: true };\n"
    )
    replacement = policy_gate + "\tif (isPreauthorizedVoiceSkillAction(params)) return { allowed: true };\n"
    if policy_gate not in patched:
        raise SystemExit(f"Voice confirmation gate changed unexpectedly: {path}")
    patched = patched.replace(policy_gate, replacement, 1)
    path.write_text(patched)
    reread = path.read_text()
    if MARKER not in reread or "isPreauthorizedVoiceSkillAction(params)" not in reread:
        raise SystemExit(f"Verification after write failed: {path}")
    changed += 1

if changed + verified == 0:
    raise SystemExit("No client voice confirmation implementation found")
print(f"Voice skill policy ready: changed={changed}, already_patched={verified}")
print("Restart required: systemctl --user restart openclaw-gateway.service")
