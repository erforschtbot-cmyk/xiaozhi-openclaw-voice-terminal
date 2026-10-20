#!/usr/bin/env bash
# Baut die bereits vorbereitete Jarvis-Firmware (MIT Kamera/Ring) im Image.
#
# Anders als build-firmware-audio-board.sh wird hier NICHTS geklont und NICHTS
# geloescht: der vorhandene Quellbaum mit der Kamera-/Ring-Arbeit wird direkt
# gebaut. Der Container kopiert ihn in ein Arbeitsverzeichnis und laesst den
# Host-Baum unberuehrt.
set -euo pipefail

src="${1:?Quellbaum als 1. Argument}"
out="${2:?Ausgabeverzeichnis als 2. Argument}"
image="jarvis-audio-board-builder:idf61"

if docker info >/dev/null 2>&1; then docker_cmd=(docker)
elif sudo -n docker info >/dev/null 2>&1; then docker_cmd=(sudo -n docker)
else echo "Docker nicht erreichbar" >&2; exit 1; fi

[ -f "$src/CMakeLists.txt" ] || { echo "Kein ESP-IDF-Projekt: $src" >&2; exit 1; }
mkdir -p "$out"

cname="jarvis-ringready-build-$$"
"${docker_cmd[@]}" rm -f "$cname" >/dev/null 2>&1 || true
"${docker_cmd[@]}" create --name "$cname" \
  -e FIRMWARE_BOARD_DIR=waveshare/esp32-s3-audio-board \
  -e FIRMWARE_BOARD_NAME=esp32-s3-audio-board \
  -e FIRMWARE_LANGUAGE=de-DE \
  -e FIRMWARE_WAKE_WORD=wn9_jarvis_tts \
  -e FIRMWARE_SOURCE_DIR=/src \
  -v "$src:/src:ro" \
  -v "$out:/output" \
  "$image" >/dev/null

rc=0
"${docker_cmd[@]}" start -a "$cname" || rc=$?
"${docker_cmd[@]}" cp "$cname:/output/." "$out/" 2>/dev/null || true
"${docker_cmd[@]}" rm -f "$cname" >/dev/null 2>&1 || true
echo "CONTAINER_EXIT=$rc"
ls -l "$out" 2>/dev/null | head -n 20
exit $rc
