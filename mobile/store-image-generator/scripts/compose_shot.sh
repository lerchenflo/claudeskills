#!/usr/bin/env bash
# Compose one App Store screenshot: caption on top, framed device below, brand gradient behind.
# Requires ImageMagick 7 (`magick`).
set -euo pipefail

SHOT=""; OUT=""; CAPTION=""; SIZE="1206x2622"
BG1=""; BG2=""; FG="#FFFFFF"; FRAME="#111111"; FONT=""
DEVICE_WIDTH_PCT=74      # device width as % of canvas width
CAPTION_TOP_PCT=7        # caption band starts at this % of canvas height
DEVICE_TOP_PCT=27        # device top edge at this % of canvas height
BLEED=0                  # 1 = let device run off the bottom edge (cropped), 0 = fit fully

usage() {
  cat <<'USAGE'
compose_shot.sh --shot IN.png --out OUT.png --caption "Line one\nLine two" \
                --bg1 '#006E2C' --bg2 '#1ED660' [--fg '#FFFFFF'] [--frame '#111111'] \
                [--font /path/font.ttf] [--size 1206x2622] [--device-width 74] \
                [--caption-top 7] [--device-top 27] [--bleed] [--caption-size 6] \
                [--callout X,Y,W,H] [--callout-scale 1.3] [--callout-anchor center|top|bottom] [--radial]

--callout lifts a region of the raw screenshot (source pixels) out of the device, enlarged by
--callout-scale, as a floating card over the spot it came from.

Every colour comes from the app's own theme - never invent one.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --shot) SHOT="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --caption) CAPTION="$2"; shift 2;;
    --size) SIZE="$2"; shift 2;;
    --bg1) BG1="$2"; shift 2;;
    --bg2) BG2="$2"; shift 2;;
    --fg) FG="$2"; shift 2;;
    --frame) FRAME="$2"; shift 2;;
    --font) FONT="$2"; shift 2;;
    --device-width) DEVICE_WIDTH_PCT="$2"; shift 2;;
    --caption-top) CAPTION_TOP_PCT="$2"; shift 2;;
    --device-top) DEVICE_TOP_PCT="$2"; shift 2;;
    --bleed) BLEED=1; shift;;
    --callout) CALLOUT="$2"; shift 2;;
    --radial) RADIAL=1; shift;;
    --callout-anchor) CALLOUT_ANCHOR="$2"; shift 2;;
    --callout-scale) CALLOUT_SCALE="$2"; shift 2;;
    --caption-size) CAPTION_SIZE_PCT="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "unknown arg: $1" >&2; usage; exit 1;;
  esac
done

RADIAL="${RADIAL:-0}"; CALLOUT_ANCHOR="${CALLOUT_ANCHOR:-center}"; CALLOUT="${CALLOUT:-}"; CALLOUT_SCALE="${CALLOUT_SCALE:-1.3}"; CAPTION_SIZE_PCT="${CAPTION_SIZE_PCT:-6}"

[[ -f "$SHOT" ]] || { echo "missing --shot file: $SHOT" >&2; exit 1; }
[[ -n "$OUT" && -n "$BG1" && -n "$BG2" ]] || { echo "--out, --bg1 and --bg2 are required" >&2; exit 1; }
[[ -n "$FONT" ]] || FONT="$(fc-match -f '%{file}' 'DejaVu Sans:bold' 2>/dev/null || true)"

W="${SIZE%x*}"; H="${SIZE#*x}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

px() { awk -v a="$1" -v b="$2" 'BEGIN{printf "%d", (a*b)/100}'; }

DW=$(px "$W" "$DEVICE_WIDTH_PCT")
DTOP=$(px "$H" "$DEVICE_TOP_PCT")
CTOP=$(px "$H" "$CAPTION_TOP_PCT")
BEZEL=$(( W / 150 )); (( BEZEL < 4 )) && BEZEL=4
RADIUS=$(( DW * 7 / 100 ))
SCREEN_W=$(( DW - 2*BEZEL ))

# How tall the screen may be. Without --bleed the whole device must fit above the bottom margin.
BOTTOM_MARGIN=$(px "$H" 4)
if [[ "$BLEED" == "1" ]]; then
  MAX_SCREEN_H=$(( H - DTOP ))            # runs off the canvas, gets cropped
else
  MAX_SCREEN_H=$(( H - DTOP - BOTTOM_MARGIN - 2*BEZEL ))
fi

# Fit the raw screenshot to the device screen. Without --bleed the whole screenshot stays visible
# (it shrinks to fit the height), which matters because the bottom nav bar is usually part of the
# story you are selling. With --bleed the shot fills the width and the overflow is cropped away.
if [[ "$BLEED" == "1" ]]; then
  magick "$SHOT" -resize "${SCREEN_W}x" -gravity north -crop "${SCREEN_W}x${MAX_SCREEN_H}+0+0" +repage "$TMP/screen.png"
else
  magick "$SHOT" -resize "${SCREEN_W}x${MAX_SCREEN_H}" "$TMP/screen.png"
fi
SCREEN_W=$(magick identify -format '%w' "$TMP/screen.png")
SCREEN_H=$(magick identify -format '%h' "$TMP/screen.png")

# Round the screen corners so it sits flush inside the bezel.
IR=$(( RADIUS - BEZEL )); (( IR < 2 )) && IR=2
magick -size "${SCREEN_W}x${SCREEN_H}" xc:black \
  -fill white -draw "roundrectangle 0,0,$((SCREEN_W-1)),$((SCREEN_H-1)),$IR,$IR" \
  -alpha off "$TMP/mask.png"
magick "$TMP/screen.png" "$TMP/mask.png" -alpha off -compose CopyOpacity -composite "$TMP/screen_r.png"

# Bezel: a rounded plate of frame colour with the screen inset on top.
PW=$(( SCREEN_W + 2*BEZEL )); PH=$(( SCREEN_H + 2*BEZEL ))
magick -size "${PW}x${PH}" xc:none \
  -fill "$FRAME" -draw "roundrectangle 0,0,$((PW-1)),$((PH-1)),$RADIUS,$RADIUS" \
  "$TMP/screen_r.png" -geometry "+${BEZEL}+${BEZEL}" -compose over -composite "$TMP/device.png"

# Drop shadow, so the device reads as a physical object on the gradient.
magick "$TMP/device.png" \
  \( +clone -background black -shadow "55x$(( W/45 ))+0+$(( H/120 ))" \) \
  +swap -background none -layers merge +repage "$TMP/device_s.png"

# Background gradient in the app's own colours.
if [[ "$RADIAL" == "1" ]]; then
  # Like an app icon lit from the top left: --bg1 glows there, fading to --bg2 at the far edges.
  R=$(( (W > H ? W : H) * 2 ))
  magick -size "${R}x${R}" "radial-gradient:${BG1}-${BG2}" \
    -crop "${W}x${H}+$(( R/2 - W*30/100 ))+$(( R/2 - H*18/100 ))" +repage "$TMP/bg.png"
else
  magick -size "${W}x${H}" "gradient:${BG1}-${BG2}" "$TMP/bg.png"
fi

DEV_W=$(magick identify -format '%w' "$TMP/device_s.png")
DEV_X=$(( (W - DEV_W) / 2 ))
SHADOW_PAD=$(( (DEV_W - PW) / 2 ))
DEV_Y=$(( DTOP - SHADOW_PAD )); (( DEV_Y < 0 )) && DEV_Y=0

magick "$TMP/bg.png" "$TMP/device_s.png" -geometry "+${DEV_X}+${DEV_Y}" -composite "$TMP/stage.png"

# Callout: a region of the raw screenshot, enlarged and floated above the device where it sits, so
# the one feature that sells the screen stays readable at store-thumbnail size.
if [[ -n "$CALLOUT" ]]; then
  IFS=, read -r CX CY CW CH <<< "$CALLOUT"
  SRC_W=$(magick identify -format '%w' "$SHOT")
  F=$(awk -v s="$SCREEN_W" -v r="$SRC_W" 'BEGIN{print s/r}')
  OUT_W=$(awk -v w="$CW" -v f="$F" -v k="$CALLOUT_SCALE" 'BEGIN{printf "%d", w*f*k}')
  MAXW=$(px "$W" 94); (( OUT_W > MAXW )) && OUT_W=$MAXW
  magick "$SHOT" -crop "${CW}x${CH}+${CX}+${CY}" +repage -resize "${OUT_W}x" "$TMP/co.png"
  COW=$(magick identify -format '%w' "$TMP/co.png"); COH=$(magick identify -format '%h' "$TMP/co.png")
  CR=$(( COW * 5 / 100 ))
  magick -size "${COW}x${COH}" xc:black -fill white -draw "roundrectangle 0,0,$((COW-1)),$((COH-1)),$CR,$CR" -alpha off "$TMP/com.png"
  magick "$TMP/co.png" "$TMP/com.png" -alpha off -compose CopyOpacity -composite "$TMP/co_r.png"
  magick "$TMP/co_r.png" \( +clone -background black -shadow "60x$(( W/40 ))+0+$(( H/100 ))" \) \
    +swap -background none -layers merge +repage "$TMP/co_s.png"
  COSW=$(magick identify -format '%w' "$TMP/co_s.png"); PAD=$(( (COSW - COW) / 2 ))
  # Centre of the region on the canvas, then keep the enlarged card inside the side margins.
  MID_X=$(awk -v d="$DEV_X" -v p="$SHADOW_PAD" -v b="$BEZEL" -v x="$CX" -v w="$CW" -v f="$F" 'BEGIN{printf "%d", d+p+b+(x+w/2)*f}')
  MID_Y=$(awk -v d="$DTOP" -v b="$BEZEL" -v y="$CY" -v h="$CH" -v f="$F" 'BEGIN{printf "%d", d+b+(y+h/2)*f}')
  X=$(( MID_X - COW/2 )); M=$(px "$W" 3)
  (( X < M )) && X=$M; (( X + COW > W - M )) && X=$(( W - M - COW ))
  # The enlarged card covers more than its region. Anchor it where the region has a clean gap so it
  # never slices through the neighbouring text: top grows downward, bottom grows upward.
  HALF=$(awk -v h="$CH" -v f="$F" 'BEGIN{printf "%d", h*f/2}')
  case "$CALLOUT_ANCHOR" in
    top) Y=$(( MID_Y - HALF ));;
    bottom) Y=$(( MID_Y + HALF - COH ));;
    *) Y=$(( MID_Y - COH/2 ));;
  esac
  magick "$TMP/stage.png" "$TMP/co_s.png" -geometry "+$(( X - PAD ))+$(( Y - PAD ))" -composite "$TMP/stage.png"
fi

# Caption: wrapped to the safe width, centred in the band above the device.
if [[ -n "$CAPTION" ]]; then
  CAP_W=$(px "$W" 92)
  PT=$(px "$W" "$CAPTION_SIZE_PCT")
  CAP_TEXT="${CAPTION//\\n/$'\n'}"
  FONT_ARG=(); [[ -f "$FONT" ]] && FONT_ARG=(-font "$FONT")
  render_caption() {
    magick -background none -fill "$FG" "${FONT_ARG[@]}" -pointsize "$1" \
      -size "${CAP_W}x" -interline-spacing "$(( $1 / 5 ))" -gravity center \
      caption:"$CAP_TEXT" "$TMP/cap.png"
  }
  BAND_H=$(( DTOP - CTOP ))
  render_caption "$PT"
  CAP_H=$(magick identify -format '%h' "$TMP/cap.png")
  # A long caption must never grow into the device. Shrink the type until it fits the band rather
  # than letting the two collide - a caption that overlaps the phone reads as a rendering bug.
  LIMIT=$(( BAND_H * 92 / 100 ))
  for _ in 1 2 3; do
    (( CAP_H <= LIMIT )) && break
    PT=$(( PT * LIMIT / CAP_H ))
    (( PT < 16 )) && PT=16
    render_caption "$PT"
    CAP_H=$(magick identify -format '%h' "$TMP/cap.png")
  done
  CAP_Y=$(( CTOP + (BAND_H - CAP_H) / 2 )); (( CAP_Y < CTOP/2 )) && CAP_Y=$(( CTOP/2 ))
  CAP_X=$(( (W - CAP_W) / 2 ))
  magick "$TMP/stage.png" "$TMP/cap.png" -geometry "+${CAP_X}+${CAP_Y}" -composite "$TMP/stage.png"
fi

mkdir -p "$(dirname "$OUT")"
magick "$TMP/stage.png" -alpha remove -alpha off -strip "$OUT"
echo "$OUT ($(magick identify -format '%wx%h' "$OUT"))"
