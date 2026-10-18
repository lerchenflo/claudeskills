#!/usr/bin/env bash
# Pulls the skills repo from GitHub and installs new or changed skills into ~/.claude/skills
# (and the Nextcloud mirror, if this device has one). Meant to run as a SessionStart hook:
# it checks GitHub at most once per CLAUDE_SKILLS_CHECK_INTERVAL seconds, and whatever it
# prints is added to Claude's context.
#
# Usage: update-skills.sh [--force] [repo-dir]
#   --force    check now, ignoring the interval
#   repo-dir   local clone to use (default ~/.claude/skills-repo, cloned on first run)
#
# Repo layout is <group>/<skill>/SKILL.md; skills are installed flat as ~/.claude/skills/<skill>/.
# A local skill is only overwritten when it still equals the version from the last sync, so
# local edits are never lost - those are reported as conflicts for Claude to merge.
#
# Runs on macOS, Linux and Windows (Git Bash, which Claude Code uses for hooks). Needs git, diff, tar.

set -u

REPO_URL="${CLAUDE_SKILLS_REPO_URL:-https://github.com/lerchenflo/claudeskills.git}"
REPO_DIR="${CLAUDE_SKILLS_REPO:-$HOME/.claude/skills-repo}"
CHECK_INTERVAL="${CLAUDE_SKILLS_CHECK_INTERVAL:-21600}" # 6 h
SKILLS_DIR="$HOME/.claude/skills"
STATE_DIR="$HOME/.claude/state"
STAMP="$STATE_DIR/skills-update-check"
INSTALLED="$STATE_DIR/skills-installed-commit"

force=0
for arg in "$@"; do
  case "$arg" in
    --force) force=1 ;;
    *) REPO_DIR="$arg" ;;
  esac
done

mkdir -p "$STATE_DIR"
now=$(date +%s)
last=$(cat "$STAMP" 2>/dev/null)
case "$last" in '' | *[!0-9]*) last=0 ;; esac
if [ "$force" != 1 ] && [ $((now - last)) -lt "$CHECK_INTERVAL" ]; then
  exit 0
fi
echo "$now" >"$STAMP"

# Never prompt for credentials, give up on a stalled connection instead of hanging the session start.
export GIT_TERMINAL_PROMPT=0 GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=15

if [ ! -d "$REPO_DIR/.git" ]; then
  git clone --quiet "$REPO_URL" "$REPO_DIR" 2>/dev/null || exit 0 # offline: try again next time
else
  git -C "$REPO_DIR" fetch --quiet origin 2>/dev/null || exit 0
  branch=$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)
  if ! git -C "$REPO_DIR" merge --ff-only --quiet "origin/$branch" >/dev/null 2>&1; then
    echo "Skills update: $REPO_DIR cannot fast-forward to origin/$branch (local commits or changes)." \
      "Run 'git -C $REPO_DIR pull --rebase', resolve, push, then 'bash $0 --force'."
    exit 0
  fi
fi

head=$(git -C "$REPO_DIR" rev-parse HEAD)
base=$(cat "$INSTALLED" 2>/dev/null)
[ "$base" = "$head" ] && exit 0
if [ -n "$base" ] && ! git -C "$REPO_DIR" cat-file -e "$base^{commit}" 2>/dev/null; then
  base="" # history was rewritten: compare against nothing, conflicts get reported
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/new" "$tmp/old"
git -C "$REPO_DIR" archive HEAD | tar -x -C "$tmp/new"
[ -n "$base" ] && git -C "$REPO_DIR" archive "$base" | tar -x -C "$tmp/old"

# CRLF vs LF does not count as a change (editors on Windows).
same() { diff -rq --strip-trailing-cr -x __pycache__ -x .DS_Store "$1" "$2" >/dev/null 2>&1; }

targets="$SKILLS_DIR"
for nc in "$HOME"/Library/CloudStorage/Nextcloud-*/Schneaggchat/claude_skills "$HOME/Nextcloud/Schneaggchat/claude_skills"; do
  [ -d "$nc" ] && targets="$targets
$nc"
done

added="" updated="" conflicts=""
for skill_md in "$tmp"/new/*/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  new_dir=$(dirname "$skill_md")
  name=$(basename "$new_dir")
  group=$(basename "$(dirname "$new_dir")")
  case "$name" in '' | . | .. | synced) continue ;; esac
  old_dir=$(ls -d "$tmp"/old/*/"$name" 2>/dev/null | head -n 1)
  [ -n "$old_dir" ] && same "$old_dir" "$new_dir" && continue # unchanged since last sync

  while IFS= read -r root; do
    mkdir -p "$root"
    dst="$root/$name"
    if [ ! -e "$dst" ]; then
      cp -R "$new_dir" "$dst" && added="$added $name"
    elif same "$dst" "$new_dir"; then
      :
    elif [ -n "$old_dir" ] && same "$dst" "$old_dir"; then
      rm -rf "$dst" && cp -R "$new_dir" "$dst" && updated="$updated $name"
    else
      conflicts="$conflicts
  - $dst (repo version: $REPO_DIR/$group/$name)"
    fi
  done <<EOF
$targets
EOF
done

# Only remember this commit once everything is in place, so open conflicts are reported again next time.
[ -z "$conflicts" ] && echo "$head" >"$INSTALLED"

if [ -n "$added$updated$conflicts" ]; then
  echo "Skills update from GitHub ($(git -C "$REPO_DIR" log -1 --format='%h %s')):"
  [ -n "$added" ] && echo "- installed:$(echo "$added" | tr ' ' '\n' | sort -u | tr '\n' ' ')"
  [ -n "$updated" ] && echo "- updated:$(echo "$updated" | tr ' ' '\n' | sort -u | tr '\n' ' ')"
  if [ -n "$conflicts" ]; then
    echo "- not overwritten, the local copy has changes that are not in the repo:$conflicts"
    echo "  Merge each pair (keep every rule from both, newest wording wins), write the result to the" \
      "local copy and the repo, commit and push, then run 'bash $0 --force'. Tell the user what was merged."
  fi
  echo "Tell the user which skills changed."
fi
exit 0
