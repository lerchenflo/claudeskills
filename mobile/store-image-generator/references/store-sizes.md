# Accepted store canvas sizes

App Store Connect validates uploads against an exact pixel list. A 1206x2623 image is rejected the
same as a 500x500 one, and you only find out at submission time - so resolve the target size before
rendering, never after. `scripts/nearest_size.py WxH --store ios` does this from a source screenshot.

## App Store (iOS) - portrait px, swap for landscape

Sizes as App Store Connect lists them (checked 2026-10). Each slot gets its own output folder:
`storeassets/ios/<folder>/<locale>/`.

| Slot | Folder | Screenshot sizes (portrait / landscape) | Notes |
|---|---|---|---|
| iPhone | `iphone` | **1206x2622** / 2622x1206, 1179x2556 / 2556x1179 | Required. |
| iPhone Duo | `iphone-duo` | **2007x2853** / 2853x2007, 1398x2034 / 2034x1398 | Foldable/dual-screen slot. Wide aspect (0.70): the phone frame sits on a wider background. |
| iPad | `ipad` | **2064x2752** / 2752x2064, 2048x2732 / 2732x2048 | Required *only* if the app ships an iPad build. |

App previews (video) are a separate upload: 886x1920 / 1920x886 (iPhone and Duo), 1200x1600 /
1600x1200 (iPad).

Other App Store rules worth knowing before you render:
- 3 to 10 screenshots per slot, per localisation. Fewer than 3 looks sparse on the product page.
- The **first two** are what people see without swiping - put the strongest features there.
- RGB, flattened, no alpha channel. `compose_shot.sh` strips alpha for this reason.
- Localised sets are independent: a German listing can have different shots than an English one.

## Play Store (Android)

Not a fixed list, but a range: 16:9 to 2:1 aspect, each side 320-3840px. 1080x1920 and 1080x2400 are
safe. Also needs the 512x512 icon and the 1024x500 feature graphic (table below).

## Icons and feature graphic

| Asset | Size | Rules | Script |
|---|---|---|---|
| App Store icon | 1024x1024 | PNG, RGB, **no alpha**, square (Apple rounds the corners) | `make_icons.sh` |
| Play icon | 512x512 | 32-bit PNG, max 1 MB, full square (Play applies the mask) | `make_icons.sh` |
| Play feature graphic | 1024x500 | JPEG or 24-bit PNG, **no alpha**; shown at the top of the listing and cropped/overlaid on some surfaces - keep text and icon away from the outer ~10% | `feature_graphic.sh` |

## Aspect mismatch

Android phone screenshots (commonly 1080x2400, aspect 0.45) do not match 1206x2622 (0.46). The gap is
small but stretching to close it distorts text and rounded corners in a way reviewers notice. The
device-frame layout sidesteps this entirely: the screenshot keeps its own aspect inside the frame and
the background absorbs the difference. Only worry when drift exceeds ~4%.
