"""Safari backend via AppleScript (osascript).

Needs: Safari > Settings > Advanced > "Show features for web developers", then
Develop menu > "Allow JavaScript from Apple Events". The first run may also ask the user to allow
the terminal app to control Safari (System Settings > Privacy & Security > Automation).
"""
from __future__ import annotations

import subprocess

JS_HINT = ("Safari refuses JavaScript from AppleScript. Enable it: Safari > Settings > Advanced > "
           "'Show features for web developers', then Develop menu > 'Allow JavaScript from Apple Events'.")


class BrowserError(RuntimeError):
    pass


def _osa(script: str, *args: str, timeout: float = 60) -> str:
    try:
        p = subprocess.run(["osascript", "-e", script, *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise BrowserError("osascript timed out")
    if p.returncode != 0:
        err = p.stderr.strip()
        if "Allow JavaScript from Apple Events" in err or "-1743" in err or "JavaScript" in err and "turned off" in err:
            raise BrowserError(JS_HINT + " (" + err + ")")
        raise BrowserError(err or f"osascript exit {p.returncode}")
    return p.stdout.rstrip("\n")


class Safari:
    name = "safari"

    def new_window(self, url: str) -> str:
        return _osa('''on run argv
tell application "Safari"
  make new document with properties {URL:(item 1 of argv)}
  return id of front window
end tell
end run''', url)

    def open_tab(self, win: str, url: str) -> None:
        _osa('''on run argv
tell application "Safari"
  tell window id ((item 1 of argv) as integer) to make new tab at end of tabs with properties {URL:(item 2 of argv)}
end tell
end run''', win, url)

    def navigate(self, win: str, index: int, url: str) -> None:
        _osa('''on run argv
tell application "Safari" to set URL of tab ((item 2 of argv) as integer) of window id ((item 1 of argv) as integer) to (item 3 of argv)
end run''', win, str(index), url)

    def tab_count(self, win: str) -> int:
        return int(_osa('''on run argv
tell application "Safari" to return count of tabs of window id ((item 1 of argv) as integer)
end run''', win))

    def run_js(self, win: str, index: int, js: str) -> str:
        return _osa('''on run argv
tell application "Safari" to return do JavaScript (item 3 of argv) in tab ((item 2 of argv) as integer) of window id ((item 1 of argv) as integer)
end run''', win, str(index), js, timeout=90)

    def ready_state(self, win: str, index: int) -> str:
        try:
            return self.run_js(win, index, "document.readyState")
        except BrowserError as e:
            if "Apple Events" in str(e):
                raise
            return ""

    def check_js(self) -> None:
        """Fail early with a clear message if JS from Apple Events is off."""
        win = self.new_window("about:blank")
        try:
            self.run_js(win, 1, "1+1")
        finally:
            self.close_window(win)

    def close_window(self, win: str) -> None:
        try:
            _osa('''on run argv
tell application "Safari" to close window id ((item 1 of argv) as integer)
end run''', win)
        except BrowserError:
            pass
