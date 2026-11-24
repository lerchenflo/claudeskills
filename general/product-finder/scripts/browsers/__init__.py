"""Browser backends. Each backend drives the user's real browser and exposes the same small API:

    win = b.new_window(url)            -> window handle (opens a NEW window, never touches the user's tabs)
    b.open_tab(win, url)               -> opens url as an extra tab in that window
    b.navigate(win, index, url)        -> loads url in tab <index> (1-based)
    b.tab_count(win)                   -> int
    b.ready_state(win, index)          -> "loading" | "interactive" | "complete" | "" on error
    b.run_js(win, index, js)           -> str (the value of the last JS expression, as a string)
    b.close_window(win)

To add a browser (e.g. Chrome), add a module with a class implementing these methods and register it below.
Chrome via AppleScript: `execute active tab javascript` / `execute tab i of window id W javascript`, needs
View > Developer > "Allow JavaScript from Apple Events".
"""
from __future__ import annotations


def get_browser(name: str):
    name = (name or "safari").lower()
    if name == "safari":
        from .safari import Safari
        return Safari()
    raise SystemExit(f"Browser '{name}' is not supported yet. Supported: safari")
