# Pulling the palette out of the app being shot

Store images sit next to the app icon on the product page, so an invented gradient reads as a
different product. Every colour in the output must come from the app's own theme. Find it, don't
guess it - and if the search comes up empty, ask the user rather than picking something plausible.

## Where the palette lives, by project type

| Project | Look here | What you want |
|---|---|---|
| Compose / KMP | `**/theme/Color.kt`, `**/ui/theme/Color.kt` | `Color(0xFF006E2C)` literals named `primary*`, `background*`, `surface*`, `onPrimary*` |
| Android XML | `res/values/colors.xml`, `themes.xml` | `colorPrimary`, `colorPrimaryContainer`, `colorSurface` |
| iOS / SwiftUI | `Assets.xcassets/*.colorset/Contents.json` | `components` → red/green/blue, often 0-1 floats or hex strings |
| Flutter | `lib/**/theme*.dart` | `ColorScheme.fromSeed(seedColor: Color(0xFF...))`, `primary:` |
| React Native / web | `tailwind.config.*`, `:root { --color-* }`, `theme.ts` | brand / primary tokens |

Material 3 projects usually carry light **and** dark sets (`primaryLight` / `primaryDark`). Both are
usable - a dark-background set makes a striking contrast shot in the middle of a light-background
series, and the choice is the user's to make.

## Mapping theme roles to the composite

| Script flag | Take it from | Why |
|---|---|---|
| `--bg1` | `primary` (the darker end) | Top of the gradient, behind the caption |
| `--bg2` | `primaryContainer` or `inversePrimary` (lighter, same hue) | Bottom of the gradient |
| `--fg` | `onPrimary` | Guaranteed readable on `primary` by construction of the theme |
| `--frame` | `tertiary`, `scrim`, or near-black | Device bezel; a real phone bezel is dark, so dark almost always wins |

Two things that break this mapping:

- **`bg1` and `bg2` are nearly the same colour.** The gradient disappears and the image looks flat.
  Reach for `secondary`/`secondaryContainer`, or use `surfaceDim` → `surfaceBright` for a quiet
  neutral backdrop, which is a legitimate look for a privacy- or productivity-focused app.
- **Both gradient ends are light.** `onPrimary` is then usually white and the caption vanishes. Use
  `onBackground` or `onSurface` for `--fg` instead.

Check rather than assume. This prints the luminance of a colour - under ~0.5 is a dark colour that
wants light text:

```bash
magick -size 1x1 xc:'#006E2C' -colorspace gray -format '%[fx:u]' info:
```

## Fonts

The app's own display font makes the caption feel like part of the product. Look for
`composeResources/font/*.ttf`, `res/font/`, `assets/fonts/`, or a bundled `.otf`, and prefer a Bold
or SemiBold face. Pass it with `--font`. Without one the script falls back to DejaVu Sans Bold,
which is serviceable but generic - worth mentioning to the user.
