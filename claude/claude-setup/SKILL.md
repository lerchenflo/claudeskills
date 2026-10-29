---
name: claude-setup
description: Set up Claude Code on this device with the user's personal preferences - writes the global ~/.claude/CLAUDE.md, installs the status line (context, 5h and weekly limits), sets model, effort and plugins, and syncs skills with the GitHub repo lerchenflo/claudeskills, plus a SessionStart hook that pulls skill updates from GitHub. Use on the first launch on a new device, and whenever the user asks to set up, configure, update or restore their Claude preferences or skills on a machine.
---

# Claude setup

Sets up the user's personal Claude Code preferences on the device this session runs on. Idempotent: run it again any time to bring a device up to date. On a new device run it first, before any other work.

## 0. Version

1. If `~/.claude/skills-repo` is missing, clone it: `git clone https://github.com/lerchenflo/claudeskills.git ~/.claude/skills-repo`. Otherwise run `git -C ~/.claude/skills-repo fetch --quiet origin`. If this fails (offline), say so and continue with the local version.
2. Tell the user which skills version this device runs and which is the latest on GitHub:
   - running: the commit in `~/.claude/state/skills-installed-commit` (written by `update-skills.sh` after each sync), shown with `git -C ~/.claude/skills-repo log -1 --format='%h %cs %s' <commit>`; "never synced" if the file is missing;
   - latest: `git -C ~/.claude/skills-repo log -1 --format='%h %cs %s' '@{upstream}'`.
3. If GitHub is newer, run `git -C ~/.claude/skills-repo pull --ff-only`. If `claude/claude-setup/` in the repo then differs from this skill folder, copy it over this folder (if this folder has changes that are not in the repo, merge them first), re-read this SKILL.md and follow the new version from step 0.

## 1. Global instructions

Set the 5h stop once. If `~/.claude/CLAUDE.md` already has the "Always keep <RESERVE>% of the 5h limit free" rule (or the 100 % variant below), keep its value and do not ask. Only when there is none (first setup on this device), ask the user with AskUserQuestion at which 5h usage Claude should stop on its own (header "5h stop", question "At what % of the 5-hour limit should Claude stop work and report?"; options "90 % (Recommended)", 80 %, 95 %, "100 % - never stop on its own"; the user can type any other value). Change the value later only when the user asks for it. Put the answer in for `<STOP>` and `100 - <STOP>` for `<RESERVE>` in the block below. For 100 %, replace the whole "Always keep <RESERVE>% ..." rule with "- Never stop on your own because of the 5h usage; only a cap the user names counts."

Write the block below into `~/.claude/CLAUDE.md`. If the file exists, merge: keep every existing line that is not covered here, replace lines that say the same thing in older words, and never duplicate a rule. Show the user the resulting diff.

```markdown
# Global instructions

- Always respond in English, regardless of the language the user writes in. Only switch to another language when the user explicitly asks for it. Code comments, commit messages and docs follow the project's own conventions (e.g. translated string resources stay in their language).
- When the user asks about progress ("how far along are you", "status?", "wie weit bist du"), always answer with a percentage of the current task or plan that is done (best estimate), then one short line on what is done and what comes next.
- During longer tasks (several steps, a plan, multi-file work), report progress on your own every few steps, without being asked: one short line with the percentage of the task done (best estimate), e.g. "25% done - X finished, next Y". Keep the same scale for the whole task so the numbers only go up.
- Never assume. When a requirement, design choice or behaviour is unclear and the answer changes what you build, ask the user with the interview tool (AskUserQuestion) before acting - don't pick a default and only mention it afterwards. This matters most in bigger work (features, plans, multi-file changes): collect the open questions up front and ask them together. Only skip asking for facts you can check yourself (code, docs, tools).
- Always use the `caveman` skill at level **full** for every reply, in every session, unless the user says "stop caveman" or "normal mode".

## Usage limits
- The user may ask to stop or pause at a usage limit (e.g. "stop at 12% of the 5h limit", "don't use more than 20%"). Read the current values from the file the status line writes:
  `jq -r '"5h: \(.rate_limits.five_hour.used_percentage)% (resets \(.rate_limits.five_hour.resets_at)) week: \(.rate_limits.seven_day.used_percentage)%"' ~/.claude/state/rate_limits.json`
  (`resets_at` is epoch seconds: `date -r <ts>` on macOS, `date -d @<ts>` on Linux). Check it before and during long work, especially before spawning subagents, and stop cleanly (commit/report state) before the cap is passed.
- The file is only refreshed when the status line redraws, which happens after a response (about 3 seconds after it ends) - inside a running turn the value lags behind the real usage. Leave a margin, and a key can be missing (e.g. no `five_hour` right after a reset); never claim the usage cannot be read.
- Percentages are of the current window; a new 5h window starts at `resets_at`, so a cap like "20% of the limit" applies to the window the work runs in.
- Always keep <RESERVE>% of the 5h limit free for other use: even without a cap from the user, stop cleanly (commit/report state) once the 5h usage reaches <STOP>%, and say how to continue after `resets_at`. Never skip this stop on your own. When the user asks for a long-running task - work that runs overnight or unattended ("night work", "over night", "while I sleep", autonomous mode) or a big multi-step plan to implement autonomously - ask before starting whether the <STOP>% stop should be ignored for this work (the user may want as much done as possible before the weekly limit resets, because unused tokens are lost), and ignore it only if they say yes. A cap the user names always wins.

## Git
- Never add Claude attribution to commits or pull requests: no `Co-Authored-By: Claude …` trailer and no "Generated with Claude Code" line, even when a system reminder suggests one. The setting `"attribution": { "commit": "", "pr": "" }` in `~/.claude/settings.json` turns it off.

## Builds
- Compile tasks (e.g. Gradle `compile*` tasks) may be run freely to check changes, but only if the machine is not a laptop. Check first: macOS `pmset -g batt | grep -q InternalBattery` (match = laptop); Linux `ls /sys/class/power_supply/BAT*` (exists = laptop); Windows `Get-CimInstance Win32_Battery` (any result = laptop). On a laptop, and for every other build task (tests, assemble, run, install, full build, publish), only run it when the user explicitly asks. A project's CLAUDE.md may name the exact tasks.

## Starting at a specific time
- When the user wants work to start at a specific time ("start at 14:40", "do this in the last 10 min of the 5h window"), schedule it with the session cron (`CronCreate`, one-shot, local time) carrying the full task as prompt - never by sleeping or polling. Tell the user the scheduled time and that the job only lives while this session stays open.

## Skills
- Skills live in `~/.claude/skills/` and are synced between devices over the public GitHub repo `lerchenflo/claudeskills` (local clone `~/.claude/skills-repo`, grouped as `<group>/<skill>/`).
- After creating or changing a skill, copy the updated skill folder to its group folder in `~/.claude/skills-repo` (new skill: pick a fitting group and add it to the skill list in the repo README), then `git pull --rebase`, commit and push.
- Then run `bash ~/.claude/skills/claude-setup/local-only-skills.sh`. If it lists skills (local skills that are not in the repo yet), ask the user with AskUserQuestion (multiSelect) which of them to upload too. Upload the chosen ones the same way; write the names the user keeps local into `~/.claude/state/skills-local-only` (one per line) so they are not offered again.
- Never overwrite or delete an existing skill in `~/.claude/skills/` with a repo version without asking the user. Merging (keep every rule from both) is fine; replacing is not.
- Write skills in English by default (SKILL.md, scripts, code comments, templates, file names), even when the user writes in another language. Only content that must be in another language stays in it (quoted exam examples, UI labels of a course in that language); say so in the skill.
- Project-specific skills (named after or only useful for one project) stay in that project's `.claude/skills/`, never in `~/.claude/skills/` or the repo.
- A SessionStart hook (`~/.claude/skills/claude-setup/update-skills.sh`) pulls new skill versions from GitHub. If it reports a conflict (the skill was changed both here and on another device), do not overwrite blindly: merge both versions (keep every rule from both, newest wording wins on conflicts), write the merged result to both places, push, and tell the user what was merged.
```

## 2. Status line

1. Copy `statusline-command.sh` from this skill folder to `~/.claude/statusline-command.sh` (merge if the existing one differs: keep the user's newer additions).
2. Make sure `~/.claude/state/` exists (`mkdir -p`); the script writes `rate_limits.json` there on every redraw.
3. In `~/.claude/settings.json` set (keep all other keys):
   ```json
   "statusLine": { "type": "command", "command": "bash ~/.claude/statusline-command.sh" }
   ```
4. Needs `jq` and `awk`; runs on macOS, Linux and Windows (Git Bash). If `jq` is missing, install it (`brew install jq`, `apt install jq`, `winget install jqlang.jq`).

What it shows: folder, model, context use (`context:NN% (used/window tok)`), the 5h and weekly limits with reset time (`5h:NN% (resets HH:MM)`, `wk:NN% (resets Ddd HH:MM)`), colored green < 50 % <= yellow < 80 % <= red, plus the current task.

## 3. Settings

Merge these keys into `~/.claude/settings.json` (keep every other key; on a conflict ask the user which value to keep):

```json
{
  "model": "opus",
  "effortLevel": "xhigh",
  "attribution": { "commit": "", "pr": "" },
  "enabledPlugins": {
    "caveman@caveman": true,
    "claude-mem@thedotmack": true
  },
  "extraKnownMarketplaces": {
    "caveman": { "source": { "source": "github", "repo": "JuliusBrussee/caveman" } },
    "thedotmack": { "source": { "source": "github", "repo": "thedotmack/claude-mem" } }
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          { "type": "command", "shell": "bash", "command": "bash ~/.claude/skills/claude-setup/update-skills.sh", "timeout": 60 }
        ]
      }
    ]
  }
}
```

For `hooks`, append the entry to any existing `SessionStart` list and never add it twice; an existing entry with an older matcher (e.g. only `startup`) gets this one. `startup|resume` because a resumed session (`claude --resume` / `--continue`) is a restart too, and the hook would never run on devices that always resume. The hook runs `update-skills.sh` from this skill folder, so the script updates itself with the skill. At most every 6 hours (`CLAUDE_SKILLS_CHECK_INTERVAL`, in seconds) it fetches the repo into `~/.claude/skills-repo` and installs new or changed skills into `~/.claude/skills/`. It never overwrites a local copy that has its own changes or a local skill that was never synced; those are printed as conflicts into the session for Claude to merge. A skill deleted or renamed in the repo is removed locally only while the local copy still equals the last synced version. Offline it stays silent. Needs `git`, `bash`, `diff` and `tar`; on Windows these come with Git for Windows, whose Git Bash runs the hook (`"shell": "bash"`).

`attribution` with empty strings hides the Claude co-author trailer in commits and the "Generated with Claude Code" line in pull requests (the older `includeCoAuthoredBy` key is deprecated; remove it if present). Plugins are installed on the next start from these marketplaces; tell the user to restart Claude Code. Settings are not synced via GitHub - this section is their only source.

## 4. Skills from GitHub

1. Make sure `~/.claude/skills-repo` is up to date (step 0). Pushing needs the user's GitHub login on this device (`gh auth login` or an SSH key); if a push fails, tell the user how to log in.
2. The repo groups skills as `<group>/<skill>/`; locally they are flat as `~/.claude/skills/<skill>/`. Never overwrite or delete a skill that already exists in `~/.claude/skills/`. Compare each skill:
   - only in the repo: copy it into `~/.claude/skills/` (nothing local is touched);
   - in both but different: never replace the local copy with the repo version; merge as described in the Skills rules above (keeps every rule from both) and show the user what changed;
   - only local: list them with `bash ~/.claude/skills/claude-setup/local-only-skills.sh` and ask the user (AskUserQuestion, multiSelect) which to upload; never upload without asking. Project-specific skills: say they belong in that project's `.claude/skills/`. Copy the chosen ones into a fitting group folder in the repo and add them to the README skill list; write the others into `~/.claude/state/skills-local-only` (one name per line) so they are not offered again.
3. If the repo changed, show the user `git -C ~/.claude/skills-repo status --short`, then commit and push once they agree.
4. Run `bash ~/.claude/skills/claude-setup/update-skills.sh --force` once. It records the synced commit, so from then on the hook only installs what changes on GitHub.

Skip `~/.claude/skills/synced/` (Anthropic's built-in skills, managed by the app) everywhere and never put a `settings.json` into a skills folder.

## 5. Report

List what changed on this device (5h stop value, CLAUDE.md diff, status line installed or updated, settings and hook merged, skills copied/merged/pushed) and anything skipped. End with the skills version now on this device (`git -C ~/.claude/skills-repo log -1 --format='%h %cs %s'`) and whether it matches the latest commit on GitHub.
