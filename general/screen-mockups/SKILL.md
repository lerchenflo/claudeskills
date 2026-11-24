---
name: screen-mockups
description: Builds side-by-side HTML mockups of an existing app or web screen - the current screen first (a screenshot the user gives, or one the agent captures itself from an Android emulator or device, an iOS simulator, a desktop window or a web page), then 3-4 clearly different redesign variants that follow the platform's design system (Material 3, Apple HIG, Windows/macOS desktop, web) and the app's own theme, all in ONE horizontal row that never wraps, opened in the browser. Use it whenever the user asks for mockups, design variants, redesign ideas, UI alternatives, "how could this screen look", "make this prettier, show me options", or a before/after comparison of a screen or part of a screen - on any platform, even if they never say "mockup".
---

# Screen mockups

Show the user how a screen looks today and how it could look, so they can pick a direction before
any real code changes. The output is one self-contained HTML file opened in the browser: the
current screen on the left, then 3-4 variants next to it, all in a single row.

## The output contract (never bend these)

1. **One row, no wrapping.** The current screen is the first item, then 3 or 4 variants. The row
   is `display: flex; flex-wrap: nowrap; overflow-x: auto`, so a narrow window scrolls sideways
   and never breaks into a second line. No second row, no grid, no extra row for empty or error
   states. If another state matters (empty, error, dark mode), add a toggle at the top that
   switches every frame at once, so it stays one row. Build a second file only if the user asks.
2. **Current screen first.** It is the real screenshot, unedited, in the same frame size as the
   variants, labeled "Now".
3. **Variants that really differ.** Each variant is a different idea: a different structure,
   hierarchy or visual metaphor, not the same layout with other colors or spacing. Before
   building, name each idea in 2-4 words (e.g. "card with edit button", "sticky note", "pair of
   cards", "inline section"). If two names describe the same layout, replace one.
4. **Platform-conform.** Build the variants from the target platform's own components and rules
   (see "Platform cheat sheet"). At most one variant may break a convention on purpose; its
   caption says so.
5. **The app's own look.** Take colors, shapes, fonts and spacing from the project's theme
   (theme files, design tokens, CSS variables), not an invented palette, so every variant could
   ship next to the rest of the app. Use the app's language for UI texts, as in the screenshot.
6. **Real content.** Use the texts, names, numbers and images from the screenshot (crop avatars,
   maps or photos out of it), never lorem ipsum. Don't mock up data the app doesn't have without
   saying so in the caption (e.g. "who wrote it isn't stored").
7. **Same frame for all.** Every item has the device's aspect ratio and the same width, and shows
   the same part of the screen as the screenshot. A caption above each frame: the letter and name
   of the idea, plus 1-2 lines on why it helps.
8. **Stays local.** Screenshots can show private data. Keep the files local (session scratchpad,
   or the project folder if asked), open them with the system browser, and never upload or
   publish them unless the user asks.

## Steps

1. **Scope.** Which screen and which part of it should change, and what bothers the user about it
   today (e.g. "too big", "nobody finds the edit button"). Read the request closely. Only ask what
   changes the result, and ask all of it at once.
2. **Get the current screen.**
   - The user gave a screenshot: use it.
   - Otherwise capture it yourself: see `references/capture.md` (Android, iOS, desktop, web).
   - A half-empty screen is a weak template. Look for demo or seed data in the project (store
     screenshot scripts, fixtures, test accounts) and fill every field the redesign touches
     before you capture. If none exists, ask the user how to get a filled screen.
3. **Read the real UI.** Theme colors and typography, and the code of the screen: which fields
   exist, which are optional, who may edit what. Variants must stay true to what the app can do.
4. **Prepare assets** in one folder: the screenshot (scaled to the frame width), crops of images
   the variants reuse (Python Pillow, e.g. circular avatar crops), nothing else.
5. **Build the HTML** from `assets/template.html`: fill in the theme variables, the frame size,
   the "Now" item and one item per variant. Plain HTML and CSS, no external requests (fonts and
   images local or system), so it opens offline.
6. **Check it.** If a headless Chrome or Chromium is available, render the page to a PNG and look
   at it: one row, frames the same size, nothing cut off or overflowing, variants visibly
   different. Fix and render again. Without a headless browser, read the HTML once more against
   the contract above.
7. **Open it** in the browser (`open` on macOS, `xdg-open` on Linux, `start` on Windows). Reply
   with the file path and one line per variant, then let the user pick (through the question tool
   if the session has one).
8. **Build the pick** only when the user asks, in the real code, following the project's rules.
   Afterwards delete temporary captures that aren't part of the mockup folder.

## Platform cheat sheet

- **Android / Jetpack Compose / Compose Multiplatform (Material 3):** top app bar with back arrow
  and overflow ⋮, cards (filled or outlined, 12-16 dp corners), tonal and text buttons, assist and
  filter chips, list items with leading icon, 48 dp touch targets, 16 dp side margins, color roles
  (primary, secondary, tertiary, surface containers), Roboto-like type scale.
- **iOS (Apple HIG):** large or inline navigation title, inset grouped lists, SF-style symbols,
  44 pt touch targets, text buttons in the tint color, sheets and context menus instead of
  overflow menus, system fonts with Dynamic Type sizes.
- **Desktop (Windows / macOS / Compose Desktop):** denser layouts, hover states, toolbars and
  side panels instead of bottom sheets, keyboard-reachable actions, wider frames (scale the frame
  with CSS so the whole row still fits sideways).
- **Web:** the site's own components and grid, responsive widths (show the width the user cares
  about), visible focus states, links that look like links.

Frame sizes: phones at their dp/pt width (about 360-430 CSS px). Tablets, desktop windows and web
pages at a scaled-down width (about 560-720 CSS px) so 4-5 items stay in one scrollable row.
