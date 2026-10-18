---
name: flow-stability
description: Traces one program flow end-to-end across a mobile client (Kotlin Multiplatform / Compose) AND its backend (Kotlin + Spring Boot) and reports where it can crash, race, get stuck, or drift out of sync — a findings table, no code edits. Use this whenever asked to check something's "stability", to trace a flow, or to reason about what happens under a bad network, a dropped socket, a backgrounded app, two users acting at once, or an offline-to-online transition. Trigger proactively on phrases like "is this stable", "will this break if...", "race condition", "trace the flow", "what happens when the connection drops / phone goes offline / user comes out of a tunnel", "stuck on loading/spinner", "messages not arriving", "duplicate message", "hangs", "deadlock", "sync issue", "out of sync", or any bug report shaped like "sometimes X doesn't happen" — even if the user doesn't name a specific file. Also use it as a pre-merge check after adding a new send/sync/socket/notification flow. If the project has its own flow-stability add-on skill (hop maps, known gaps), read it too. For endpoint auth/authorization only, prefer spring-endpoint-security-check instead.
---

# Tracing a client-server flow for stability

Most real bugs in a client-server app don't live inside one function — they live in the **seam
between two hops**: the server saves a message but the socket push never lands, the client marks a
send "in flight" and the app gets killed before the flag clears, two sync jobs race to write the
same row. A trace that stops at "the controller looks fine" or "the ViewModel looks fine" has not
actually answered the question. This skill's whole value is refusing to stop at the repo boundary.

## References

| Topic | File |
|---|---|
| Full per-lens checklists with the reasoning behind each item — **MUST read before tracing any hop** | `references/lens-checklists.md` |

If the project has its own add-on skill (for example `<project>-flow-stability` in the project's
`.claude/skills/`), read it as well: it names the project's real classes, its existing locks,
ready-made hop maps and known gaps with `file:line` anchors. Client and server often live in two
repos — find the other one (sibling folder, project CLAUDE.md) before tracing, and say so if it is
not available.

## How to use this

1. **Pin down the flow.** Restate it as a concrete sequence of hops before reading any lens.
   If the user names a bug symptom ("stuck on the sync spinner") instead of a flow, work backwards
   to the flow that produces that symptom.
2. **List every hop**, client and server, using the skeleton below as a starting template — adjust
   it, don't force-fit a flow that doesn't match. Check the project add-on for a ready-made hop map
   first so you're not rediscovering plumbing that's already mapped.
3. **At each hop**, run the five lenses — read `references/lens-checklists.md` for the full
   checklists. Not every lens applies to every hop — a pure UI hop has no database write, a pure
   database write has no recomposition — but check all five before moving to the next hop rather
   than picking your favorite one and stopping.
4. **Report** using the exact format in "Output format". Do not modify code — this is a diagnostic
   pass; the user decides what and when to fix.

## The hop skeleton

Written for the KMP + Spring Boot stack of the `kmp-architecture` and `spring-boot` skills; rename
the hops to the project's classes. Not every flow touches every hop, and some branch differently —
but this is the spine most client-initiated actions follow:

```
Compose UI (button / gesture)
  → ViewModel action handler
  → Repository method (often behind a Mutex - see lens 2)
  → safe-call helper → Ktor HttpClient (authenticated, token refresh on 401)
  → Controller (auth check) → Service → Mongo repository
  → NotificationService.notifyX() → WebSocket handler
      → recipient connected? push via WebSocket : fall back to FCM / APNs
  → client socket manager receives frame → socket message handler
  → Room DAO upsert/delete → Flow emission → Compose recomposition
```

Server-initiated flows (push-only, scheduled jobs) start partway down this chain. Pure sync flows
skip the socket/push section entirely and instead loop a `/x/sync` endpoint until the server says
there are no more entries.

## The five lenses (summary)

Full checklists in `references/lens-checklists.md` — these one-liners are only the index:

1. **Crash / unhandled exception** — `!!` without type-narrowing, unvalidated id parsing on the
   server, `catch (e: Exception)` that swallows cancellation, bare unsupervised
   `CoroutineScope(...).launch`.
2. **Races & concurrency** — the project's existing locks, check-then-act around a lock, server
   optimistic-locking retry, parallel sync-job interference, double-submit, socket-vs-sync
   ordering, version-watermark discipline.
3. **Network failure / offline / retry** — branch per error subtype, durable retry traces,
   retryable vs invalidated token refresh, reconnect paths, push fallback, head-of-line blocking,
   dead fallback branches, unbatched per-item fetches, zero-replay `SharedFlow` triggers.
4. **Data consistency / sync drift** — `updatedAt`/version bumps, deletion tombstones, local-id
   reconciliation, socket-vs-sync shape parity, watermark vs recomputed-sort pagination.
5. **Stuck UI states** — loading flags cleared in `finally`, errors reaching the user, "finished
   with errors" surfaced, re-enable paths on every failure branch, auth-invalidated events
   actually collected.

## Severity rubric

- **HIGH** — data loss, a permanently stuck UI state, or a crash reachable on a normal (not
  adversarial, not multi-user) path.
- **MEDIUM** — real issue, but needs a specific precondition to trigger: bad network, two users
  acting concurrently, app backgrounded/killed at the wrong instant, a specific error subtype.
- **LOW / NOTE** — defense-in-depth, inconsistency with how a sibling flow already handles the same
  situation, or a theoretical gap with no realistic trigger.

## Output format

Start with the numbered hop list you traced (this is what lets the user sanity-check you actually
followed the flow rather than guessing), then the findings:

```markdown
## Flow trace: <name of the flow>

1. Compose UI: ... (`file:line`)
2. ViewModel: ... (`file:line`)
3. ...

## Stability findings

| Severity | Hop (file:line) | Failure mode | How it triggers | Suggested fix |
|----------|------------------|--------------|------------------|----------------|
| HIGH | Repository.kt:120 | `m.poll!!` assumes poll is non-null | A poll-typed unsent row saved without its poll payload | Guard with a null check that falls back to a failed-send state instead of crashing |
```

If nothing turns up, write `No stability issues found against the checklist.` instead of an empty
table. Follow the table with a one-line count ("2 HIGH, 1 MEDIUM, 0 LOW"). Close with a short note
that these are advisory findings — this skill does not modify code.

## Related skills

- **`kmp-crash-guard`** — a deeper crash-only pass over client code (lens 1 in depth).
- **`spring-endpoint-security-check`** — auth/authorization (can user A touch user B's data); run
  it alongside this skill when the traced flow also touches sensitive data.
- **`spring-delta-sync-endpoint`** and **`spring-realtime-push`** — the intended shapes for sync
  endpoints and socket/push fan-out that lenses 2–4 check against.
