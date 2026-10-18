# Crash catalog (common code)

Each entry lists the **pattern**, the **exception** it throws, the usual **trigger** and a
**fix**. "Looks safe but isn't" notes are the ones most worth reading. Platform-specific crashes
(expect/actual, Android permissions and API levels, iOS/iPad) are in `platform-crashes.md`.

## Contents
1. Lazy lists, grids and pagers: keys
2. Null: `!!`, `as`, lateinit, platform types
3. Empty collections and missing keys
4. Index and range
5. Parsing and conversion of external input
6. Arithmetic
7. Range arguments
8. Compose layout and text arguments that throw
9. Saved state and navigation
10. Coroutines and error handling
11. Network and serialization
12. Room / database
13. Explicit throws and DI

---

## 1. Lazy lists, grids and pagers: keys

**Exception:** `IllegalArgumentException: Key "X" was already used. If you are using LazyColumn/Row please make sure you provide a unique key for each item.`
This applies to `LazyColumn`, `LazyRow`, `LazyVerticalGrid`, the staggered grids and
`HorizontalPager`/`VerticalPager` with `key`.

Keys have to be unique **across the whole lazy scope**: every `item`, `items` and `stickyHeader`
block in one `LazyColumn { }`, not just within one `items()` call.

Looks safe but isn't:
- `items(list, key = { it.id })` where `list = local + remote`, `cached + fresh`, `page1 + page2`
  (overlapping pagination), or an optimistic insert followed by the server echo. The same id
  appears twice. **Fix:** `distinctBy { it.id }` at the point where the lists are merged (in the
  ViewModel, not in the composable), or prefix keys per source.
- Two `items()` blocks in one scope, both keyed by `it.id`, where the ids come from different
  tables (event 5 and shift 5). **Fix:** `key = { "event-${it.id}" }`.
- `stickyHeader(key = date)` together with `items(key = { it.date })`: header and item collide.
  Also, one header key per group only stays unique if the grouping really is unique. `groupBy` is
  fine, but a manual "new header when the date changes" loop over unsorted data produces the same
  header twice.
- An item is shown in two sections (e.g. "Today" and "My events") with the same key. **Fix:**
  add a section prefix.
- Unsaved or placeholder items that all have `id = 0`, `-1` or `""` (a Room autoGenerate id before
  insert, or a local draft). **Fix:** use a temporary UUID key, or a key built from
  `"draft-$index"`.
- A key taken from a field that isn't unique: `name`, `date`, `title`, `timestamp` (two rows in
  the same millisecond), `hashCode()` (collisions are possible).
- Keying by index (`key = { index }`) doesn't crash, but it defeats keys. `itemsIndexed` without
  a key is fine.
- Server data: never assume the backend guarantees uniqueness unless the DB primary key enforces
  it. If the list comes from JSON, `distinctBy` is cheap insurance.

**Android-only exception:** `IllegalArgumentException: Type of the key X is not supported. On Android you can only use types which can be stored inside the Bundle.`
Keys must be Bundle-saveable on Android: primitives, String, enums, Parcelable, or
java.io.Serializable (Pair/Triple of those work). A plain `data class` key from `commonMain`
works on iOS and **crashes only on Android**. Types from other libraries (for example
kotlinx-datetime `LocalDate`) are only saveable if they implement Serializable in the version you
use, so check before trusting them. `.toString()` is always safe. **Fix:** key by
`id`/`toString()`.

`contentType` never crashes. A wrong one only costs performance.

## 2. Null: `!!`, `as`, lateinit, platform types

**`!!` → `NullPointerException`** (on K/N it's a `NullPointerException` too, and it terminates
the app). For each `!!`, trace where the value comes from:
- A value that was just checked on the previous line (`if (x != null) x!!.foo`) is safe but is a
  smell. A `var` property can change between the check and the use (another coroutine, a
  recomposition). Prefer `x?.let {}` or a local `val`.
- `map[key]!!`: the key is missing after a delete, a filter or a race. Use `getOrElse`/`?:` with
  a fallback.
- `state.selectedItem!!` in a composable: crashes for one frame when the state resets (e.g. back
  navigation clears the selection before the screen leaves the composition). This is very common.
  Guard with `?: return`.
- `savedStateHandle.get<T>("x")!!` or a nav argument `!!`: process death or a deep link without
  the argument.
- `response.body!!`, `json["field"]!!`: server contract.
- `.firstOrNull { }!!`: this is `first {}` with a worse message.

**Unsafe `as` → `ClassCastException`**: `as Int` on a JSON number that came back as Long or
Double, `as String` on `Any?` that is null (that's an NPE), casting `LocalContext.current as
Activity` (it can be a `ContextWrapper`, e.g. inside a Dialog or with Hilt). Fix: `as?` with a
fallback. For the Activity case, walk `ContextWrapper.baseContext` until you reach the Activity.

**`lateinit` → `UninitializedPropertyAccessException`**: initialized in `init()`, `onCreate`,
`setup()` or a platform entry point that doesn't always run first. Check with `::x.isInitialized`,
or make it nullable or a constructor parameter. See platform-crashes.md §1 for the case where a
context holder is initialized from an Activity.

**Platform types (`String!`)** from Java/Android APIs: `intent.getStringExtra()`,
`getSystemService()`, `clipboard.primaryClip`, `packageManager.getLaunchIntentForPackage()`,
`cursor.getString()`. Kotlin lets you assign these to non-null types, and the NPE then happens at
the assignment. Treat them as nullable.

## 3. Empty collections and missing keys

| Call | Exception on empty / missing | Safe alternative |
|---|---|---|
| `first()`, `last()`, `first { }` | `NoSuchElementException` | `firstOrNull()` |
| `single()` | `NoSuchElementException` / `IllegalArgumentException` (more than one) | `singleOrNull()` |
| `max()`, `min()`, `maxBy {}`, `maxOf {}` | `NoSuchElementException` | `maxOrNull()`, `maxOfOrNull {}` |
| `reduce {}` | `UnsupportedOperationException` | `fold(initial) {}` |
| `random()` | `NoSuchElementException` | `randomOrNull()` |
| `map.getValue(k)` | `NoSuchElementException` | `map[k] ?: fallback` |
| `list.removeFirst()`/`removeLast()` | `NoSuchElementException` (and see platform-crashes.md for API < 35) | `removeFirstOrNull()` |
| `Flow.first()` | `NoSuchElementException` if the flow completes empty | `firstOrNull()` |
| `iterator.next()` | `NoSuchElementException` | `hasNext()` |
| `list.component1()` / destructuring `val (a, b) = list` | `IndexOutOfBoundsException` | size check |

Trigger checklist: first app launch, empty DB, filter or search that hides everything, the user
deletes the last item, the server returns `[]`, all items are in the past, a week with no shifts.

## 4. Index and range

`IndexOutOfBoundsException` / `StringIndexOutOfBoundsException`:
- `list[0]`, `list[list.size - 1]` (crashes on empty), `list[index]` where `index` was captured in
  a lambda before the list shrank. This happens with `onClick = { vm.delete(index) }` followed by
  a fast second tap, or a coroutine that finishes after a refresh. Pass the **id**, not the index.
- `str.split(" ")[1]`, `split(":")[1]` when there's no separator (a time without a minute part,
  a name without a space). Use `getOrNull(1)`.
- `substring(0, 10)` on a shorter string → `take(10)`. `substring(indexOf(x))` when `indexOf`
  returns -1.
- `subList(a, b)` with `b > size` or `a > b`, e.g. `subList(0, 3)` when there are only 2 items.
  Use `take(3)`.
- `chunked(n)` / `windowed(n)` with n ≤ 0 → `IllegalArgumentException`.
- `entries[ordinal]` from stored data after an enum entry was removed.
- `Pager` page → list index mapping when `pageCount` changes while the page is visible.

## 5. Parsing and conversion of external input

"External" means user input, server JSON, stored prefs/DB from an **older app version**, QR/NFC,
deep links and clipboard.

| Call | Throws | Classic trigger |
|---|---|---|
| `"x".toInt()`/`toLong()` | `NumberFormatException` | `""`, `" 5"`, `"5.0"`, `"1,5"`, a value > Int.MAX |
| `"12,5".toDouble()` | `NumberFormatException` | **Decimal comma**: German, Austrian and most EU locales type `,`. Normalize with `replace(',', '.')` and use `toDoubleOrNull()` |
| `LocalDate.parse` / `Instant.parse` / `LocalTime.parse` | `DateTimeFormatException` / `IllegalArgumentException` | missing zero padding (`2026-9-1`), a time without seconds, an ISO string without an offset passed to `Instant.parse`, a server change to its date format |
| `LocalDate(y, m, d)` | `IllegalArgumentException` | Feb 29 in a non-leap year, day 31 in a 30-day month (e.g. "same day next month") |
| `Month(n)`, `DayOfWeek(n)` | `IllegalArgumentException` | 0-based vs 1-based mixups |
| `Enum.valueOf(s)` / `enumValueOf` | `IllegalArgumentException` | the server adds a new status, or the stored name is from an older build |
| `Json.decodeFromString<T>` | `SerializationException` | persisted JSON (prefs/DataStore/DB) written by an older app version whose model has since changed. **This crashes on app update, never on a fresh install.** |
| `Regex(userInput)` | `PatternSyntaxException` | the user searches for `(` or `*`. Use `Regex.escape` |
| `Color.parseColor` / hex parsing | `IllegalArgumentException` | a server-provided color like `"red"`, `"#FFF"`, or `""` |
| `x.roundToInt()` / `roundToLong()` | `IllegalArgumentException: Cannot round NaN value.` | `0f / 0f` (e.g. a progress calculation with total = 0) |
| `Long.toInt()`, `Double.toInt()` | no throw, but silent overflow or truncation | ids and epoch millis stored in an Int |

## 6. Arithmetic

- Int or Long `/ 0` and `% 0` → `ArithmeticException`. Typical sources: averages (`sum / count`),
  percentages (`done * 100 / total`), per-day rates (`total / days`), a grid column count
  (`width / itemWidth`).
- Float or Double `/ 0` doesn't throw. It produces `Infinity` or `NaN`, which then crashes further
  down: `roundToInt()` on NaN, `Modifier.fillMaxWidth(NaN)`, `LinearProgressIndicator(progress =
  NaN)`, Canvas sizes, `weight(NaN)`. Trace float results into Compose APIs.
- Duration math: `hours = minutes / 60` is fine, but `x / (end - start)` crashes when
  `end == start`.

## 7. Range arguments

- `coerceIn(min, max)` with `min > max` → `IllegalArgumentException: Cannot coerce value to an
  empty range`. Trigger: `coerceIn(0, list.size - 1)` on an empty list (max = -1), or
  `coerceIn(minWidth, availableWidth)` when the screen or container is smaller than the minimum
  (split screen, landscape keyboard, iPad Slide Over). **Fix:** `coerceIn(0, maxOf(0, size - 1))`.
- `coerceAtLeast`/`coerceAtMost` never throw.
- `a..b step n` with n ≤ 0 → `IllegalArgumentException`. `(a..b)` with a > b is empty but not a
  crash.
- `Slider(steps = n)` with n < 0 → `IllegalArgumentException`. Trigger: `steps = (max - min) - 1`
  when max == min. `valueRange` with start > end also misbehaves or throws.
- `Random.nextInt(from, until)` with `until <= from` → `IllegalArgumentException`.

## 8. Compose layout and text arguments that throw

| Call | Exception | Trigger |
|---|---|---|
| `Modifier.weight(w)` | `IllegalArgumentException: invalid weight ...; must be greater than zero` | `weight(count.toFloat())` with count 0, `weight(fraction)` with fraction 0 or NaN |
| `Modifier.padding(x)` | `IllegalArgumentException: Padding must be non-negative` | computed padding `(available - content) / 2` when content > available |
| `size/width/height/requiredSize(x)` with a negative value | `IllegalArgumentException` in Constraints | same computed-size pattern |
| `Text(maxLines = n)` / `minLines` | `IllegalArgumentException: both minLines and maxLines must be greater than zero` | `maxLines = if (expanded) Int.MAX_VALUE else collapsedLines` with collapsedLines 0 |
| `listState.scrollToItem(i)` / `animateScrollToItem(i)` | `IllegalArgumentException: Index should be non-negative` | **`indexOfFirst { }` returns -1** when the target isn't in the list (filtered, not loaded yet). Out-of-range positive indexes are clamped and don't crash |
| `pagerState.scrollToPage` | clamped, but crashes if pageCount is 0 in some versions | an empty pager |
| `Brush.linearGradient(colors)` / `horizontalGradient` | `IllegalArgumentException` (needs at least 2 colors) | a color list built from data with one entry |
| `AnnotatedString.Builder.addStyle(style, start, end)` / `SpanStyle` ranges | `IllegalArgumentException` | highlighting a search match using an index from a different string (lowercased or trimmed) or -1 from `indexOf` |
| LazyColumn inside `verticalScroll` (same direction) | `IllegalStateException: Vertically scrollable component was measured with an infinity maximum height constraints` | nested scrolling containers. Horizontal-in-vertical is fine. Also a LazyColumn inside a Column with `verticalScroll` in a *parent* composable in another file, so check the call sites |
| `Canvas`/`drawArc` with NaN sweep | no crash on some platforms, a native crash on others | percentage with total 0 |
| `rememberSaveable { mutableStateOf(nonSaveable) }` | see §9 | |
| `SubcomposeLayout`/`BoxWithConstraints` measuring a child twice | `IllegalStateException: measure() may not be called multiple times on the same Measurable` | custom layouts |
| Reading `LocalX.current` for a CompositionLocal with no default (`compositionLocalOf { error(...) }`) | `IllegalStateException` | the composable is used in a preview, dialog or new screen that isn't wrapped in the provider |

## 9. Saved state and navigation

- `rememberSaveable` with a type that isn't saveable (a data class that isn't Parcelable, a
  LocalDate, a list of custom objects) → **Android only**: `IllegalArgumentException: MutableState
  containing X cannot be saved using the current SaveableStateRegistry`. It fails on the first
  save (backgrounding the app or rotating the device), not on the first composition, so it's easy
  to miss in testing. **Fix:** a custom `Saver`, or save only the id.
- Big saved state (a whole list in rememberSaveable or SavedStateHandle, or a Bitmap) →
  `TransactionTooLargeException` when the app is backgrounded (Android, ~1 MB limit per
  transaction, shared).
- Navigation 3: `backStack.removeLast()` on a stack with one entry, then `NavDisplay` with an
  empty back stack → `IllegalArgumentException`/`NoSuchElementException`. Trigger: a double tap on
  a back or close button, a back gesture plus a button pop, or a `LaunchedEffect` that pops after
  saving while the user also pressed back. **Fix:** `if (backStack.size > 1) backStack.removeLastOrNull()`.
- Nav3 `rememberNavBackStack` keys have to be `@Serializable` NavKeys → runtime error otherwise.
- Nav2 type-safe routes: argument types without a NavType → runtime `IllegalArgumentException`.
  `popBackStack()` to a route that isn't in the stack returns false, which is fine, but
  `getBackStackEntry(route)` throws.
- Double navigation (a double tap pushes the same screen twice) doesn't crash by itself, but it
  does if the screen assumes a single instance (a duplicate key in a list of back-stack entries,
  or Koin scoped ViewModels).

## 10. Coroutines and error handling

- An exception inside `viewModelScope.launch {}` / `scope.launch {}` without a try/catch or
  handler reaches the thread's uncaught handler → **app crash** on Android and iOS. Every launch
  that calls the network, the DB, parsing or file IO needs a try/catch (or `runCatching`) inside,
  or a `CoroutineExceptionHandler` on the scope. `async {}` exceptions surface at `await()`, and
  cancel the parent scope unless it's a supervisor.
- `catch (e: Exception)` / `runCatching` **also catches `CancellationException`**. That isn't a
  crash, but it produces zombie coroutines: loops that keep running after the screen closes and
  then crash writing to dead state. Rethrow: `catch (e: CancellationException) { throw e }` first.
- `catch (e: IOException)` for network errors: **the Ktor Darwin engine on iOS throws
  `DarwinHttpRequestException`, which is not an IOException**. Neither are
  `HttpRequestTimeoutException` or `UnresolvedAddressException`. A catch that works on Android
  then crashes on iOS in airplane mode. Catch `Exception` (rethrowing cancellation) at the
  network boundary.
- `stateIn`/`shareIn`: an exception upstream cancels the scope (it crashes via the scope's
  handler). Put `.catch {}` before `stateIn`.
- `Channel.send` after `close()` → `ClosedSendChannelException`. `Mutex.unlock()` when it isn't
  locked → `IllegalStateException`. Use `withLock`.
- `withTimeout` throws `TimeoutCancellationException`, a CancellationException subclass. If it
  isn't caught it silently cancels the parent, and if it's caught by a generic handler it's
  swallowed. Use `withTimeoutOrNull`.
- `runBlocking` on the main thread → ANR on Android, and a watchdog kill on iOS (0x8badf00d).
- `GlobalScope.launch`: nothing catches it, and it outlives the screen.
- Writing Compose `SnapshotStateList`/`mutableStateListOf` from several background threads at
  the same time → `ConcurrentModificationException` / snapshot apply failures. Mutate on Main or
  through a `MutableStateFlow.update {}`.
- Modifying a `MutableList` while iterating over it (`forEach { list.remove(it) }`) →
  `ConcurrentModificationException` on the JVM. On K/N it's undefined behaviour instead. Use
  `removeAll {}`.

## 11. Network and serialization

- The `Json` config decides a lot. Find the `Json { }` instance used by Ktor
  ContentNegotiation:
  - Without `ignoreUnknownKeys = true`, **any new server field crashes old app versions**
    (`SerializationException: Encountered an unknown key`).
  - A field that is non-null in Kotlin and `null` in JSON → `JsonDecodingException` (unless it has
    a default and `coerceInputValues = true`).
  - A required field (no default) that's missing → `MissingFieldException`.
  - An unknown enum value → `SerializationException`. Fix: `coerceInputValues = true` plus a
    default, or a custom serializer with an `UNKNOWN` entry.
  - A number where a string was expected, or `"5"` where an int was expected: with
    `isLenient = false` both throw.
- `response.body<T>()` when the server returned an error page (HTML 500, 502 from nginx, a captive
  portal login page on hotel wifi) → `JsonConvertException`/`NoTransformationFoundException`.
  Check `status.isSuccess()` before `body()`, or use `expectSuccess = true` together with a
  handler.
- A `body<List<T>>()` where the server sometimes returns `{"error": ...}` instead.
- Empty body (204) decoded as T → exception.
- A cookie or session expiring mid-flow (redirect to the login HTML) → the same body-decoding
  crash.
- Big responses decoded on Main → ANR/jank, not a crash, unless the payload is huge.

## 12. Room / database

- `@Insert` (default `OnConflictStrategy.ABORT`) on an existing primary key or unique index →
  `SQLiteConstraintException`. Trigger: a re-sync inserts rows that already exist, or a double tap
  on save. Use `@Upsert` or `REPLACE` deliberately (note that REPLACE deletes and re-inserts,
  which cascades to foreign-key children!).
- A foreign-key violation (inserting a child before its parent, or deleting a parent with
  `RESTRICT`) → `SQLiteConstraintException`.
- A single-row `@Query` returning a **non-null** type when no row matches → crash
  (`IllegalStateException: The query result was empty` on newer Room codegen, NPE on older).
  Make the return type nullable.
- A non-suspend, non-Flow DAO call on the main thread → `IllegalStateException: Cannot access
  database on the main thread` (Android).
- The schema version was bumped without a migration → `IllegalStateException: A migration from X
  to Y was required but not found`. A migration whose SQL doesn't match the generated schema →
  `IllegalStateException: Migration didn't properly handle`. This **only shows on an upgrade
  install**, never on a fresh one. Check that every version step has a migration and that it's
  registered with `addMigrations`.
- `fallbackToDestructiveMigration` doesn't crash, but it deletes user data. Report it if the
  project cares (see its CLAUDE.md).
- Cursor/row mapping: a column that's `NOT NULL` in SQL but nullable in the entity, or the
  reverse after a migration → NPE on read.
- Large `IN (:ids)` lists over 999 params on old SQLite → `SQLiteException: too many SQL variables`.

## 13. Explicit throws and DI

- `TODO()` → `NotImplementedError`. `error("...")`, `require`, `check`, `throw` in `when` branches
  that were "impossible" until someone added a new enum value, route or server status. Decide
  whether each one is reachable from UI or data.
- `else -> throw IllegalStateException("unknown type")` in a mapper for server data: the server
  adds a type and old apps crash. Map it to UNKNOWN instead.
- Koin: `koinViewModel<T>()` / `get<T>()` / `koinInject()` for a type with no definition, or
  missing a parameter → `NoDefinitionFoundException`/`NoParameterFoundException` at runtime, only
  when that screen opens. Check each injected type against the modules (`module { }`), including
  platform modules (`expect val platformModule`): a definition that exists only in
  `androidMain`'s module crashes on iOS. Koin `verify()` in a test catches this.
- Koin `single` created before its dependency is ready (e.g. a DB builder that needs a platform
  context from an Android actual that isn't initialized yet).
