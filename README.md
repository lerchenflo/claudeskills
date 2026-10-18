# claudeskills

Claude Code skills, shared publicly. The owner uses this repo to keep the skills on all devices
(desktop and laptop) in sync, and anyone is welcome to use them.

## First launch: run `claude-setup`

On a new device, or on the first launch after cloning, run the `claude-setup` skill before
anything else. It:

- shows which skills version (commit) the device runs and the latest one on GitHub, and updates
  itself first if GitHub is newer;
- on the first setup, asks once at which percentage of the 5-hour usage limit Claude should
  stop on its own. Claude never ignores this stop by itself: before a long-running task (night,
  unattended or autonomous work) it asks whether the stop should be ignored;
- sets up Claude Code (global `CLAUDE.md`, status line, model, plugins);
- installs all skills from this repo into `~/.claude/skills/` and adds a hook that keeps them up
  to date.

macOS, Linux and Windows (Git Bash):

```bash
git clone https://github.com/lerchenflo/claudeskills.git ~/.claude/skills-repo
mkdir -p ~/.claude/skills
cp -R ~/.claude/skills-repo/claude/claude-setup ~/.claude/skills/
```

Then start Claude Code and run `/claude-setup`.

`claude-setup` applies the owner's personal preferences. If you only want some skills, copy them
as described below instead. If you use it with a fork, set `CLAUDE_SKILLS_REPO_URL` to your fork.

## Using single skills

Skills are grouped into folders here, but Claude Code expects them flat. Copy a skill folder
(`<group>/<skill>/`) to `~/.claude/skills/<skill>/` to use it everywhere, or to
`<project>/.claude/skills/<skill>/` to use it in one project.

## How the sync works

- `claude-setup` installs a `SessionStart` hook that runs `claude/claude-setup/update-skills.sh`.
  At most every 6 hours it pulls this repo into `~/.claude/skills-repo` and installs new or
  changed skills into `~/.claude/skills/`.
- A local skill is only replaced when it still equals the last synced version. Local edits are
  never overwritten; the hook reports them as conflicts and Claude merges both versions.
- When Claude changes a skill on a device, it copies the skill into its group folder here,
  commits and pushes, so the other devices get it on their next check.
- Project-specific skills (named after or only useful for one project) do not belong here. They
  live in that project's `.claude/skills/`.

## Skills

### claude - Claude Code itself

| Skill | What it does |
|-------|--------------|
| `claude-setup` | Sets up Claude Code on a device: global `CLAUDE.md`, status line (context, 5h and weekly limits), model, effort, plugins, skill sync with GitHub, and the auto-update hook. Run it first on every new device. |
| `caveman` | Compressed reply style that cuts output tokens but keeps full technical accuracy. Levels lite, full, ultra and wenyan variants. |
| `skill-creator` | Creates and improves skills, runs evals and benchmarks, and tunes skill descriptions so they trigger reliably. |

### general

| Skill | What it does |
|-------|--------------|
| `exam-question-generator` | Turns study material (slides, summaries, chapters) into applied multiple-choice exam questions, study-summary PDFs and an interactive HTML practice test. Built and calibrated for the course *Strukturierter Einstieg in die Programmierung*; it works for other courses, but its question style and folder layout target that course. |
| `security-review` | Systematic security code review (injection, XSS, authentication, authorization, cryptography) with confidence-based findings. |
| `test-driven-development` | Test-first workflow for features and bug fixes: write a failing test, then the code. |
| `vori-translator` | Translates and reviews Vorarlbergerisch (Vori dialect) string resources (`values-de-rAT/strings.xml`, website texts): fills missing keys, fixes typos, Standard-German leftovers and broken placeholders. |

### kmp-architecture - Kotlin Multiplatform / Compose app architecture

Based on skills by Philipp Lackner, changed a bit.

| Skill | What it does |
|-------|--------------|
| `android-project-init` | Wizard that bootstraps a fresh KMP / Compose Multiplatform project: dependencies, modules, navigation, networking, database, preferences, DI, error handling. |
| `android-module-structure` | Module layout, dependency rules and package organization: decides where new code lives. |
| `android-dependency-setup` | Version catalog (`libs.versions.toml`), KSP wiring and dependency bundles. |
| `android-presentation-mvi` | MVI presentation layer: State, Action, Event, ViewModel, Root/Screen composable split, UiText, SavedStateHandle. |
| `android-compose-ui` | Compose UI patterns: stability, recomposition, side effects, lazy lists, animations, previews, accessibility, design system. |
| `android-navigation` | Type-safe Navigation 3 for KMP: Route sealed interface, NavDisplay, NavBackStack, Navigator, nested backstacks. |
| `android-data-layer` | Data sources, repositories, DTOs, mappers, Room, Ktor HttpClient, token storage and offline-first. |
| `android-di-koin` | Koin modules per layer, ViewModel injection and `koinViewModel()`. |
| `android-error-handling` | Typed `Result<T, E>` wrapper, `DataError`, `EmptyResult` and helpers (`map`, `onSuccess`, `onFailure`). |
| `android-testing` | ViewModel and Compose UI tests with JUnit5, Turbine, AssertK and fakes. Only used when tests are asked for. |

### android - Android tooling, migrations and Play Store

| Skill | What it does |
|-------|--------------|
| `agp-9-upgrade` | Migrates an Android project (not KMP) to Android Gradle Plugin 9. |
| `android-cli` | Installs and uses the `android` CLI: create projects, run apps, manage emulators and SDK components, look up docs. |
| `android-profiler` | Records and analyzes Perfetto traces, heap dumps and method recordings for jank, memory leaks and slow startup. |
| `appfunctions` | Exposes app workflows as AppFunctions so AI agents and system shortcuts can run them without opening the app. |
| `edge-to-edge` | Migrates a Compose app to edge-to-edge and fixes insets, IME and system bar problems. |
| `migrate-xml-views-to-jetpack-compose` | Step-by-step migration of an XML View to Jetpack Compose. |
| `navigation-3` | Installs or migrates to Jetpack Navigation 3: deep links, multiple backstacks, scenes, conditional navigation, results. |
| `play-billing-library-version-upgrade` | Upgrades the Google Play Billing Library to the latest stable version. |
| `play-policy-insights` | Audits an Android app against Google Play policies (permissions, accounts, data safety) and writes a compliance report. |
| `r8-analyzer` | Finds redundant or too broad R8 / ProGuard keep rules to make the app smaller. |
| `restore-credentials` | Implements Restore Credentials (`androidx.credentials`) for silent sign-in after a device restore. |

### mobile - cross-platform mobile apps

| Skill | What it does |
|-------|--------------|
| `kmp-crash-guard` | Hunts runtime crashes the compiler misses in KMP, Compose, Android and iOS code (duplicate lazy keys, `!!`, unsafe casts, platform-only crashes) and ranks them with fixes. |
| `mobile-ux-conventions` | Mobile UX rules from Material 3, Apple HIG and WCAG: dialog button order, destructive actions, touch targets, forms, loading and empty states, color, typography, motion. |
| `store-image-generator` | Captures emulator screens and builds App Store / Play Store screenshots with captions, store icons and the Play Store feature graphic. |

### spring-boot - Kotlin + Spring Boot + MongoDB backends

| Skill | What it does |
|-------|--------------|
| `spring-boot-project-init` | Wizard that adds a web server, JWT auth (register, login, refresh, logout) and a STOMP WebSocket to a fresh start.spring.io project. |
| `spring-boot-architecture` | House architecture: feature packages with Controller / Service / LookupService, one repository package, `core/` and `util/`. |
| `spring-delta-sync-endpoint` | Adds `/x/sync` delta-sync endpoints (timestamp diff or version watermark) with soft deletes for offline clients. |
| `spring-realtime-push` | Realtime updates and push notifications: WebSocket first, FCM and APNs fallback through one NotificationService. |
| `spring-endpoint-security-check` | Audits REST endpoints for missing auth, IDOR, input validation, injection, rate limiting and secret exposure. |

## Contributing

Anyone, human or AI agent, may open issues and pull requests: new skills, improvements, or fixes
for anything that is broken. Only the owner (@lerchenflo) merges; nobody else gets write access.

Forks are welcome, but they are meant to be merged back: open a pull request against this repo
so that all users profit from the changes.

A pull request is only merged when it explains itself:

- The commit messages and the pull request description say what was broken (or missing) and what
  was changed to fix it.
- If the change affects how something is used (a new skill, a new requirement, a changed
  command), the README is updated in the same pull request.

Rules for skills and scripts:

- One skill per folder: `<group>/<skill>/SKILL.md` with `name` and `description` frontmatter.
  Add every new skill to the list above.
- No project-specific skills, no secrets, tokens or personal data.
- Scripts must run on macOS, Linux and Windows (Git Bash). Line endings stay LF
  (`.gitattributes` enforces this).
- Skills that come from third parties keep their original license file.

## Credits

Some skills are sourced from Philipp Lackner and changed a bit (the `kmp-architecture` group).
