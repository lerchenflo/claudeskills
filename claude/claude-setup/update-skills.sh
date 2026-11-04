#!/usr/bin/env bash
# Pulls the skills repo from GitHub and installs new or changed skills into ~/.claude/skills.
# Meant to run as a SessionStart hook: it checks GitHub at most once per CLAUDE_SKILLS_CHECK_INTERVAL seconds, and whatever it
# prints is added to Claude's context. It prints facts only (what changed), never instructions; what Claude does with
# them is set in the user's global CLAUDE.md.
#
# Usage: update-skills.sh [--force] [--mode auto|review] [repo-dir]
#   --force        check now, ignoring the interval
#   --mode auto    install new and changed skills (default, the behaviour of older setups)
#   --mode review  only report which skills changed; install nothing (run again with --mode auto to install)
#   repo-dir       local clone to use (default ~/.claude/skills-repo, cloned on first run)
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

force=0 mode=auto want_mode=0
for arg in "$@"; do
  if [ "$want_mode" = 1 ]; then mode="$arg" want_mode=0; continue; fi
  case "$arg" in
    --force) force=1 ;;
    --mode) want_mode=1 ;;
    --mode=*) mode="${arg#--mode=}" ;;
    *) REPO_DIR="$arg" ;;
  esac
done
case "$mode" in
  auto | review) ;;
  *) echo "Skills update: unknown mode '$mode' (expected auto or review); nothing checked."; exit 0 ;;
esac

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
    echo "Skills update: $REPO_DIR cannot fast-forward to origin/$branch (it has local commits or changes)." \
      "Nothing was installed. Fix: git -C $REPO_DIR pull --rebase"
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

mkdir -p "$SKILLS_DIR"
added="" updated="" conflicts=""
for skill_md in "$tmp"/new/*/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  new_dir=$(dirname "$skill_md")
  name=$(basename "$new_dir")
  group=$(basename "$(dirname "$new_dir")")
  case "$name" in '' | . | .. | synced) continue ;; esac
  old_dir=$(ls -d "$tmp"/old/*/"$name" 2>/dev/null | head -n 1)
  [ -n "$old_dir" ] && same "$old_dir" "$new_dir" && continue # unchanged since last sync

  dst="$SKILLS_DIR/$name"
  if [ ! -e "$dst" ]; then
    if [ "$mode" = review ]; then added="$added $name"; else cp -R "$new_dir" "$dst" && added="$added $name"; fi
  elif same "$dst" "$new_dir"; then
    :
  elif [ -n "$old_dir" ] && same "$dst" "$old_dir"; then
    if [ "$mode" = review ]; then updated="$updated $name"; else rm -rf "$dst" && cp -R "$new_dir" "$dst" && updated="$updated $name"; fi
  else
    conflicts="$conflicts
  - $dst (repo version: $REPO_DIR/$group/$name)"
  fi
done

# Skills deleted or renamed in the repo: remove the local copy, but only while it still equals the last synced version.
removed=""
for skill_md in "$tmp"/old/*/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  old_dir=$(dirname "$skill_md")
  name=$(basename "$old_dir")
  case "$name" in '' | . | .. | synced) continue ;; esac
  ls -d "$tmp"/new/*/"$name" >/dev/null 2>&1 && continue # still in the repo
  dst="$SKILLS_DIR/$name"
  [ -e "$dst" ] || continue
  if same "$dst" "$old_dir"; then
    if [ "$mode" = review ]; then removed="$removed $name"; else rm -rf "$dst" && removed="$removed $name"; fi
  else
    conflicts="$conflicts
  - $dst was removed or renamed in the repo but has local changes (merge them into the renamed skill or keep it)"
  fi
done

# Only remember this commit once everything is in place (auto mode, no conflicts), so open items are reported again next time.
[ "$mode" = auto ] && [ -z "$conflicts" ] && echo "$head" >"$INSTALLED"

list() { echo "$1" | tr ' ' '\n' | sort -u | tr '\n' ' '; }
if [ -n "$added$updated$removed$conflicts" ]; then
  latest=$(git -C "$REPO_DIR" log -1 --format='%h %s')
  if [ "$mode" = review ]; then
    installed="never synced"
    [ -n "$base" ] && installed=$(git -C "$REPO_DIR" log -1 --format=%h "$base")
    echo "Skill updates available on GitHub (review mode, nothing installed). Installed: $installed. GitHub: $latest."
    [ -n "$added" ] && echo "- new:$(list "$added")"
    [ -n "$updated" ] && echo "- changed:$(list "$updated")"
    [ -n "$removed" ] && echo "- deleted or renamed in the repo:$(list "$removed")"
    [ -n "$conflicts" ] && echo "- local copy differs from the repo (never overwritten):$conflicts"
    echo "Install command: bash $0 --force --mode auto"
  else
    echo "Skills update from GitHub ($latest):"
    [ -n "$added" ] && echo "- installed:$(list "$added")"
    [ -n "$updated" ] && echo "- updated:$(list "$updated")"
    [ -n "$removed" ] && echo "- removed (deleted or renamed in the repo):$(list "$removed")"
    [ -n "$conflicts" ] && echo "- not overwritten, the local copy has changes that are not in the repo:$conflicts"
  fi
fi
exit 0
