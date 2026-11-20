#!/usr/bin/env bash
# Enforces the 5h usage stop from the global CLAUDE.md ("Always keep <RESERVE>% of the 5h limit free").
# Reads ~/.claude/state/rate_limits.json, written by statusline-command.sh on every status line redraw.
#
#   usage-cap-hook.sh pretool        PreToolUse hook: at or above the stop value, deny the tool call.
#   usage-cap-hook.sh prompt         UserPromptSubmit hook: warn at or above the stop value; a prompt that
#                                    says "ignore the limit/cap/90%" lifts the stop for the current 5h window.
#   usage-cap-hook.sh --allow-window Lift the stop for the current 5h window (only after the user said so).
#   usage-cap-hook.sh --status       Print usage, stop value and override state (self test).
#
# The stop value is read from the global CLAUDE.md (see below). The override is stored as the window's
# resets_at in ~/.claude/state/usage-cap-override, so it expires on its own when the next window starts.
# Limit: the status line refreshes only after a reply ends, so inside one long turn the value lags.
set -u

STATE="$HOME/.claude/state"
LIMITS="$STATE/rate_limits.json"
OVERRIDE="$STATE/usage-cap-override"
MODE="${1:-}"

# Stop value: CLAUDE_USAGE_STOP, else from the global CLAUDE.md rule "Always keep <RESERVE>% of the 5h limit
# free" (stop = 100 - reserve), else 90. The "Never stop on your own" variant (100 %) turns the hook off.
GLOBAL_MD="$HOME/.claude/CLAUDE.md"
if [ -n "${CLAUDE_USAGE_STOP:-}" ]; then
  STOP="$CLAUDE_USAGE_STOP"
elif grep -q 'Never stop on your own because of the 5h usage' "$GLOBAL_MD" 2>/dev/null; then
  STOP=101
else
  reserve="$(grep -Eo 'Always keep [0-9]+% of the 5h limit free' "$GLOBAL_MD" 2>/dev/null | grep -Eo '[0-9]+' | head -1)"
  STOP=$(( 100 - ${reserve:-10} ))
fi

input=""
if [ "$MODE" = "pretool" ] || [ "$MODE" = "prompt" ]; then
  input="$(cat)"
fi

command -v jq >/dev/null 2>&1 || exit 0
[ -f "$LIMITS" ] || exit 0

used="$(jq -r '.rate_limits.five_hour.used_percentage // empty' "$LIMITS" 2>/dev/null)"
resets="$(jq -r '.rate_limits.five_hour.resets_at // empty' "$LIMITS" 2>/dev/null)"
now="$(date +%s)"

reset_time() {
  date -r "$resets" '+%H:%M' 2>/dev/null || date -d "@$resets" '+%H:%M' 2>/dev/null || echo "$resets"
}

over_cap() {
  [ -n "$used" ] && [ -n "$resets" ] || return 1
  # A window whose reset already passed is stale: the next redraw shows the new window.
  [ "${resets%.*}" -gt "$now" ] 2>/dev/null || return 1
  awk -v u="$used" -v s="$STOP" 'BEGIN { exit !(u + 0 >= s + 0) }'
}

overridden() {
  [ -f "$OVERRIDE" ] && [ -n "$resets" ] && [ "$(cat "$OVERRIDE" 2>/dev/null)" = "$resets" ]
}

allow_window() {
  mkdir -p "$STATE"
  printf '%s' "$resets" > "$OVERRIDE"
}

case "$MODE" in
  --allow-window)
    [ -n "$resets" ] || { echo "no 5h window in $LIMITS"; exit 1; }
    allow_window
    echo "5h stop lifted until $(reset_time)"
    ;;
  --status)
    state="off"; overridden && state="on (until $(reset_time))"
    cap="below stop"; over_cap && cap="AT OR ABOVE STOP"
    echo "5h: ${used:-?}% stop: ${STOP}% resets: $( [ -n "$resets" ] && reset_time || echo '?') -> $cap, override: $state"
    ;;
  prompt)
    prompt="$(printf '%s' "$input" | jq -r '.prompt // empty' 2>/dev/null | tr '[:upper:]' '[:lower:]')"
    if printf '%s' "$prompt" | grep -Eq 'ignore (the )?(5h |usage )?(limit|cap|stop|90 ?%)'; then
      [ -n "$resets" ] && allow_window
      exit 0
    fi
    over_cap && ! overridden || exit 0
    msg="5h usage is at ${used}% (stop at ${STOP}%, window resets $(reset_time)). Tool calls are blocked. Stop cleanly: report the state in text and say how to continue after $(reset_time). The user lifts the stop for this window by saying 'ignore the limit'."
    jq -n --arg m "$msg" '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $m}}'
    ;;
  pretool)
    over_cap && ! overridden || exit 0
    cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
    case "$cmd" in *usage-cap-hook.sh*) exit 0 ;; esac
    msg="5h usage is at ${used}% (stop at ${STOP}%, window resets $(reset_time)): tool call blocked. Stop now and report the state in text: what is done, what is open, how to continue after $(reset_time). Only if the user explicitly says to ignore the limit, run: bash ~/.claude/skills/claude-setup/usage-cap-hook.sh --allow-window"
    jq -n --arg m "$msg" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $m}}'
    ;;
esac
exit 0
