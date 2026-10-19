# Jarvis GUI-compatible realtime — 2026-10-13

Active profile: realtime. Wakeword and firmware unchanged.
Uses talk.session.create with the same default resolution as GUI relay:
mode=realtime, transport=gateway-relay, brain=agent-consult.
No forced model, voice, reasoning or 3000 ms VAD pause.
Observed resolved provider/model: openai / gpt-live-1-codex.
Gateway-managed GPT-Live consult routes tools into agent:voice:xiaozhi-realtime-v5.
The helper retains talk.client.toolCall handling for client-delegating providers.
No extra Allgemein consult session. Global Talk instructions are inherited.
GUI browser-local voice overrides are not copied; gateway defaults are used.

## Backup / switching
Local STT/TTS helper files and local services are unchanged.
Local profile preserves the original systemd command verbatim.
Switch locally (only bridge restarts, never Gateway):
  ~/.local/share/jarvis-realtime-bridge/voice-mode local
Switch back:
  ~/.local/share/jarvis-realtime-bridge/voice-mode realtime
No automatic failover is installed.

## Tests and boundaries
Real provider audio probe: response started about 515 ms after speech end
in a warmed session (single synthetic test, not hardware latency guarantee).
Opus bridge probe: STT + 63 output packets + stream_end passed.
Cold session startup measured 2.74 s; existing hello prewarm remains enabled.
10-second follow-up window and session keys unchanged.
When the microphone pauses, a bounded 60 ms silence pump maintains the
provider audio stream, matching continuous GUI capture without speaker echo.
Tool route verified in test-session history: voice agent -> session_status ->
spoken current time; transcript persistence confirmed.
Provider sometimes still speaks an English interim acknowledgement despite
the existing global German instructions; no global config patched.
Microphone forwarding is still paused during playback (no full-duplex barge-in).
Hardware wakeword, acoustic echo, speaker playback remain to be tested by owner.
