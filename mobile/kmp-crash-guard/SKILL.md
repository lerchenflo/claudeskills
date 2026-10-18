---
name: kmp-crash-guard
description: Hunts for runtime crashes that the Kotlin compiler does not catch, in Kotlin Multiplatform, Compose Multiplatform, Jetpack Compose and Android projects. It covers duplicate or unsaveable LazyColumn/LazyRow/LazyGrid/Pager keys, `!!` and unsafe `as` casts, first()/[0]/getValue() on empty collections, toInt()/parse/decode on bad input, coerceIn with inverted bounds, Modifier weight/padding values that throw, uncaught coroutine exceptions, Ktor and serialization failures, Room constraint and migration crashes, back-stack underflow, and platform-only crashes. The platform crashes include expect/actual implementations that diverge (TODO stubs, null on iOS vs. a throw on Android, context holders that were never initialized), Android runtime permissions and API-level or targetSdk behaviour (SecurityException, PendingIntent flags, removeLast() on API < 35, exact alarms, foreground-service types, FileProvider), and iOS/iPad crashes (missing Info.plist usage strings, share sheets or action sheets without a popover anchor on iPad, orientation mismatch, Split View sizes, keyWindow null, Kotlin exceptions crossing into Swift without @Throws). The result is a ranked findings table with file:line, the concrete input that triggers each crash and a suggested fix, and edits happen only after the user agrees. Use it whenever the user asks for a crash check, crash audit, stability pass, "can this crash", "find NPEs", "check for !!", "duplicate key exception", "Key was already used", "IllegalArgumentException", "NoSuchElementException", "does this work on iPad", "permission crash", "check the actuals", "older Android versions", a pre-release or pre-merge safety pass, or reports an app that "closes itself" or "crashes sometimes". Also use it proactively after writing a new screen that has a list, parses input, or calls the network, even if the user doesn't say "crash".
---

# KMP / Compose crash guard

Compile-clean Kotlin still crashes in production. The compiler can't see that a server sent two
rows with the same id, that a list was empty on first launch, or that a user typed "12,5" into a
number field. This skill finds those places, proves that each one is reachable, and reports them
ranked, with the input that triggers the crash.

The scan script only finds candidates. The real work is **deciding which ones can actually
happen**, which means tracing where the value comes from. A report that lists 40 `!!` without
tracing any of them is noise, and the user will stop reading it. Five proven crashes, each with a
concrete trigger, is much more useful.

## Workflow

1. **Scope.** Take whatever the user named: a file, a feature, a diff (`git diff main...HEAD`) or
   the whole repo. With no scope, scan the whole repo but trace the UI and data layers first,
   since that's where crashes reach users.
2. **Collect candidates** by running the bundled scanner from the project root:
   ```bash
   bash ~/.claude/skills/kmp-crash-guard/scripts/scan.sh [path ...]
   ```
   It prints grep hits grouped by category and skips `build/`, generated code and test sources.
   It's a fast first pass, not the whole search. Some categories can't be grepped (see step 4).
3. **Triage each hit** with `references/crash-catalog.md` (common code) and
   `references/platform-crashes.md` (expect/actual, Android, iOS/iPad), which gives the exact exception, what
   triggers it and the fix for each pattern. Read the catalog section for a category before
   judging hits in it, because many cases look safe and aren't. For example, `items(key = { it.id })`
   looks fine until you notice that the list is `local + remote`.
4. **Hunt what grep can't see.** Read the scoped screens and ViewModels and go through the
   edge-case sweep below. Most of the worst crashes (merged lists, empty first launch, double
   taps) only show up when you read the code.
5. **Prove reachability.** For every surviving candidate, trace where the value comes from (server
   JSON, DB row, user input, nav argument, platform API) and write down the concrete trigger,
   e.g. "the server returns an event with `shift = null`" or "the user deletes the last entry and
   then presses back". If you can show the value is guaranteed, drop the candidate or list it
   under *Checked, safe*. If you can't decide, mark it **Possible** and say what would settle it.
6. **Report** in the format below, then ask whether to fix. Don't edit code before the user
   agrees. Crash fixes change behaviour (what shows up instead of the crash), and that is the
   user's decision.
7. **When fixing:** apply the smallest fix that keeps the intended behaviour, and match the local
   error-handling style (the existing Result/snackbar/log helper) instead of adding a new one.
   Compile after the edits. Say which fixes are only compile-checked and not runtime-tested.

## Edge-case sweep (step 4)

For each screen or flow in scope, ask these questions. Each one maps to a catalog section.

- **Empty:** first launch, empty DB, server returns `[]`, a filter hides everything, a search has
  no hits. Does anything call `first()`, `[0]`, `max()`, `random()` or `reduce`, or compute
  `pageCount - 1`?
- **One element / boundaries:** the last item is deleted, the index equals `size`, a range has
  `from > to`, `coerceIn(min, max)` gets `min > max` (for example when the container is smaller
  than the content).
- **Duplicates:** lists merged from two sources, pagination that overlaps, optimistic insert plus
  a server echo, headers and items sharing one key space, several unsaved items using a
  placeholder id such as 0 or -1, a date or name used as a key.
- **Null from outside:** a JSON field that is nullable in practice but typed non-null, a Room
  single-row query for a row that doesn't exist, Android APIs that return platform types
  (intent extras, `getSystemService`, clipboard, `packageManager`).
- **Bad input:** a number with a comma or spaces, empty text, a huge value that overflows `Int`, a
  date like Feb 30, an unknown enum value from a newer server version.
- **Timing:** a double tap that navigates twice or pops twice, an action after the screen has
  left, a coroutine finishing after the list changed (a stale index), a flow collected while the
  DB is migrating.
- **Lifecycle:** process death with `rememberSaveable` holding a non-saveable or huge object
  (Android only), no app installed to handle an Intent.
- **expect/actual:** read every `actual` side by side with its siblings. Is one of them still a
  `TODO()`? Does one return null where another throws? Does an Android actual read a context
  holder that only the Activity initializes, even though the process can start from a push, an
  alarm or a worker? Does an iOS actual call UIKit off Main?
- **Android versions and permissions:** read `minSdk`/`targetSdk`. For each API newer than
  minSdk, is there a version gate? For each permission-guarded call, is there a check right
  before the call, and is the denied or revoked case handled? Are targetSdk behaviour changes
  (PendingIntent flags, receiver export flags, FGS types, exact alarms) respected?
- **iOS / iPad:** Info.plist has a usage string for every permission-using feature. The share
  sheet and action sheets have a popover anchor (they crash on iPad otherwise). The orientation
  plist matches the code. Layout survives Split View widths. No `keyWindow!!`. Every
  Swift-called API has `@Throws`. Check `TARGETED_DEVICE_FAMILY` to know whether iPad ships at
  all.

## Severity

- **Crash-likely:** reachable by normal use or ordinary data (empty list, second tap, common
  server shape). Fix before release.
- **Crash-possible:** needs unusual but real data or timing (server bug, a race, a rare
  locale). Worth hardening.
- **Hardening:** crashing is currently impossible, but only because of an assumption made
  somewhere else. Mention it briefly and don't pad the report with these.

## Output format

```
## Crash guard: <scope>

| # | Severity | Platform | Where | Exception | Trigger (concrete) | Fix |
|---|----------|----------|-------|-----------|--------------------|-----|
| 1 | Crash-likely | all | `path/File.kt:123` | IllegalArgumentException: Key "5" was already used | Server returns the same event in "mine" and "all", and the lists are concatenated | `distinctBy { it.id }` before `items`, or prefix the keys per section |

### Details
<only for findings whose fix or trigger needs more than one table row: short code snippet of the fix>

### Checked, safe
<one line each: pattern + why it can't crash (e.g. "`EventsScreen.kt:206` key = id - ids are the Room primary key, single source")>

### Not covered
<anything you could not verify: e.g. server contract unknown, iOS code not in scope>
```

Rank by severity first, then by how easy the trigger is. Keep *Checked, safe* short. It's there
so the user knows those spots were looked at, not to fill space.

End with one question asking whether to apply the fixes, and name which findings you would fix.

## References

| When | Read |
|---|---|
| Triage common-code categories (scanner sections 1-16), or before calling a candidate safe | `references/crash-catalog.md` |
| expect/actual, Android permissions / API level / targetSdk, iOS and iPad, manifest and plist checks (scanner sections 17-20). **Read this whenever the project has `androidMain`/`iosMain` or an `iosApp`** | `references/platform-crashes.md` |
| Candidate search | `scripts/scan.sh` (run it; read it only to extend the patterns) |
