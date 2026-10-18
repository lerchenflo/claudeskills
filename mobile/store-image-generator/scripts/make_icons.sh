#!/usr/bin/env bash
# Export the store app icons from one square master: 1024x1024 (App Store) and 512x512 (Play Store).
# Requires ImageMagick 7 (`magick`).
set -euo pipefail

SRC=""; OUT_DIR="storeassets/icon"; BG=""

usage() {
  cat <<'USAGE'
make_icons.sh --src app_icon_fullbleed.png [--out-dir storeassets/icon] [--bg '#3A6284']

--src   square master, ideally 1024x1024 or larger, full-bleed (no rounded corners, no padding).
--bg    colour to flatten transparency onto; needed when the master has alpha. Take it from the
        icon's own background (or the adaptive icon's background layer), never invent one.

Writes <out-dir>/appstore-1024.png (RGB, no alpha - App Store rejects alpha) and
<out-dir>/play-512.png (PNG, 512x512, also flattened).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src) SRC="$2"; shift 2;;
    --out-dir) OUT_DIR="$2"; shift 2;;
    --bg) BG="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "unknown arg: $1" >&2; usage; exit 1;;
  esac
done

[[ -f "$SRC" ]] || { echo "missing --src file: $SRC" >&2; exit 1; }
read -r W H CH <<< "$(magick identify -format '%w %h %[channels]' "$SRC")"
(( W == H )) || { echo "master is ${W}x${H}, must be square" >&2; exit 1; }
(( W < 1024 )) && echo "warning: master is only ${W}px - the 1024 export will be upscaled and soft" >&2
if [[ "$CH" == *a* && -z "$BG" ]]; then
  echo "master has an alpha channel - pass --bg with the icon's background colour" >&2; exit 1
fi

mkdir -p "$OUT_DIR"
FLAT=(); [[ -n "$BG" ]] && FLAT=(-background "$BG" -alpha remove)
for spec in "appstore-1024:1024" "play-512:512"; do
  name="${spec%%:*}"; px="${spec##*:}"
  magick "$SRC" "${FLAT[@]}" -alpha off -filter Lanczos -resize "${px}x${px}" -strip "$OUT_DIR/$name.png"
  echo "$OUT_DIR/$name.png ($(magick identify -format '%wx%h %[channels]' "$OUT_DIR/$name.png"))"
done
