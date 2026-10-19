# Conservative Alexa direct route

Created 2026-10-18 at the owner's request. Activation requires the owner to
restart the gateway; never restart it automatically. This is a local gateway
patch, not an upstream feature. Updates may replace it. The marker is
`jarvis-safe-router-v1` in `dist/handlers-*.mjs`.

## Architecture

Keep `disable-smart-home-fastpath` present. Neither Python bridge nor helper may
execute smart-home commands independently. The gateway's existing native
consult admission calls `routeSmartHome` for **only**
`agent:voice:xiaozhi-realtime-v6`, after checking voice session/cancellation.
It returns a direct result OR starts the ordinary agent. Never both.
Do not enable the older substring-based bridge fast path.

The router only accepts the exact native XML envelope with an input identical
to the complete single user transcript. Multiple transcript entries, rewritten
subcommands, tool-call paraphrases and unknown envelope formats fail closed to
the AI. This intentionally trades coverage for no partial execution.

Eligible commands: known unambiguous catalog target plus one on/off imperative,
matching the whole sentence. No fuzzy names. Conditions, timings, conjunctions,
questions and extra text go to the AI untouched. Not yet a general dimming,
temperature, blind or scene parser. High-consequence loads and arbitrary
virtual switches are not automatically admitted merely because Alexa lists them.

## Catalog

`node refresh-alexa-catalog.mjs` reads only Alexa2 objects and device definitions.
It uses `.powerState` capability and `native.friendlyName`, rejects duplicate
names/aliases, and atomically replaces `alexa-device-catalog.json` only on full
success. Daily timer `jarvis-alexa-catalog.timer`. A missing, corrupt or >48-hour
snapshot disables direct routing automatically; AI remains available.

Monitor and lamps are covered. The observed catalog names a fan `Ventilator
Arbeitszimmer`, not `Deckenventilator`; do not invent equivalence without owner
confirmation. Generic `Licht an` needs a unique known `Licht` target; there is no
assumed default room.

## Execution guarantees and limits

Only the fixed Echo textCommand endpoint is written. HTTP 200 means accepted,
not a verified physical state. No read-back, blind retry or agent fallthrough
after an attempted write. Error/timeout yields an honest uncertain result.
Concurrent identical device/action requests within the same voice session share
one in-memory promise for 8 seconds, including failures. Deliberate identical
repeats in that interval are also suppressed. Cross-device wake arbitration is
still the bridge's job; this does not add a global cross-device guarantee.

The normal speech completion/playback-drained chain is unchanged. The direct
route skips the tool-agent LLM, not speech recognition or native delegation.
Speech pauses can still split separate utterances; no parser can foresee a
continuation after the recognizer has finalized a sentence.

## Verification and rollback

`node --test test-smart-home-router.mjs` uses fake sends: no real devices switch.
`node --check smart-home-router.mjs` and `node --check <gateway handler>`.
After owner restart: test a simple command; gateway log must contain exactly one
`[jarvis-fast-route] accepted` and there must be no agent tool execution for it.
Then test a complex request: no direct-route accepted line, normal agent consult.
Verify audible completion and follow-up listening on the real device.

The original handler backup is `handlers-De0Uc7cE.mjs.before-safe-router`.
For rollback, remove ONLY the `jarvis-safe-router-v1` block from the current
handler (do not overwrite newer unrelated changes with the old full backup),
then ask the owner to restart. Do not delete old sessions or firmware.
