#!/usr/bin/env bash
# Grab a clean screenshot off a connected Android device/emulator.
# Demo mode is what turns a dev screenshot into a store-grade one: fixed 09:41 clock, full battery,
# full signal, no notification icons - the same trick Apple and Google use in their own marketing.
set -euo pipefail

OUT=""; SERIAL=""; DEMO=1; DELAY=0
usage() {
  cat <<'USAGE'
capture_screen.sh --out shot.png [--serial emulator-5554] [--no-demo] [--delay 2]
capture_screen.sh --demo-off [--serial ...]     # restore the real status bar when you are done
capture_screen.sh --list                        # show attached devices
USAGE
}

adbx() { if [[ -n "$SERIAL" ]]; then adb -s "$SERIAL" "$@"; else adb "$@"; fi; }

demo() { adbx shell am broadcast -a com.android.systemui.demo -e command "$@" >/dev/null; }

demo_on() {
  adbx shell settings put global sysui_demo_allowed 1 >/dev/null
  demo enter
  demo clock -e hhmm 0941
  demo battery -e level 100 -e plugged false
  demo network -e wifi show -e level 4
  demo network -e mobile show -e datatype none -e level 4
  demo notifications -e visible false
}

demo_off() { demo exit || true; }

MODE="capture"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2;;
    --serial) SERIAL="$2"; shift 2;;
    --no-demo) DEMO=0; shift;;
    --delay) DELAY="$2"; shift 2;;
    --demo-off) MODE="demo-off"; shift;;
    --list) MODE="list"; shift;;
    -h|--help) usage; exit 0;;
    *) echo "unknown arg: $1" >&2; usage; exit 1;;
  esac
done

case "$MODE" in
  list) adb devices -l; exit 0;;
  demo-off) demo_off; echo "status bar restored"; exit 0;;
esac

[[ -n "$OUT" ]] || { echo "--out is required" >&2; exit 1; }
if ! adbx get-state >/dev/null 2>&1; then
  echo "no device reachable. Boot the emulator (or plug in a phone) and re-run; 'adb devices' should list it." >&2
  exit 1
fi

[[ "$DEMO" == "1" ]] && demo_on
[[ "$DELAY" != "0" ]] && sleep "$DELAY"

mkdir -p "$(dirname "$OUT")"
adbx exec-out screencap -p > "$OUT"
[[ -s "$OUT" ]] || { echo "screencap produced an empty file" >&2; exit 1; }
echo "$OUT ($(magick identify -format '%wx%h' "$OUT" 2>/dev/null || echo 'size unknown'))"
