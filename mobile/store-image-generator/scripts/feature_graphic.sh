#!/usr/bin/env bash
# Play Store feature graphic (1024x500, 24-bit PNG, no alpha) in one of three layouts.
# Requires ImageMagick 7 (`magick`).
set -euo pipefail

LAYOUT="hero"; OUT=""; ICON=""; NAME=""; TAGLINE=""; SHOTS=()
BG1=""; BG2=""; FG="#FFFFFF"; FRAME="#111111"; FONT=""; RADIAL=0
W=1024; H=500

usage() {
  cat <<'USAGE'
feature_graphic.sh --layout hero|icon|phones --out OUT.png --bg1 '#3A6284' --bg2 '#1A3144' \
                   [--icon icon.png] [--name "Hufly"] [--tagline "Der ganze Stall in einer App"] \
                   [--shot a.png [--shot b.png ...]] [--fg '#FFFFFF'] [--frame '#111111'] \
                   [--font Bold.ttf] [--radial]

hero    icon + name + tagline on the left, one framed phone (first --shot) on the right, cut by the bottom edge
icon    icon, name and tagline centred - no screenshot
phones  tagline on top, 2-3 framed phones (--shot each) fanned along the bottom edge

Every colour comes from the app's own theme or icon - never invent one.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --layout) LAYOUT="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --icon) ICON="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --tagline) TAGLINE="$2"; shift 2;;
    --shot) SHOTS+=("$2"); shift 2;;
    --bg1) BG1="$2"; shift 2;;
    --bg2) BG2="$2"; shift 2;;
    --fg) FG="$2"; shift 2;;
    --frame) FRAME="$2"; shift 2;;
    --font) FONT="$2"; shift 2;;
    --radial) RADIAL=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "unknown arg: $1" >&2; usage; exit 1;;
  esac
done

[[ -n "$OUT" && -n "$BG1" && -n "$BG2" ]] || { echo "--out, --bg1 and --bg2 are required" >&2; exit 1; }
case "$LAYOUT" in
  hero) [[ -f "$ICON" && ${#SHOTS[@]} -ge 1 ]] || { echo "hero needs --icon and one --shot" >&2; exit 1; };;
  icon) [[ -f "$ICON" ]] || { echo "icon needs --icon" >&2; exit 1; };;
  phones) [[ ${#SHOTS[@]} -ge 2 ]] || { echo "phones needs 2-3 --shot" >&2; exit 1; };;
  *) echo "unknown layout: $LAYOUT" >&2; exit 1;;
esac
[[ -n "$FONT" ]] || FONT="$(fc-match -f '%{file}' 'DejaVu Sans:bold' 2>/dev/null || true)"
FONT_ARG=(); [[ -f "$FONT" ]] && FONT_ARG=(-font "$FONT")
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# Background in the app's colours (radial = lit from the top left like an icon).
if [[ "$RADIAL" == "1" ]]; then
  magick -size 2048x2048 "radial-gradient:${BG1}-${BG2}" -crop "${W}x${H}+$(( 1024 - W*25/100 ))+$(( 1024 - H*30/100 ))" +repage "$TMP/stage.png"
else
  magick -size "${W}x${H}" "gradient:${BG1}-${BG2}" -rotate -90 -resize "${W}x${H}!" "$TMP/stage.png"
fi

# Rounded icon with a soft shadow, $1 px wide -> $TMP/icon_s.png
icon_tile() {
  local s=$1 r=$(( $1 * 22 / 100 ))
  magick "$ICON" -resize "${s}x${s}" \( -size "${s}x${s}" xc:black -fill white -draw "roundrectangle 0,0,$((s-1)),$((s-1)),$r,$r" \) \
    -alpha off -compose CopyOpacity -composite "$TMP/icon_r.png"
  magick "$TMP/icon_r.png" \( +clone -background black -shadow "50x12+0+6" \) +swap -background none -layers merge +repage "$TMP/icon_s.png"
}

# Framed phone, screen $2 px wide, from shot $1 -> $3 (with shadow). Rotated by $4 degrees.
# Built at 4x and scaled down once at the end: rotating (or shrinking twice) at the final size
# turns the UI text into jagged, pixelated mush.
phone() {
  local shot=$1 out=$3 rot=${4:-0}
  local ss=4 sw=$(( $2 * 4 ))
  local bz=$(( sw / 28 + 3 )) rad=$(( sw * 12 / 100 ))
  magick "$shot" -filter Lanczos -resize "${sw}x" "$TMP/p_screen.png"
  local sh; sh=$(magick identify -format '%h' "$TMP/p_screen.png")
  local ir=$(( rad - bz ))
  magick "$TMP/p_screen.png" \( -size "${sw}x${sh}" xc:black -fill white -draw "roundrectangle 0,0,$((sw-1)),$((sh-1)),$ir,$ir" \) \
    -alpha off -compose CopyOpacity -composite "$TMP/p_screen_r.png"
  local pw=$(( sw + 2*bz )) ph=$(( sh + 2*bz ))
  magick -size "${pw}x${ph}" xc:none -fill "$FRAME" -draw "roundrectangle 0,0,$((pw-1)),$((ph-1)),$rad,$rad" \
    "$TMP/p_screen_r.png" -geometry "+${bz}+${bz}" -compose over -composite \
    -background none -virtual-pixel none +distort SRT "$rot" +repage \
    -filter Lanczos -resize "$(( 100 / ss ))%" -unsharp 0x0.6+0.6+0 \
    \( +clone -background black -shadow "55x14+0+8" \) +swap -background none -layers merge +repage "$out"
}

# Text block (name big, tagline below), max width $1, gravity $2 -> $TMP/text.png
text_block() {
  local maxw=$1 grav=$2
  local parts=(); rm -f "$TMP/t_name.png" "$TMP/t_tag.png"
  if [[ -n "$NAME" ]]; then
    magick -background none -fill "$FG" "${FONT_ARG[@]}" -pointsize 74 -size "${maxw}x" -gravity "$grav" caption:"$NAME" "$TMP/t_name.png"
    parts+=("$TMP/t_name.png")
  fi
  if [[ -n "$TAGLINE" ]]; then
    magick -background none -fill "$FG" "${FONT_ARG[@]}" -pointsize 36 -size "${maxw}x" -interline-spacing 6 -gravity "$grav" \
      caption:"${TAGLINE//\\n/$'\n'}" "$TMP/t_tag.png"
    parts+=("$TMP/t_tag.png")
  fi
  # Gap above the tagline: splice with north gravity, centre gravity would cut through the glyphs
  [[ -f "$TMP/t_tag.png" && -n "$NAME" ]] && magick "$TMP/t_tag.png" -background none -gravity north -splice 0x14 "$TMP/t_tag.png"
  magick -background none "${parts[@]}" -gravity "$grav" -append +repage "$TMP/text.png"
}

put() { magick "$TMP/stage.png" "$1" -geometry "+$2+$3" -composite "$TMP/stage.png"; }
dim() { magick identify -format "%$1" "$2"; }

case "$LAYOUT" in
  hero)
    # Phone on the right, top at 12%, running off the bottom edge
    phone "${SHOTS[0]}" 300 "$TMP/ph.png" 0
    put "$TMP/ph.png" $(( W - $(dim w "$TMP/ph.png") - 40 )) 50
    icon_tile 150
    text_block 520 west
    TH=$(dim h "$TMP/text.png"); IH=$(dim h "$TMP/icon_s.png")
    BLOCK=$(( IH + 10 + TH )); Y0=$(( (H - BLOCK) / 2 ))
    put "$TMP/icon_s.png" 50 "$Y0"
    put "$TMP/text.png" 64 $(( Y0 + IH + 10 ))
    ;;
  icon)
    icon_tile 190
    text_block 860 center
    IW=$(dim w "$TMP/icon_s.png"); IH=$(dim h "$TMP/icon_s.png"); TW=$(dim w "$TMP/text.png"); TH=$(dim h "$TMP/text.png")
    BLOCK=$(( IH + TH )); Y0=$(( (H - BLOCK) / 2 ))
    put "$TMP/icon_s.png" $(( (W - IW) / 2 )) "$Y0"
    put "$TMP/text.png" $(( (W - TW) / 2 )) $(( Y0 + IH ))
    ;;
  phones)
    NAME_SAVED="$NAME"; NAME=""   # the tagline carries this layout; the name lives on the icon next to it
    text_block 900 center
    NAME="$NAME_SAVED"
    TW=$(dim w "$TMP/text.png")
    put "$TMP/text.png" $(( (W - TW) / 2 )) 36
    N=${#SHOTS[@]}; (( N > 3 )) && N=3
    if (( N == 3 )); then ROTS=(-8 0 8); XS=(170 512 854); YS=(200 160 200); else ROTS=(-6 6); XS=(360 664); YS=(175 175); fi
    # Side phones first so the middle one sits on top
    ORDER=(); if (( N == 3 )); then ORDER=(0 2 1); else ORDER=(0 1); fi
    for i in "${ORDER[@]}"; do
      phone "${SHOTS[$i]}" 230 "$TMP/ph$i.png" "${ROTS[$i]}"
      put "$TMP/ph$i.png" $(( XS[i] - $(dim w "$TMP/ph$i.png") / 2 )) "${YS[$i]}"
    done
    ;;
esac

mkdir -p "$(dirname "$OUT")"
magick "$TMP/stage.png" -crop "${W}x${H}+0+0" +repage -alpha remove -alpha off -strip "$OUT"
echo "$OUT ($(magick identify -format '%wx%h %[channels]' "$OUT"))"
