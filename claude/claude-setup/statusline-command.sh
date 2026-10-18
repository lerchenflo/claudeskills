#!/usr/bin/env bash
input=$(cat)
# Force C numeric locale so printf accepts dot-decimal percentages regardless of user locale
export LC_NUMERIC=C

model=$(echo "$input" | jq -r '.model.display_name // "unknown model"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')
dir=$(basename "$cwd")
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
total_input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
window_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
session_id=$(echo "$input" | jq -r '.session_id // empty')
five_hour_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_hour_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
seven_day_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
seven_day_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
echo "$input" | jq -c '{rate_limits, written_at: now}' > "$HOME/.claude/state/rate_limits.json" 2>/dev/null

format_tokens() {
  local n="$1"
  if [ -z "$n" ] || [ "$n" = "null" ]; then
    return
  fi
  if [ "$n" -ge 1000 ]; then
    awk -v n="$n" 'BEGIN{printf "%.1fk", n/1000}'
  else
    printf '%s' "$n"
  fi
}

# Color for a 0-100 usage percentage (green < 50, yellow < 80, red >= 80)
pct_color() {
  local p="$1"
  if [ "$p" -ge 80 ]; then
    printf '%s' "$red"
  elif [ "$p" -ge 50 ]; then
    printf '%s' "$yellow"
  else
    printf '%s' "$green"
  fi
}

# Format a unix epoch: GNU date (Linux, Git Bash on Windows) takes -d @ts, BSD date (macOS) takes -r ts
date_at() {
  date -d "@$1" "$2" 2>/dev/null || date -r "$1" "$2" 2>/dev/null
}

# Format a unix-epoch reset timestamp: "HH:MM" if today, otherwise "Ddd HH:MM"
format_reset() {
  local ts="$1"
  if [ -z "$ts" ] || [ "$ts" = "null" ]; then
    return
  fi
  ts=$(printf '%.0f' "$ts")
  local today reset_day
  today=$(date +%Y-%m-%d)
  reset_day=$(date_at "$ts" +%Y-%m-%d) || return
  if [ "$reset_day" = "$today" ]; then
    date_at "$ts" +%H:%M
  else
    date_at "$ts" '+%a %H:%M'
  fi
}

# Build " label:NN% (resets ...)" colored by usage; empty when no data
limit_part() {
  local label="$1" pct="$2" reset_ts="$3"
  if [ -z "$pct" ] || [ "$pct" = "null" ]; then
    return
  fi
  local pct_int color reset_fmt
  pct_int=$(printf '%.0f' "$pct")
  color=$(pct_color "$pct_int")
  reset_fmt=$(format_reset "$reset_ts")
  if [ -n "$reset_fmt" ]; then
    printf ' %s%s:%s%% (resets %s)%s' "$color" "$label" "$pct_int" "$reset_fmt" "$reset"
  else
    printf ' %s%s:%s%%%s' "$color" "$label" "$pct_int" "$reset"
  fi
}

reset='\033[0m'
bold='\033[1m'
dim='\033[2m'
cyan='\033[36m'
green='\033[32m'
yellow='\033[33m'
magenta='\033[35m'
blue='\033[34m'
red='\033[31m'

ctx_part=""
if [ -n "$used_pct" ]; then
  pct_int=$(printf '%.0f' "$used_pct")
  if [ "$pct_int" -ge 80 ]; then
    ctx_color="$red"
  elif [ "$pct_int" -ge 50 ]; then
    ctx_color="$yellow"
  else
    ctx_color="$green"
  fi
  tokens_fmt=$(format_tokens "$total_input_tokens")
  window_fmt=$(format_tokens "$window_size")
  if [ -n "$tokens_fmt" ] && [ -n "$window_fmt" ]; then
    ctx_part=" ${ctx_color}context:${pct_int}% (${tokens_fmt}/${window_fmt} tok)${reset}"
  else
    ctx_part=" ${ctx_color}context:${pct_int}%${reset}"
  fi
fi

limits_part=""
limits_part+=$(limit_part "5h" "$five_hour_pct" "$five_hour_reset")
limits_part+=$(limit_part "wk" "$seven_day_pct" "$seven_day_reset")

task_part=""
if [ -n "$session_id" ]; then
  todo_file=$(ls -t "$HOME"/.claude/todos/"${session_id}"*.json 2>/dev/null | head -1)
  if [ -n "$todo_file" ] && [ -s "$todo_file" ]; then
    task=$(jq -r '
      def in_progress: map(select(.status=="in_progress"));
      def pending: map(select(.status=="pending"));
      (in_progress[0] // pending[-1] // empty) | (.activeForm // .content // empty)
    ' "$todo_file" 2>/dev/null)
    if [ -n "$task" ] && [ "$task" != "null" ]; then
      if [ "${#task}" -gt 40 ]; then
        task="${task:0:37}..."
      fi
      task_part=" ${dim}| ${task}${reset}"
    fi
  fi
fi

echo -ne "${bold}${blue}${dir}${reset} ${cyan}${model}${reset}${ctx_part}${limits_part}${task_part}"
