---
name: spring-delta-sync-endpoint
description: How to add a /x/sync delta-sync endpoint to a Kotlin + Spring Boot + MongoDB backend so offline-capable clients can pull missed updates and deletions — two shapes, the simple id/timestamp-list diff and the race-safe version-watermark (monotonic counter) sync. Use whenever adding a sync endpoint, implementing delta/incremental sync, offline catch-up, soft delete for synced entities, or paginated sync responses. Trigger on phrases like "sync endpoint", "/sync", "delta sync", "incremental sync", "IdTimeStamp", "since version", "watermark", "offline sync", "client cache reconciliation". Builds on spring-boot-architecture; if the project has a local sync skill, read it for the concrete class names.
---

# Delta-sync endpoint (`/x/sync`)

Clients keep a local cache and call `/x/sync` on app start / reconnect to get what changed and what
was deleted while they were offline. Realtime push (see `spring-realtime-push`) covers the online
case; sync is the safety net, so it must be correct even when push isn't.

Templates for both shapes: `examples/sync-endpoint.md`.

## Prerequisite: soft delete

Synced entities never hard-delete: `deleted: Boolean = false` (+ `deletedAt`, `updatedAt`). A
hard-deleted row can't be reported back as a deletion, so clients would keep it forever. Hard-delete
only from a cleanup job, long after every client could have synced.

## Pick a shape

| | A — id/timestamp diff | B — version watermark |
|---|---|---|
| Request | `POST` body `List<IdTimeStamp{id, timeStamp}>` (everything the client has) + `page`, `page_size` | `GET ?since=<lastVersion>&page_size=` |
| Server work | Load all visible rows, diff against client map | `find(version > since && version <= safeWatermark).sort(version).limit(pageSize)` |
| Deletions | Client ids missing on server (page 0 only) | Rows with `deleted=true` and `version > since` |
| Payload cost | O(client cache) every call | O(changes) |
| Concurrency | Rows can shift between pages under concurrent writes (self-heals next sync) | Race-safe if versions come from an atomic counter + in-flight tracking |
| Use for | Small, low-write collections (users, groups, settings) | High-write collections (messages, events, logs) |

Default to **A** for small collections, **B** for anything that grows unbounded or is written often.

## Rules (both shapes)

1. `requireAuth()` first; the query must be scoped to what the **requester** may see (own
   friends/groups/memberships computed server-side) — never trust ids the client sends to decide
   visibility. In shape A the client list only selects *what's new for them*, not *what they may see*.
2. Validate pagination params (`page >= 0`, `1 <= page_size <= max`) and `since >= 0`.
3. Response always: `XSyncResponse(updatedEntries: List<XResponse>, deletedEntries: List<String>, moreEntries: Boolean)`
   (shape B adds `latestVersion: Long` for the client's next cursor).
4. Reuse one shared `IdTimeStamp` class across features — don't redefine per feature.
5. Sync reads go through `XLookupService` (owner of the repository) — see `spring-boot-architecture`.

## Shape A specifics

- `toAdd` = server rows whose id the client lacks; `toUpdate` = rows with `updatedAt` > client
  timestamp. Merge, sort newest-first, page with `drop(page*size).take(size)`.
- `deletedEntries` only on page 0 (client known set minus server visible set) — otherwise every page
  would repeat them.
- Losing visibility (left the group, unfriended) must also show up as a deletion, which the diff
  gives you for free because the row drops out of the visible set.

## Shape B specifics

- One monotonic counter document per synced collection (`counters` collection, atomic
  `findAndModify` `$inc`, `upsert=true`). Stamp `version` on **every** write, including soft deletes.
- A version can be allocated before the document is persisted. Track allocated-but-unwritten
  versions in memory and bound queries by `safeWatermark` (highest version with nothing in flight
  below it) — never by the raw counter, or a slow writer's row is skipped forever.
- Index `{ visibilityKey: 1, version: 1 }` for the scoped range query.
- Newly gained visibility (user added to a group) must replay older rows the cursor already passed —
  store e.g. `joinedAtVersion` on the membership and send full history for those scopes.
- `moreEntries = results.size == pageSize`; client loops with `since = latestVersion` until false.

## Related

- Scaffolding the feature: `spring-boot-architecture`
- Live updates while online: `spring-realtime-push`
- Audit the endpoint: `spring-endpoint-security-check`
