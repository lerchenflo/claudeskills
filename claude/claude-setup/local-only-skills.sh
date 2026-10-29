#!/usr/bin/env bash
# Lists skills in ~/.claude/skills that are not in the skills repo yet, so Claude can ask the user whether to upload them.
# Skips Anthropic's built-in skills (synced/), folders without SKILL.md, and skills the user chose to keep local
# (one name per line in ~/.claude/state/skills-local-only).
#
# Usage: local-only-skills.sh [repo-dir]   (default ~/.claude/skills-repo)
# Prints one skill name per line; prints nothing when every local skill is in the repo.

set -u
REPO_DIR="${1:-${CLAUDE_SKILLS_REPO:-$HOME/.claude/skills-repo}}"
SKILLS_DIR="$HOME/.claude/skills"
KEEP_LOCAL="$HOME/.claude/state/skills-local-only"

for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  name=$(basename "$(dirname "$skill_md")")
  [ "$name" = synced ] && continue
  ls -d "$REPO_DIR"/*/"$name" >/dev/null 2>&1 && continue
  [ -f "$KEEP_LOCAL" ] && grep -qx "$name" "$KEEP_LOCAL" && continue
  echo "$name"
done
exit 0
