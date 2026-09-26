#!/usr/bin/env python3
"""Wendet die aktiven OpenClaw-dist-Patches fuer den Jarvis-Voice-Pfad an.

Patch A - agent-tools.before-tool-call-*.mjs
    Deaktiviert die zusaetzliche Talk-Sprachbestaetigung vollstaendig
    (voice-confirmation-disabled-by-owner-v1).

Patch B - handlers-*.mjs  (Marker voice-persist-split-v3)
    Sorgt dafuer, dass User-Text und Assistant-Text beide gespeichert werden,
    aber GETRENNT und genau einmal pro Turn:
      - ohne Tool: der Relay schreibt Frage und Antwort (je 1x)
      - mit Tool:  der Consult schreibt die Antwort -> der Relay schweigt
    Verworfen wird nur die Zwischenansage ("I'll check that request"), weil sie
    der zweite Schreiber war und den SQLite-Konflikt ausloeste.

Beide Patches liegen in kompilierten dist-Dateien und werden von jedem
OpenClaw-Update ueberschrieben. Nach jedem Update erneut anwenden.
"""
from __future__ import annotations

import datetime
import pathlib
import subprocess
import sys

# ---------------------------------------------------------------- Patch A
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

# ---------------------------------------------------------------- Patch B
MARK_B = 'voice-persist-split-v3'

# B1: new relay field
B1_ANCHOR = '\t\tvoiceSessionCreated: false,\n\t\tvoiceTranscriptSeq: 0,\n'
B1_REPLACE = (
    '\t\tvoiceSessionCreated: false,\n'
    '\t\tvoiceTranscriptSeq: 0,\n'
    '\t\t// Set when a consult runs in the current turn; the consult already writes\n'
    '\t\t// the assistant answer, so the relay must not write it a second time.\n'
    '\t\tassistantOwnedByConsult: false,\n'
)

# B2: provider-direct consult hook (no openclaw_agent_consult tool call)
B2_ANCHOR = (
    '\t\t...runControl.handleDelegationInput ? { handleDelegationInput: (text, respond) => {\n'
    '\t\t\tconst relay = getActiveRelay();\n'
    '\t\t\tif (!relay) return "control";\n'
    '\t\t\treturn runControl.handleDelegationInput(text, (message) => {\n'
    '\t\t\t\tif (getActiveRelay() === relay) respond(message);\n'
    '\t\t\t});\n'
    '\t\t} } : {},\n'
)
B2_REPLACE = (
    '\t\t...runControl.handleDelegationInput ? { handleDelegationInput: (text, respond) => {\n'
    '\t\t\tconst relay = getActiveRelay();\n'
    '\t\t\tif (!relay) return "control";\n'
    '\t\t\tconst outcome = runControl.handleDelegationInput(text, (message) => {\n'
    '\t\t\t\tif (getActiveRelay() === relay) respond(message);\n'
    '\t\t\t});\n'
    '\t\t\t// voice-persist-split-v3\n'
    '\t\t\t// provider-direct consult: there is no openclaw_agent_consult tool call,\n'
    '\t\t\t// so mark the turn here. A real consult (outcome "consult") writes the\n'
    '\t\t\t// assistant answer; the relay must not write it a second time. Control\n'
    '\t\t\t// intents (status/cancel) keep "control" and do not mark the turn.\n'
    '\t\t\tif (outcome !== "control") relay.assistantOwnedByConsult = true;\n'
    '\t\t\treturn outcome;\n'
    '\t\t} } : {},\n'
)

# B3: tool-call consult hook (non-provider-direct routing)
B3_ANCHOR = '\t\t\tif (toolCall.name === "openclaw_agent_consult") {\n'
B3_REPLACE = (
    '\t\t\tif (toolCall.name === "openclaw_agent_consult") {\n'
    '\t\t\t\trelay.assistantOwnedByConsult = true;\n'
)

# B4: forced consult scheduler
B4_ANCHOR = (
    '\t\tconst itemId = `forced-consult-item-${randomUUID()}`;\n'
    '\t\tsession.harness.forcedConsults.markStarted(handle);\n'
)
B4_REPLACE = (
    '\t\tconst itemId = `forced-consult-item-${randomUUID()}`;\n'
    '\t\t// Forced consult writes the assistant answer too: keep the relay from\n'
    '\t\t// writing it a second time in the same turn.\n'
    '\t\tsession.assistantOwnedByConsult = true;\n'
    '\t\tsession.harness.forcedConsults.markStarted(handle);\n'
)

# B5: the transcript gate itself
B5_ANCHOR = '\t\t\tif (final && !enqueueRelayVoiceTranscript(relay, role, text)) return;\n'
B5_REPLACE = (
    '\t\t\t// voice-persist-split-v3\n'
    '\t\t\t// Owner-Vorgabe: User-Text und Assistant-Text sollen beide gespeichert\n'
    '\t\t\t// werden, aber GETRENNT und genau einmal pro Turn.\n'
    '\t\t\t//  - ohne Tool: der Relay schreibt Frage und Antwort (je 1x)\n'
    '\t\t\t//  - mit Tool:  der Consult schreibt die Antwort -> der Relay schweigt\n'
    '\t\t\t// Verworfen wird nur die Zwischenansage ("I\'ll check that request"),\n'
    '\t\t\t// weil sie der zweite Schreiber war und den SQLite-Konflikt ausloeste.\n'
    '\t\t\tif (final) {\n'
    '\t\t\t\t// A new finalized user question starts a new turn — but only when no\n'
    '\t\t\t\t// consult run is active. With consultRouting=provider-direct the consult\n'
    '\t\t\t\t// starts BEFORE the finalized user transcript is persisted, so clearing\n'
    '\t\t\t\t// here unconditionally would drop the marker again and the relay would\n'
    '\t\t\t\t// write the answer a second time.\n'
    '\t\t\t\tif (role === "user" && pruneInactiveRelayAgentRuns(relay) === 0) relay.assistantOwnedByConsult = false;\n'
    '\t\t\t\tif (role === "assistant") {\n'
    '\t\t\t\t\tconst spoken = String(text ?? "").trim();\n'
    '\t\t\t\t\tconst interimAck = /^(i[\'\\u2019]?ll check that request\\.?|ich pr\\u00fcfe das( kurz)?\\.?|einen moment( bitte)?\\.?)$/i.test(spoken);\n'
    '\t\t\t\t\tif (interimAck) return;\n'
    '\t\t\t\t\t// A consult already wrote the assistant answer for this turn.\n'
    '\t\t\t\t\tif (relay.assistantOwnedByConsult) return;\n'
    '\t\t\t\t\t// Second, independent guard: an agent run is still active.\n'
    '\t\t\t\t\tif (pruneInactiveRelayAgentRuns(relay) > 0) return;\n'
    '\t\t\t\t}\n'
    '\t\t\t\tif (!enqueueRelayVoiceTranscript(relay, role, text)) return;\n'
    '\t\t\t}\n'
)

B_EDITS = (
    ("field", B1_ANCHOR, B1_REPLACE),
    ("delegation-hook", B2_ANCHOR, B2_REPLACE),
    ("toolcall-hook", B3_ANCHOR, B3_REPLACE),
    ("forced-consult", B4_ANCHOR, B4_REPLACE),
    ("transcript-gate", B5_ANCHOR, B5_REPLACE),
)


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


def patch_handlers(path: pathlib.Path) -> str:
    if MARK_B in path.read_text():
        return "already"
    text = path.read_text()
    for label, anchor, replacement in B_EDITS:
        if anchor not in text:
            raise SystemExit(f"persist-split/{label}: Anker nicht gefunden in {path} — "
                             "Layout hat sich geaendert.")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path.with_name(path.name + f".bak-persist-split-{stamp}").write_text(text)
    for label, anchor, replacement in B_EDITS:
        text = text.replace(anchor, replacement, 1)
    path.write_text(text)
    reread = path.read_text()
    if MARK_B not in reread:
        raise SystemExit(f"persist-split: Verifikation nach dem Schreiben fehlgeschlagen: {path}")
    for label, _, _ in B_EDITS:
        pass
    for needle in ("assistantOwnedByConsult: false", 'outcome !== "control"',
                   "relay.assistantOwnedByConsult = true", "pruneInactiveRelayAgentRuns(relay) > 0"):
        if needle not in reread:
            raise SystemExit(f"persist-split: Teil {needle!r} fehlt nach dem Schreiben: {path}")
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
            result[f"transcript:{path.name}"] = patch_handlers(path)

    if not result:
        raise SystemExit("Keine passende OpenClaw-Implementierung gefunden.")
    for key, value in sorted(result.items()):
        print(f"{key}: {value}")
    print("Neustart noetig: systemctl --user restart openclaw-gateway.service")
    return 0


if __name__ == "__main__":
    sys.exit(main())
