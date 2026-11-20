---
name: claude-setup
description: Set up Claude Code on this device with the user's personal preferences - writes the global ~/.claude/CLAUDE.md, installs the status line (context, 5h and weekly limits), sets model and effort, and syncs skills with the GitHub repo lerchenflo/claudeskills, plus a SessionStart hook for skill updates whose mode the user picks (review first, auto-install or off). Starts with a to-do list of every step and works through it. Use on the first launch on a new device, and whenever the user asks to set up, configure, update or restore their Claude preferences or skills on a machine.
---

# Claude setup

Sets up the user's personal Claude Code preferences on the device this session runs on. Idempotent: run it again any time to bring a device up to date. On a new device run it first, before any other work.

## To-do list first

Start every run with a to-do list, before any command that changes something. Use the session's task / to-do tool when there is one; otherwise write a numbered checklist in the reply. List every step below (0-6) with the sub-steps that apply on this device, the questions to ask included. Show the list, then work through it in order: mark each item in progress and done, add items that a check turns up (e.g. a skill conflict to merge), and do no work that is not on the list. Step 0 can replace this skill with a newer version: then rebuild the list from the new version. The self test (step 5) runs before the report; the report (step 6) goes through the list item by item.

Ask every question with AskUserQuestion, never as plain text (see the global rules below). Ask the open questions up front: right after step 0, check what steps 1 and 3 need (5h stop value, CLAUDE.md override, skill update mode) and ask all questions that apply in one AskUserQuestion call, with the CLAUDE.md difference summary from step 1 written just before it. Then do the steps without asking again.

## 0. Version

1. If `~/.claude/skills-repo` is missing, clone it: `git clone https://github.com/lerchenflo/claudeskills.git ~/.claude/skills-repo`. Otherwise run `git -C ~/.claude/skills-repo fetch --quiet origin`. If this fails (offline), say so and continue with the local version.
2. Tell the user which skills version this device runs and which is the latest on GitHub:
   - running: the commit in `~/.claude/state/skills-installed-commit` (written by `update-skills.sh` after each sync), shown with `git -C ~/.claude/skills-repo log -1 --format='%h %cs %s' <commit>`; "never synced" if the file is missing;
   - latest: `git -C ~/.claude/skills-repo log -1 --format='%h %cs %s' '@{upstream}'`.
3. If GitHub is newer, run `git -C ~/.claude/skills-repo pull --ff-only`. If `claude/claude-setup/` in the repo then differs from this skill folder, copy it over this folder (if this folder has changes that are not in the repo, merge them first), re-read this SKILL.md and follow the new version from step 0.

## 1. Global instructions

Set the 5h stop once. If `~/.claude/CLAUDE.md` already has the "Always keep <RESERVE>% of the 5h limit free" rule (or the 100 % variant below), keep its value and do not ask. Only when there is none (first setup on this device), ask the user with AskUserQuestion at which 5h usage Claude should stop on its own (header "5h stop", question "At what % of the 5-hour limit should Claude stop work and report?"; options "90 % (Recommended)", 80 %, 95 %, "100 % - never stop on its own"; the user can type any other value). Change the value later only when the user asks for it. Put the answer in for `<STOP>` and `100 - <STOP>` for `<RESERVE>` in the block below. For 100 %, replace the whole "Always keep <RESERVE>% ..." rule with "- Never stop on your own because of the 5h usage; only a cap the user names counts."

Fill the block below with these values, then compare it with `~/.claude/CLAUDE.md`:

- File missing: write the block. No question.
- File equals the block: change nothing, say so.
- File differs: tell the user the differences in a short text - at most 5 plain bullets such as "adds rule X", "rule Y has newer wording", "your file has extra rule Z that the setup version lacks"; no raw diff. Then ask with AskUserQuestion (header "CLAUDE.md", question "Override your global ~/.claude/CLAUDE.md with the setup version?"):
  - "Merge (Recommended)": keep every existing line that is not covered by the block, replace lines that say the same thing in older words, and never duplicate a rule.
  - "Override": replace the whole file with the block. Extra local rules are lost, so the summary must name them.
  - "Keep": leave the file untouched.

After Merge or Override, show the user the resulting diff.

```markdown
# Global instructions

- Always respond in English, whatever language user writes. Switch only when user explicitly asks. Covers every message to user - replies, progress lines, status notes, AskUserQuestion questions/options - also when project files, course material, skills or notes are in another language (e.g. German slides): files follow project's language, chat stays English. Code comments, commit messages, docs follow project's own conventions (e.g. translated string resources stay in their language).
- User asks about progress ("how far along are you", "status?", "wie weit bist du"): answer with percentage of current task or plan done (best estimate), then one short line: what done, what next.
- Longer tasks (several steps, plan, multi-file work): report progress unasked every few steps. One short line with percentage done (best estimate), e.g. "25% done - X finished, next Y". Same scale whole task, numbers only go up.
- Never assume. Requirement, design choice or behaviour unclear and answer changes what you build: ask user with interview tool (AskUserQuestion) before acting - never pick default and mention it only afterwards. Matters most in bigger work (features, plans, multi-file changes): collect open questions up front, ask together. Skip asking only for facts you can check yourself (code, docs, tools).
- Ask every open question with AskUserQuestion, never as plain text in reply. Includes yes/no confirmations, "should I ...?" offers at end of reply, choices between options or next steps. Put needed context into each question: user may see only question dialog. Plain text only for results and reports.
- "Next to-do" always starts with interview. User says "let's continue with the next to-do", "pick next todo" or similar: never start item on your own. First ask with AskUserQuestion which item next (offer top open items of to-do list, one short line each) and whether to commit current changes first. Then interview about picked item before building. Skip only when same session already settled it: earlier answers fixed exactly what comes next and in which order.
- Always use the `caveman` skill at level **ultra** for every reply, in every session, unless the user says "stop caveman" or "normal mode". This is very important to keep token use low. The caveman plugin default is set to ultra in `~/.config/caveman/config.json` (`{"defaultMode": "ultra"}`); a hook line saying "full" never lowers the level.
- After change with several small fixes or edits: end last reply of that work with small table of what changed or fixed, one row per item (also in caveman mode). Skip table for single change.

## Usage limits
- User may ask to stop or pause at usage limit (e.g. "stop at 12% of the 5h limit", "don't use more than 20%"). Read current values from file status line writes:
  `jq -r '"5h: \(.rate_limits.five_hour.used_percentage)% (resets \(.rate_limits.five_hour.resets_at)) week: \(.rate_limits.seven_day.used_percentage)%"' ~/.claude/state/rate_limits.json`
  (`resets_at` = epoch seconds: `date -r <ts>` on macOS, `date -d @<ts>` on Linux). Check before and during long work, especially before spawning subagents. Stop cleanly (commit/report state) before cap passed.
- File refreshes only on status line redraw, about 3 seconds after response ends - inside running turn value lags real usage. Leave margin. Key can be missing (e.g. no `five_hour` right after reset); never claim usage cannot be read.
- Percentages are of current window. New 5h window starts at `resets_at`, so cap like "20% of the limit" applies to window work runs in.
- Always keep <RESERVE>% of the 5h limit free for other use: even without cap from user, stop cleanly (commit/report state) once 5h usage reaches <STOP>%, say how to continue after `resets_at`. Never skip this stop on your own. User asks for long-running task - work that runs overnight or unattended ("night work", "over night", "while I sleep", autonomous mode) or big multi-step plan to implement autonomously: ask before starting whether <STOP>% stop should be ignored for this work (user may want as much done as possible before weekly limit resets, because unused tokens are lost); ignore only on yes. Cap user names always wins. A hook enforces the stop (`usage-cap-hook.sh`, see the claude-setup skill): at the stop it blocks every tool call. On a yes to ignoring it, lift it for the current 5h window with `bash ~/.claude/skills/claude-setup/usage-cap-hook.sh --allow-window`; never run it without that yes.

## Private data in requests
- Never send user's private data to external service on your own: no email address, name, username, phone number, home address, location, account or device IDs, tokens or API keys in any request header (e.g. `User-Agent`, `From`, `Referer`), URL, query parameter or payload. Holds even when site's policy asks automated clients to identify themselves or give contact details.
- Request would need or could include such data: stop before sending, interview user with AskUserQuestion. Make very clear: which data exactly, to which service and URL, in which field (header name, parameter, body), how often, why. Always offer neutral alternative (generic tool name, no contact data, library default); recommend it unless service really requires data.
- Send private data only after user explicitly agrees for that service and that field. Yes for one service, field or session does not carry over to another.
- Default for scripts and tools you write: neutral `User-Agent` (tool name only or library default), never one carrying personal contact data.

## Git
- No Claude attribution in commits or pull requests (no `Co-Authored-By: Claude …` trailer, no "Generated with Claude Code" line). `claude-setup` turns it off with `"attribution": { "commit": "", "pr": "" }` in `~/.claude/settings.json`; user's choice for every repo.

## Client and server projects
- Some projects = client repo plus server repo (app and its backend). Agent changes code only in own repo; reading other repo fine.
- Change user approved needs work in other repo: hand it over. Run `ListAgents`: session of other repo live, send request with `SendMessage`. None live or message fails: add request to other repo's to-do file (one its CLAUDE.md names, e.g. `Todo.md` or `plans/Todo.md`) with source and date. That to-do file = only file agent may write in other repo.
- Hand over only changes user approved, never own guess.
- Describe what is needed, not how to build it: behaviour, user's decisions, who may do what, edge cases, compatibility with released versions, exact field names this side sends or reads. Leave other side's structure (classes, services, storage, file layout) to other agent: it researches own code, decides with own skills.
- Receiving agent replies with contract it built (endpoints, field names, changes to proposed names); requester follows it. Rules work both ways: client to server and server to client.
- Project's CLAUDE.md may name peer repo, its to-do file or stricter format.

## Builds
- Compile tasks (e.g. Gradle `compile*` tasks) may run freely to check changes, only if machine not laptop. Check first: macOS `pmset -g batt | grep -q InternalBattery` (match = laptop); Linux `ls /sys/class/power_supply/BAT*` (exists = laptop); Windows `Get-CimInstance Win32_Battery` (any result = laptop). On laptop, and for every other build task (tests, assemble, run, install, full build, publish), run only when user explicitly asks. Project's CLAUDE.md may name exact tasks.

## Starting at a specific time
- User wants work to start at specific time ("start at 14:40", "do this in the last 10 min of the 5h window"): schedule with session cron (`CronCreate`, one-shot, local time) carrying full task as prompt - never by sleeping or polling. Tell user scheduled time and that job only lives while this session stays open.

## Skills
- Skills live in `~/.claude/skills/`, synced between devices over public GitHub repo `lerchenflo/claudeskills` (local clone `~/.claude/skills-repo`, grouped as `<group>/<skill>/`).
- After creating or changing skill: copy updated skill folder to its group folder in `~/.claude/skills-repo` (new skill: pick fitting group, add to skill list in repo README), then `git pull --rebase`, commit, push.
- Then run `bash ~/.claude/skills/claude-setup/local-only-skills.sh`. Lists skills (local, not in repo yet): ask user with AskUserQuestion (multiSelect) which to upload too. Upload chosen ones same way; write names user keeps local into `~/.claude/state/skills-local-only` (one per line) so not offered again.
- Never overwrite or delete existing skill in `~/.claude/skills/` with repo version without asking. Merging (keep every rule from both) fine; replacing not.
- Write skills in English by default (SKILL.md, scripts, code comments, templates, file names), even when user writes another language. Only content that must be in another language stays in it (quoted exam examples, UI labels of course in that language); say so in skill.
- Project-specific skills (named after or only useful for one project) stay in that project's `.claude/skills/`, never in `~/.claude/skills/` or repo.
- SessionStart hook (`~/.claude/skills/claude-setup/update-skills.sh`) checks GitHub for new skill versions; mode (review, auto or off) set by `claude-setup`. Review mode: hook reports available updates, tell user which skills changed with short summary of each diff (`git -C ~/.claude/skills-repo diff <installed>..HEAD -- <group>/<skill>`), install only after user agrees (`bash ~/.claude/skills/claude-setup/update-skills.sh --force --mode auto`). Auto mode: tell user which skills installed or updated. Hook reports conflict (skill changed both here and on another device): never overwrite blindly - merge both versions (keep every rule from both, newest wording wins on conflicts), write merged result to both places, push, tell user what merged.
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
  "attribution": { "commit": "", "pr": "" }
}
```

`attribution` with empty strings hides the Claude co-author trailer in commits and the "Generated with Claude Code" line in pull requests (the older `includeCoAuthoredBy` key is deprecated; remove it if present). Settings are not synced via GitHub - this section is their only source.

The setup installs no plugins: `caveman` comes as a skill from the repo. Older versions of this setup enabled the plugins `caveman@caveman` and `claude-mem@thedotmack` (with their marketplaces). Leave them as they are unless the user asks, but name them in the report; for `claude-mem`, also say that its worker needs the Bun runtime and records nothing without it (check `~/.claude-mem/logs/` for "Bun runtime not found").

### Skill update mode (SessionStart hook)

Each device picks how it gets skill updates from GitHub. Check `~/.claude/settings.json` for a `SessionStart` entry that runs `update-skills.sh`, and `~/.claude/state/skills-update-mode`:

- Entry with `--mode review` or `--mode auto`: keep it (only fix an older matcher, see below). Report the mode, do not ask.
- Entry without `--mode` (older setup; it behaves like auto): ask the question below once and rewrite the entry with the chosen mode.
- No entry and the mode file says `off` (or the older `~/.claude/state/skills-hook-declined` exists): report "skill updates: off", do not ask.
- No entry and no mode file: ask with AskUserQuestion (header "Updates", question "How should this device get skill updates from GitHub (lerchenflo/claudeskills)?"):
  - "Review first (Recommended)": the hook checks GitHub at most every 6 hours and only reports which skills changed. Nothing is installed until the user agrees.
  - "Auto-install": the hook installs new and changed skills on its own. Local edits are never overwritten.
  - "Off": no hook. Skills update only when this skill runs again (or with `update-skills.sh --force --mode auto`).

Store the answer: review or auto - merge the entry below with that mode and write the mode into `~/.claude/state/skills-update-mode`; off - write `off` there and remove an existing entry. Change the mode later only when the user asks.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          { "type": "command", "shell": "bash", "command": "bash ~/.claude/skills/claude-setup/update-skills.sh --mode review", "timeout": 60 }
        ]
      }
    ]
  }
}
```

Append the entry to any existing `SessionStart` list and never add it twice; an existing entry with an older matcher (e.g. only `startup`) gets this one. `startup|resume` because a resumed session (`claude --resume` / `--continue`) is a restart too, and the hook would never run on devices that always resume.

What the hook does: at most every 6 hours (`CLAUDE_SKILLS_CHECK_INTERVAL`, in seconds) it fetches the repo into `~/.claude/skills-repo` and compares it with the last installed commit. Review mode prints the new, changed and removed skills and installs nothing; the user's global CLAUDE.md tells Claude to show the diffs and install only after the user agrees. Auto mode installs new and changed skills into `~/.claude/skills/`. In both modes it never overwrites a local copy that has its own changes or a local skill that was never synced (it reports them as conflicts), and a skill deleted or renamed in the repo is removed locally only while the local copy still equals the last synced version. The hook prints facts only, never instructions to Claude. In review mode `update-skills.sh` itself changes only when the user installs an update, so no unreviewed code runs. Offline it stays silent. Needs `git`, `bash`, `diff` and `tar`; on Windows these come with Git for Windows, whose Git Bash runs the hook (`"shell": "bash"`).

### Usage cap hook (PreToolUse + UserPromptSubmit)

The 5h stop from step 1 is enforced by a hook, not only by text: sessions drift past a text rule in long work (user, 2026-11-20). Merge both entries into `~/.claude/settings.json` (append to existing lists, never twice; replace an older entry that runs `usage-cap-hook.sh`):

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "*", "hooks": [ { "type": "command", "shell": "bash", "command": "bash ~/.claude/skills/claude-setup/usage-cap-hook.sh pretool", "timeout": 10 } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "shell": "bash", "command": "bash ~/.claude/skills/claude-setup/usage-cap-hook.sh prompt", "timeout": 10 } ] }
    ]
  }
}
```

What `usage-cap-hook.sh` does: reads `~/.claude/state/rate_limits.json` (written by the status line, step 2). The stop value comes from the global CLAUDE.md rule "Always keep <RESERVE>% of the 5h limit free" (stop = 100 - reserve; the "Never stop on your own" variant turns the hook off; `CLAUDE_USAGE_STOP` overrides). At or above the stop it denies every tool call with a message to stop cleanly and report, and warns on every prompt. A prompt that says "ignore the limit" (or cap / stop / 90%) lifts the stop for the current 5h window; after a yes in AskUserQuestion Claude runs `bash ~/.claude/skills/claude-setup/usage-cap-hook.sh --allow-window` (the only command the hook lets through). The lift is stored as the window's `resets_at` in `~/.claude/state/usage-cap-override` and ends with the window. Limit: the status line refreshes only after a reply ends, so inside one long turn the value lags. Needs `jq` and `awk`.

### Caveman level

Caveman runs at level **ultra** in every session (user, 2026-11-20). If the plugin `caveman@caveman` is enabled, always write `~/.config/caveman/config.json` with `{"defaultMode": "ultra"}` (merge the key into an existing file, keep its other keys). Why: the plugin's hooks re-arm caveman at their default level whenever a prompt says something like "use caveman"; without this file that default is "full", so a session drops from ultra back to full. The level is stored per session in `~/.claude/.caveman-sessions/<session id>.mode`.

## 4. Skills from GitHub

1. Make sure `~/.claude/skills-repo` is up to date (step 0). Pushing needs the user's GitHub login on this device (`gh auth login` or an SSH key); if a push fails, tell the user how to log in.
2. The repo groups skills as `<group>/<skill>/`; locally they are flat as `~/.claude/skills/<skill>/`. Never overwrite or delete a skill that already exists in `~/.claude/skills/`. Compare each skill:
   - only in the repo: copy it into `~/.claude/skills/` (nothing local is touched);
   - in both but different: never replace the local copy with the repo version; merge as described in the Skills rules above (keeps every rule from both) and show the user what changed;
   - only local: list them with `bash ~/.claude/skills/claude-setup/local-only-skills.sh` and ask the user (AskUserQuestion, multiSelect) which to upload; never upload without asking. Project-specific skills: say they belong in that project's `.claude/skills/`. Copy the chosen ones into a fitting group folder in the repo and add them to the README skill list; write the others into `~/.claude/state/skills-local-only` (one name per line) so they are not offered again.
3. If the repo changed, show the user `git -C ~/.claude/skills-repo status --short`, then ask with AskUserQuestion whether to commit and push; do it only on yes.
4. Run `bash ~/.claude/skills/claude-setup/update-skills.sh --force --mode auto` once, after the user has seen the changes from 2. It records the synced commit, so from then on the hook (if installed) only reports or installs what changes on GitHub.

Skip `~/.claude/skills/synced/` (Anthropic's built-in skills, managed by the app) everywhere and never put a `settings.json` into a skills folder.

## 5. Self test

Run every check, and fix or report each failure before the report. Never leave a test value behind: back up `~/.claude/state/rate_limits.json` first and restore it at the end, and delete `~/.claude/state/usage-cap-override` before and after.

1. Files: `~/.claude/CLAUDE.md`, `~/.claude/statusline-command.sh`, `~/.claude/state/rate_limits.json` (exists after the first status line redraw) and `~/.config/caveman/config.json` with `defaultMode` `ultra` (when the caveman plugin is enabled).
2. `jq . ~/.claude/settings.json` parses, and `hooks` has exactly one entry each for `update-skills.sh` (unless updates are off) and `usage-cap-hook.sh pretool` / `prompt`.
3. Status line: `echo '{}' | bash ~/.claude/statusline-command.sh` prints a line and does not fail.
4. Usage cap hook, with fake values written into `rate_limits.json` (`resets_at` one hour ahead unless stated):
   - 50 %: `echo '{"tool_input":{"command":"ls"}}' | bash ~/.claude/skills/claude-setup/usage-cap-hook.sh pretool` prints nothing (allowed);
   - stop value + 2: same call prints `permissionDecision` `deny`; `echo '{"prompt":"go on"}' | ... prompt` prints a `UserPromptSubmit` context;
   - stop value + 2 with `--allow-window` in the command: allowed;
   - stop value + 5 with `resets_at` in the past: allowed (stale window);
   - stop value + 2, then `echo '{"prompt":"ignore the limit"}' | ... prompt`: the next pretool call is allowed, and `--status` says override on; with `resets_at` five hours later (next window) the call is denied again.
   - `bash ~/.claude/skills/claude-setup/usage-cap-hook.sh --status` after the restore shows the real usage and the stop value from CLAUDE.md.
5. Caveman (plugin enabled): find `caveman-mode-tracker.js` under `~/.claude/plugins/cache/caveman/`, run `echo '{"prompt":"use caveman","session_id":"selftest-0000"}' | node <path>` and check the output names level ultra; then delete `~/.claude/.caveman-sessions/selftest-0000.mode`.
6. Skills: `git -C ~/.claude/skills-repo status --short` is clean, and `~/.claude/state/skills-installed-commit` matches the repo HEAD after step 4.

## 6. Report

Include the self test result (each check passed or what failed). Go through the to-do list item by item: what changed on this device (5h stop value, CLAUDE.md choice - merged, overridden or kept - and its diff, status line installed or updated, settings merged, plugins from older setups, skill update mode - review / auto / off, new or unchanged - skills copied/merged/pushed) and anything skipped. End with the skills version now on this device (`git -C ~/.claude/skills-repo log -1 --format='%h %cs %s'`) and whether it matches the latest commit on GitHub.
