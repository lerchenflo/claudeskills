---
name: store-image-generator
description: Produce finished app-store listing images - capture real screens off a running Android emulator or device, frame them on a brand-coloured background, overlay a marketing caption, and export at exactly the pixel sizes App Store Connect accepts; also exports the 1024x1024 / 512x512 store app icons and the 1024x500 Play Store feature graphic (Vorstellungsgrafik). Use this whenever the user mentions app store screenshots, store listing images, App Store Connect assets, Play Store graphics, store app icon, feature graphic, Vorstellungsgrafik, marketing screenshots, promo images for an app, screenshots with captions or text overlays, or says something like "I need images for the store", "make screenshots for the listing", or "my app store screenshots are outdated" - even if they don't name a pixel size or a store. Also use it when they want a single screenshot dressed up for a website, changelog, or release post.
---

# Store image generator

Turn live app screens into a store-ready set: caption on top, the app framed as a phone below, the
app's own colours behind it, exported at an accepted store size.

The output is a marketing asset, not a debug screenshot. Two things follow from that. First, every
colour and font comes from the app being shot - an invented palette makes the images look like a
different product sitting next to the real icon. Second, the pixel size is not negotiable: App Store
Connect rejects anything off its list, and it tells you at submission time, after the whole set is
built.

## What you need

- ImageMagick 7 (`magick`) - the compositor is built on it.
- `adb` plus a booted emulator or a plugged-in device, for the capture step.
- Python 3, for the size picker.

Check `magick -version` and `adb devices` up front. If nothing is attached, say so and stop there -
the rest of the workflow has nothing to work with.

## Two variants

- **A - emulator capture** (this file): live screens off a device, composited with ImageMagick.
  Works for any app and real data.
- **B - Compose previews** (`references/preview-variant.md`): the store images are screenshot tests
  rendered on the JVM (Roborazzi). No emulator; one Gradle task refreshes every image after a UI
  change. Offer B when the app is Compose with stateless screens and the set will be updated often.

Ask which one the user wants before step 1 if both fit.

## Workflow

### 1. Find the app's palette and font

Read `references/brand-colors.md` and follow it. You are looking for four things: a dark brand
colour (`--bg1`), a lighter one in the same hue (`--bg2`), a caption colour that reads on both
(`--fg`), and a bundled font. Show the user what you found as hex values with their theme role
("primary #006E2C, primaryContainer #1ED660") so a wrong guess gets caught before 8 images are
rendered. If the project has no discoverable theme, ask - do not pick something that merely looks
nice.

### 2. Agree on the screen list

Find the app's top-level destinations yourself first: a nav graph, route sealed interface, bottom
nav item list, tab bar, or router config. Then ask the user which of those to shoot, as a
multi-select with the destinations you found as the options, plus room for screens you missed.

Ask for the locale in the same breath if the app is localised - a German listing wants German
screenshots, and the device locale has to be switched before any capture, not after.

Aim for 3-6 screens. Apple allows up to 10 per slot but the first two carry the product page, so
push the strongest feature to position one.

### 3. Hand the device to the user

Sample data is the difference between a screenshot that sells and one that shows an empty state, and
only the user knows what realistic data looks like in their app. Ask them to get the device ready:
signed in, the right locale, chats/pins/entries populated, nothing personal or embarrassing on
screen. Wait for their confirmation before capturing anything.

### 4. Capture, one screen at a time

For each agreed screen, navigate there (or ask the user to), then **before capturing** ask the user
whether they like what the emulator shows right now: is there enough content, nothing empty, the
right scroll position, the right item opened? Use AskUserQuestion ("Passt der Screen so?" - capture /
let me adjust first / scroll or open something else). An empty list or a half-filled board sells
nothing, and only the user can see the emulator and judge it. Capture only after a yes:

```bash
scripts/capture_screen.sh --out shots/01-chats.png --delay 1
```

Demo mode is on by default: it pins the clock to 09:41, fills the battery and signal, and hides
notification icons. That is what makes a screenshot look deliberate rather than grabbed off someone's
phone mid-afternoon at 14% battery.

Look at every capture with the Read tool before moving on. Wrong screen, a half-finished animation,
a keyboard covering the content, a debug banner, real names or addresses - all cheap to fix now and
expensive after compositing. Re-capture rather than proceeding with a flawed shot.

When all screens are captured, restore the status bar:

```bash
scripts/capture_screen.sh --demo-off
```

### 5. Write captions with the user

Captions are the part the user cares most about and the part you know least about, so draft first and
let them steer. For each screenshot, offer about four variants in the target language, deliberately
different in angle rather than four rewordings of one idea:

- a benefit ("Nie wieder einen Geburtstag vergessen")
- a plain feature statement ("Gruppenchats mit bis zu 50 Leuten")
- something short and punchy, two or three words
- a tone-of-voice line that matches how the app talks to its users

Use AskUserQuestion so they can pick per screenshot, then let them rewrite the chosen line freely -
the draft is a starting point, not a menu. Two short lines beat one long one; the caption is read at
thumbnail size in a store search result. Use `\n` where you want the break rather than trusting the
automatic wrap.

### 6. Resolve the target size

```bash
python3 scripts/nearest_size.py 1080x2424 --store ios
```

This maps the source resolution onto the nearest accepted canvas and reports the aspect drift. The
full table with Apple's rules is in `references/store-sizes.md` - read it for the per-slot folders (`iphone`, `iphone-duo`, `ipad`) and when the user asks about
iPad, landscape, Play Store, or how many images they need.

### 7. Compose

**One image at a time.** Compose the first image, show it to the user (Read the PNG, then
AskUserQuestion: passt / change caption / change callout / other), and only after a yes compose the
next. Never batch the whole set before the first approval - a wrong callout or caption repeated four
times wastes the run. Once all are approved, render the remaining store sizes in one go.

```bash
scripts/compose_shot.sh \
  --shot shots/01-chats.png \
  --out storeassets/ios/iphone/de/01-chats.png \
  --caption 'Privat chatten.\nOhne Tracking.' \
  --bg1 '#006E2C' --bg2 '#1ED660' --fg '#FFFFFF' --frame '#111111' \
  --font path/to/display_bold.ttf \
  --size 1206x2622
```

Write into a dedicated folder in the project root (`storeassets/<store>/<slot>/<locale>/NN-name.png`).
Numbering the files keeps store ordering obvious to whoever uploads them.

Layout knobs, when the default needs adjusting:

| Flag | Default | Use it when |
|---|---|---|
| `--bleed` | off | You want the device to run off the bottom edge - dynamic, but it eats the bottom nav bar |
| `--device-width` | 74 | A dense screen needs more room (78-82) or a sparse one wants more background (68) |
| `--caption-top` / `--device-top` | 7 / 27 | A three-line caption needs the device pushed down |
| `--caption-size` | 6 | Caption height in % of canvas width; 6.5-7 reads better at thumbnail size |
| `--callout X,Y,W,H` | off | Lift the one element that sells the screen (in source-screenshot pixels) out of the device as an enlarged floating card |
| `--callout-scale` | 1.3 | Zoom of the callout; 1.3 for a full-width card, 1.6 for a narrower one |

**Callouts are the default for a sales set.** At store-thumbnail size the UI inside the phone is
unreadable; one enlarged card per image (the task card, the medication block, the invitation banner)
makes the feature legible in the first second. Pick a region that is a whole UI element - a card,
a banner, a header row - never a slice through one, and keep it free of half-cut neighbours. Find
coordinates with `adb shell uiautomator dump` bounds or by measuring a downscaled preview.
Find exact element edges by probing pixel rows (`magick shot.png -crop 1000x1+40+$y +repage -format
'%[fx:standard_deviation>0.01?1:0]' info:` over a y range: 0 = blank gap, 1 = content); start the
region inside a blank gap so the enlarged card never slices neighbouring text. When the card would
grow into text above or below, use `--callout-anchor top|bottom`. For an icon-like backdrop (glow top
left, dark edges) use `--radial` with colours sampled from the app icon. One callout per image; two
compete. Proven look (Hufly, 2026-10): `--device-width 76
--caption-size 6.6 --callout-scale 1.3-1.6`, ExtraBold caption, theme `primary` → `primaryContainer`.

Without `--bleed` the whole screenshot stays visible, shrinking to fit. That is the right default
when the bottom nav bar is part of what you are selling.

### 8. Review as a set

The images ship as a row in a store listing, so judge them as a row, not one at a time:

```bash
magick storeassets/ios/iphone/de/*.png -resize x600 +append /tmp/contact-sheet.png
```

Read that sheet and check what only shows up in aggregate: captions drifting in length, one image's
background clashing, the strongest feature buried in position four, the same word opening three
captions. Show it to the user and offer the sheet path so they can look themselves.

### 9. App icons and Play feature graphic

Both stores want more than screenshots. Generate these from the same palette and font:

```bash
# 1024x1024 (App Store) + 512x512 (Play), RGB without alpha
scripts/make_icons.sh --src path/to/app_icon_fullbleed.png --out-dir storeassets/icon
# 1024x500 Play feature graphic, shown on top of the Play listing
scripts/feature_graphic.sh --layout hero --out storeassets/play/feature-graphic/<locale>/hero.png \
  --bg1 '#3A6284' --bg2 '#1A3144' --radial --font path/to/ExtraBold.ttf \
  --icon storeassets/icon/appstore-1024.png --name 'Hufly' --tagline 'Der ganze Stall in einer App.' \
  --shot shots/01-heute.png
```

- Icon master: the **full-bleed square** source (iOS `AppIcon.appiconset`, a `*_fullbleed.png`, or the
  adaptive icon's foreground over its background) - never a pre-rounded or padded launcher PNG, the
  stores round the corners themselves. With alpha, pass `--bg` with the icon's own background colour.
- Feature graphic layouts: `hero` (icon, name, tagline left; one phone right), `icon` (centred icon,
  name, tagline), `phones` (tagline over 2-3 fanned phones). Unless the user already picked one,
  render all three and let them choose. Tagline = the listing's promise in ≤ 6 words, same locale as
  the screenshots. Keep it free of "Download now"/rank claims - Play rejects call-to-action text.
- Verify with `magick identify` (exact size, `srgb 3.0` = no alpha) and Read the result.

### 10. Listing text

Write the store texts (subtitle, promotional text, keywords, short description, description) to
`storeassets/listing/<locale>.txt`, following `references/listing-text.md`. Draft from the features
the images show, let the user edit, check every field against its character limit before handing
over.

### 11. Hand over

Report the output folder, the canvas size, how many images per locale, and anything still owed -
iPad shots if the app has an iPad build, icons or feature graphic not yet chosen, other locales.
Mention that the status bar demo mode was switched off.

## Adapting

The scripts take flags, not a fixed recipe. A caption below the device is `--caption-top` and
`--device-top` moved around; a dark-theme variant of the set is the dark half of the app's palette
and a re-run. When the user wants a layout the flags cannot express, compose it with `magick`
directly rather than forcing the script - `compose_shot.sh` is readable and worth borrowing from.

One thing not to adapt: the exported pixel size. Everything else is taste.
