# The Five Lenses — Full Checklists

Ask all five at every hop. Each item below explains *why* it matters, not just what to grep for —
use the reasoning to spot the same shape somewhere the examples don't cover, since new flows won't
look exactly like the old ones. Project-specific anchors (which locks exist, known gaps with
`file:line`) belong in the project's own add-on skill; read it alongside this file.

## 1. Crash / unhandled exception

A crash is the worst outcome for a hop that's supposed to be "fire and forget" (a socket frame
handler, a sync job) because one bad message shouldn't take down everything after it.

- Force operators: `!!` and unchecked casts. `val poll = m.poll!!` is safe *only* when the message
  type was already switched on (`MessageType.POLL`) right above it; the same `!!` anywhere without
  that type-narrowing guard is a live crash waiting for a null column.
- Server: every `ObjectId(id)` (or other parse of a client-supplied id) must be validated first
  (`require(isValidObjectId(id))`) — otherwise a malformed id string throws an unhandled exception
  before the global exception handler gets a clean shot at it. Check what exception type actually
  surfaces for a bad hop — only specific exception types have a registered `@ExceptionHandler`;
  anything else becomes a raw 500.
- `catch (e: Exception)` blocks in coroutines: do they call `ensureActive()` /
  `currentCoroutineContext().ensureActive()` (or rethrow `CancellationException`) before treating
  the exception as a normal failure? Without it, cancelling the surrounding scope (e.g. leaving the
  screen) gets silently absorbed as "job failed" instead of propagating as cancellation.
- A socket message handler that wraps its whole `when` in one try/catch is good — one malformed
  frame can't kill the socket loop — but check that a *new* branch doesn't call something further
  down (a suspend network call, a force unwrap) whose exception type that catch doesn't anticipate.
- A bare `CoroutineScope(...).launch { }` — one not built from `viewModelScope`, an application
  scope, or another scope with a `SupervisorJob`/`CoroutineExceptionHandler` attached — has no owner
  to catch what it throws. Downscaling a picked image this way means a corrupt or undecodable image
  crashes the whole app, not just the image-picking flow. Any fire-and-forget coroutine that isn't
  anchored to a supervised scope is the same risk.

## 2. Races & concurrency

A codebase usually already has locks for the flows that need them — a new flow that writes the same
rows without joining (or explicitly deciding it doesn't need) that discipline is the tell.

- Find the project's locks first: typically a `Mutex` around sending messages, one around the full
  data sync, one around token refresh, one around the socket connect. If the traced flow mutates
  state one of these already guards, ask whether it goes through the existing lock or opens a
  second uncoordinated path to the same data.
- Reference shapes worth matching: an offline-queue sender that waits for the interactive sender
  (`while (sendLock.isLocked) delay(...)`) instead of hard-blocking it; a second sync caller that
  awaits the first run instead of starting a duplicate; concurrent 401-triggered refreshes deduped
  to one network call with a `Mutex` plus an in-flight `Deferred`.
- Check-then-act around a lock: `if (lock.isLocked) { lock.withLock {}; return }` followed by a
  separate `lock.withLock { ... }` lets two near-simultaneous callers both observe `isLocked ==
  false` and both run the full job back-to-back. The `Mutex` still serializes them, so nothing
  corrupts, but the second one doesn't reuse the first's result. Don't use this shape where the
  duplicate run is expensive or user-visible — prefer `tryLock` or a "just finished" flag checked
  inside the lock.
- Server-side optimistic locking: a load-then-save on a `@Version`-annotated document must go
  through a retry helper (e.g. `withOptimisticRetry`). One that doesn't throws
  `OptimisticLockingFailureException` under concurrent writers instead of retrying.
- Client-side parallel-job interference: when a sync launches several jobs concurrently via
  `async` (users, messages, groups, ...), ask what one job can insert that another job in the same
  batch deletes. The reference fix is re-applying the deletions after `awaitAll` (e.g. purging rows
  of groups the user just left, which a parallel message job may have re-inserted).
- Double-submit from the UI: can the button/action that starts this flow fire twice before the
  first call's state update (loading flag, disabled state) takes effect?
- Ordering between socket and sync: a socket-delivered change and a `/sync` response for the same
  row can arrive in either order. A push must not advance the sync cursor (keep the stored
  `version = existing?.version ?: 0L`), and "whichever arrives last wins" is not automatically safe.
- Version-watermark sync cursors: atomically allocating a version (Mongo `findAndModify`) is not
  enough — the document carrying it can still be mid-write when a sync request runs. Track
  allocated versions as in-flight until the write commits, and bound sync queries by the highest
  version *guaranteed committed* (a safe watermark), not the current counter. A cursor that
  returns success before checking its version in reintroduces the skip-on-concurrent-write race.
  See `spring-delta-sync-endpoint`.

## 3. Network failure / offline / retry

The happy path is easy; a flow's stability is decided by what happens on every *other* branch.

- Walk every network error subtype the traced call can return — no internet, timeout,
  unauthorized, forbidden, conflict, too many requests, payload too large, serialization,
  unknown — and check whether the caller branches on them or treats every error the same.
  Collapsing "offline" and "server rejected this permanently" into one bucket is a common source of
  retry loops that can never succeed, or one-shot failures that should have retried.
- If the call fails, does it leave a durable trace an offline-retry sweep will pick back up, or
  does the user's input silently vanish? A message write that only updates in-memory state and
  never lands a `sent = false` row in the local database is lost the moment the process dies.
- Token refresh must distinguish *retryable* (offline / rate-limited / 5xx — try again later, keep
  the session) from *invalidated* (the server rejected the refresh token — the session is gone). A
  caller that treats both the same either logs the user out on a transient blip or keeps retrying a
  dead session forever.
- Socket reconnection: every exit path of the connect logic (`onError`, `onClose`, catch blocks)
  must reach the reconnect scheduling. A branch that returns or throws past it silently kills
  reconnection until the next app restart.
- Server push fallback: notifications try the WebSocket first and fall back to FCM/APNs only when
  the recipient is not connected. A new notification method that skips this fallback silently drops
  updates for offline recipients — fine only for data the sync endpoints also cover. See
  `spring-realtime-push`.
- **Head-of-line blocking in a serial retry queue.** A loop that always retries the first pending
  item and stops as soon as that item is unchanged after an attempt lets one item that can never
  succeed (oversized, undecodable, permanently rejected) block every other queued item, of any type,
  forever. If the pending query has no `ORDER BY`, "first" isn't even the oldest. Check that a
  permanently failing item can be skipped or marked failed, not just retried.
- **A branch that builds a fallback value but never uses it.** In Kotlin,
  `if (m.audioPath == null) { TextContent("Offline audio sending failed") }` that isn't the
  branch's last expression is never returned or assigned — the code falls straight through and
  builds the real content from a file that may not exist. When tracing a multi-branch fallback
  (missing image/audio/attachment), check that the "missing" branch actually short-circuits.
- **Sequential per-item fetches inside a "fetch all missing X" job.** Launching categories
  concurrently doesn't help if each category's downloader does `ids.forEach { fetch(it) }`, one
  round trip at a time, each bounded only by the full request timeout. After a long offline stretch
  the backlog can be dozens of items; with still-weak signal right when connectivity returns, the
  step stalls far longer than any single timeout suggests. Batch, or bound the concurrency.
- **A reconnect/resume trigger built on a `SharedFlow` can silently stop firing.** A
  `MutableSharedFlow<Unit>(extraBufferCapacity = 1)` with `replay = 0` drops an emission that has
  no active collector — `extraBufferCapacity` does not buffer for late subscribers. If a resume
  fires before the ViewModel's `init` has subscribed (plausible at cold start), it is lost with no
  re-trigger; the failure isn't a visible spinner, it's a *silently skipped* sync. Prefer seeding
  with `.onStart { emit(Unit) }` or driving off a `StateFlow`'s current value when a missed first
  event matters.

## 4. Data consistency / sync drift

- Every mutation a `/x/sync` endpoint depends on must bump the field the sync query compares
  against (usually `updatedAt` or a version counter) — a write that changes a document without
  touching that field is invisible to clients that sync afterward.
- Deletions need an explicit tombstone / deleted-ids path through sync (the response carries
  deleted entries as well as updated ones) — a resource that only syncs upserts leaves deleted rows
  stranded on clients that were offline when the delete happened.
- Local ids vs server ids: rows created offline are keyed by a local primary key before the server
  assigns a real `id`. The upsert path must reconcile the two (look up the existing row and keep
  its `localPK`) instead of creating a duplicate row when the server echo arrives.
- Socket-delivered and sync-delivered copies of the same entity must produce the *same* local
  shape — if one path sets a field the other leaves null/default, whichever arrives second silently
  regresses it.
- **Not every sync endpoint paginates the same way, and the difference matters under concurrent
  writes.** Paging by a monotonic version watermark is stable no matter what else changes
  mid-sync. Recomputing `sortedByDescending { updatedAt }.drop(start).take(pageSize)` on *every*
  page call is not: if any eligible row's `updatedAt` changes between two page fetches of the same
  client sync loop (plausible when several sync jobs run concurrently), the order shifts under the
  pagination and a row is skipped or returned twice. It self-heals on the next full sync, so it's a
  LOW/MEDIUM drift window, not data loss. Check which shape a new paginated endpoint follows.

## 5. Stuck UI states

A failure that's handled correctly but never reaches the screen is, from the user's perspective,
indistinguishable from a hang. For every failure branch identified under lenses 1–4, ask: **what
does the user see, and is there a way out that doesn't require restarting the app?**

- Is a loading/syncing flag cleared in a `finally` block, or only on the success path? Clearing it
  in `finally` is what stops a mid-run exception from stranding the spinner.
- An early return that bails out *before* the loading flag is set (e.g. `requireLoggedIn() ?:
  return` at the top) is safe — nothing was shown yet. The same early return *after* the flag was
  flipped true is the dangerous version, since nothing clears it.
- Does a failure ever reach a user-visible channel (an error channel collected by the UI, a
  snackbar), or does the code path only log it? A silently swallowed error reads as "nothing
  happened" — the user has no reason to retry and no idea it failed.
- A "finished with errors" state (e.g. `exitedWithErrors`) — is it surfaced somewhere the user can
  act on (retry button, error banner), or computed and never read?
- A disabled button/spinner whose re-enable depends on exactly one response type: if the request
  can fail in a way that never reaches that code (an exception before the `finally`, a cancelled
  coroutine that skips `.also { isSending = false }`), the control stays disabled until the screen
  is recreated.
- An "auth invalidated" event must actually be collected somewhere that navigates to the login
  screen; firing it into a channel nobody listens on leaves the user on a screen whose calls will
  401 forever.
