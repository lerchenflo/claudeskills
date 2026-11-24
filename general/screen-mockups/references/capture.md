# Capturing the current screen

Prefer an emulator or simulator with demo or test data. A physical device, a real account or a
logged-in browser can show private data: ask the user before you capture from one.

## Android (emulator or device)

```bash
ADB=$(command -v adb || echo ~/Library/Android/sdk/platform-tools/adb)   # Linux: ~/Android/Sdk/...
$ADB devices                       # pick the serial; with two devices pass -s every time
~/Library/Android/sdk/emulator/emulator -list-avds                       # start one if none runs:
~/Library/Android/sdk/emulator/emulator -avd <name> -no-snapshot-save -no-boot-anim &   # run in background
$ADB -s emulator-5554 shell getprop sys.boot_completed                   # "1" once booted
$ADB -s <serial> shell monkey -p <package> -c android.intent.category.LAUNCHER 1   # launch the app
$ADB -s <serial> shell wm size                                           # screen size in px
$ADB -s <serial> exec-out screencap -p > now.png
```

Navigating: `adb shell input tap X Y` (screen pixels; a downscaled screenshot needs the scale
factor), `adb shell input swipe X1 Y1 X2 Y2 300`, `adb shell input keyevent 4` (back). To tap by
text, dump the view tree with `adb shell uiautomator dump /sdcard/ui.xml` and read the `bounds` of
the node with that text. Close onboarding tours, permission dialogs and snackbars before the shot,
and wait a moment after loading so no blur or spinner is captured.

If the app needs an install or build first, ask: building is the user's call in many projects.

## iOS simulator (macOS)

```bash
xcrun simctl list devices booted
xcrun simctl boot "<device name>" && open -a Simulator      # if none is booted
xcrun simctl launch booted <bundle id>
xcrun simctl openurl booted "<deep link>"                   # jump to a screen if the app has links
xcrun simctl io booted screenshot now.png
```

The simulator has no tap command. Use a deep link, or ask the user to open the screen and say
when it's there.

## Desktop app

- macOS: `screencapture -x -o -l <window id> now.png` for one window. Get the id with
  `osascript -e 'tell app "System Events" to get id of window 1 of process "<App>"'` or use
  `screencapture -x -R x,y,w,h now.png` for a screen region.
- Linux: `import -window "$(xdotool search --name '<title>' | head -1)" now.png` (ImageMagick) or
  `gnome-screenshot -w -f now.png`.
- Windows: ask the user for a screenshot (Win+Shift+S) unless a capture tool is set up.

## Web page

```bash
"<chrome binary>" --headless=new --hide-scrollbars --window-size=390,844 --screenshot=now.png "<url>"
```

Chrome: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (macOS),
`google-chrome` or `chromium` (Linux). Playwright works too
(`npx playwright screenshot --viewport-size=390,844 <url> now.png`). Pages behind a login: ask the
user for a screenshot instead of logging in.

## Preparing images (Pillow)

```python
from PIL import Image, ImageDraw
im = Image.open("now.png").convert("RGB")
w = 400                                                     # frame width in CSS px
im.resize((w, round(im.height * w / im.width))).save("mockup/now.png")
# circular crop around center (cx, cy) with radius r, in screenshot pixels
crop = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((240, 240))
mask = Image.new("L", (240, 240), 0); ImageDraw.Draw(mask).ellipse((0, 0, 239, 239), fill=255)
out = Image.new("RGBA", (240, 240)); out.paste(crop, (0, 0), mask); out.save("mockup/avatar.png")
```

Render the finished page to check it (headless Chrome): `--window-size=2400,1000
--screenshot=check.png file:///abs/path/mockups.html`, then look at `check.png`.
