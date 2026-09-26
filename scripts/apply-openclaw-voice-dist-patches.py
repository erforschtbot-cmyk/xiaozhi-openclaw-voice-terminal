#!/usr/bin/env python3
"""Wendet die beiden aktiven OpenClaw-dist-Patches fuer den Jarvis-Voice-Pfad an.

Patch A - agent-tools.before-tool-call-*.mjs
    Deaktiviert die zusaetzliche Talk-Sprachbestaetigung vollstaendig
    (voice-confirmation-disabled-by-owner-v1).

Patch B - handlers-*.mjs
    Unterdrueckt das Persistieren des Assistant-/Provider-Transkripts in die
    Voice-Session (voice-test-suppress-assistant-persist-v1). Das User-Transkript
    bleibt erhalten.

Beide Patches liegen in kompilierten dist-Dateien und werden von jedem
OpenClaw-Update ueberschrieben. Nach jedem Update erneut anwenden.
"""
from __future__ import annotations

import datetime
import pathlib
import subprocess
import sys

ANCHOR_A = (
    'function resolveClientVoiceToolConfirmationPolicy(params, consume) {\n'
    '\tif (!params.agentId || !params.voiceSessionId) return { allowed: true };\n'
)
PATCH_A = (
    ANCHOR_A
    + '\t// voice-confirmation-disabled-by-owner-v1\n'
    + '\t// The owner explicitly disabled the additional Talk voice confirmation.\n'
    + '\t// No command, argument, punctuation, quoting, or wording filter is used.\n'
    + '\treturn { allowed: true };\n'
)
MARK_A = 'voice-confirmation-disabled-by-owner-v1'

ANCHOR_B = '\t\t\tif (final && !enqueueRelayVoiceTranscript(relay, role, text)) return;\n'
PATCH_B = (
    '\t\t\t// voice-test-suppress-assistant-persist-v1\n'
    '\t\t\t// Owner-Test: Assistant-/Provider-Transkript (KI-Antwort + "check request")\n'
    '\t\t\t// wird NICHT mehr in die Session geschrieben. User-Transkript bleibt.\n'
    '\t\t\tif (final && role !== "assistant" && !enqueueRelayVoiceTranscript(relay, role, text)) return;\n'
)
MARK_B = 'voice-test-suppress-assistant-persist-v1'


def patch(path: pathlib.Path, anchor: str, replacement: str, marker: str, label: str) -> str:
    text = path.read_text()
    if marker in text:
        return "already"
    if anchor not in text:
        raise SystemExit(f"{label}: Anker nicht gefunden in {path} — Layout hat sich geaendert.")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path.with_name(path.name + f".bak-{label}-{stamp}").write_text(text)
    path.write_text(text.replace(anchor, replacement, 1))
    if marker not in path.read_text():
        raise SystemExit(f"{label}: Verifikation nach dem Schreiben fehlgeschlagen: {path}")
    return "changed"


def main() -> int:
    root = pathlib.Path(subprocess.run(["npm", "root", "-g"], check=True, text=True,
                                       capture_output=True).stdout.strip())
    dist = root / "openclaw" / "dist"
    result = {}

    tool_files = sorted(dist.glob("agent-tools.before-tool-call-*.mjs"))
    if not tool_files:
        raise SystemExit(f"Kein OpenClaw-Bundle unter {dist}")
    for path in tool_files:
        if "client-voice-confirmation.ts" in path.read_text():
            result[f"confirm:{path.name}"] = patch(path, ANCHOR_A, PATCH_A, MARK_A, "voice-confirm-off")

    handler_files = sorted(dist.glob("handlers-*.mjs"))
    for path in handler_files:
        if "enqueueRelayVoiceTranscript" in path.read_text():
            result[f"transcript:{path.name}"] = patch(path, ANCHOR_B, PATCH_B, MARK_B, "persist-off")

    if not result:
        raise SystemExit("Keine passende OpenClaw-Implementierung gefunden.")
    for key, value in sorted(result.items()):
        print(f"{key}: {value}")
    print("Neustart noetig: systemctl --user restart openclaw-gateway.service")
    return 0


if __name__ == "__main__":
    sys.exit(main())
