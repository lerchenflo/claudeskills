---
name: spring-realtime-push
description: How to wire realtime updates and push notifications in a Kotlin + Spring Boot backend — STOMP destinations or a sealed raw-WebSocket message type, plus one NotificationService that fans out WebSocket first and falls back to FCM (Firebase) and APNs push when the recipient is offline. Use whenever adding a new socket message type, a new push notification, a notifyX method, or setting up WebSocket + push delivery in a Spring Boot project. Trigger on phrases like "websocket message", "socket message type", "push notification", "FCM", "APNs", "Firebase push", "NotificationService", "realtime update", "live update", "broadcast to clients". Builds on spring-boot-architecture; if the project has a local realtime skill, read it for the concrete subtypes and method names.
---

# Realtime updates + push fallback

Delivery is two-tier: the live WebSocket connection first; if the recipient has none, push via
**both** FCM and APNs (a device may have registered either token type). One class orchestrates
this: `notifications/NotificationService`.

Templates: `examples/notification-wiring.md`.

## Transport

| Project uses | Socket layer | NotificationService calls |
|---|---|---|
| **STOMP** (new projects, set up by `spring-boot-project-init`) | `SocketPublisher` + `@MessageMapping` controllers; one destination per event type (`/queue/<feature>`) instead of a `_class` envelope | `socketPublisher.sendToUser(userId, "/queue/x", dto)` / `broadcast("/topic/x", dto)` / `isConnected(userId)` |
| **Raw WebSocket** (existing projects) | `SocketConnectionHandler` + sealed `SocketConnectionMessage` — template in `examples/raw-websocket-handler.md` | `socketConnectionHandler.sendMessage(msg, receiverId)` / `broadcast(msg, excludeUserId)` / `isConnected(userId)` |

Same contract either way: the targeted send returns `false` when the user has no session → push
fallback. Below, "socket handler" means whichever of the two the project has; rule 2 (register each
subtype twice) only applies to the raw transport.

## Package layout

```
notifications/
  NotificationService.kt           the ONLY entry point for features
  websocket/
    ...                            transport-specific, see "Transport" below
  firebase/FirebaseService.kt      FCM send, token cleanup on UNREGISTERED
  firebase/model/FirebaseToken.kt
  apns/ApnsService.kt              APNs (Pushy) send
  apns/model/ApnsToken.kt
```

Token repositories go in `repository/` like every other repository, owned by a lookup per
`spring-boot-architecture`.

## Rules

1. **Only `NotificationService`** calls the socket layer (`SocketPublisher` / `SocketConnectionHandler`),
   `FirebaseService.*`, `ApnsService.*`. Feature services inject `NotificationService`, nothing
   lower.
2. **Every socket subtype is registered twice in the same change**: the `data class` in the sealed
   interface AND a `@JsonSubTypes.Type(..., name = "xchange")` entry. Discriminator property
   `"_class"`, lowercase names. Missing one breaks serialization at runtime, not compile time.
3. Socket payloads carry `*Response` DTOs, never entities.
4. Call `notifyX(...)` **after** the write is persisted, so a client that refetches on receipt sees
   the new state.
5. Keep `FirebaseService` and `ApnsService` method signatures parallel — `NotificationService` calls
   them as a pair.
6. Push payloads: minimal, no secrets, no other users' private fields. Remove invalid tokens on
   provider errors (`UNREGISTERED`, `INVALID_ARGUMENT`, `SENDER_ID_MISMATCH`, APNs `BadDeviceToken`).

## Pick a delivery shape

| Shape | When | Push fallback |
|---|---|---|
| **Targeted** | Known recipients (DM receiver, group members minus actor) | Yes — when the targeted send returns `false` |
| **Broadcast** | Everyone connected should see it (shared map, global feed) | No — offline clients catch up via `/x/sync` |
| **Offline-only side notification** | Live state already covered by another socket message (e.g. reactions ride on the message change) | Only if `!isConnected(recipient)` |

## Cycle warning

The socket layer often needs a service (presence, location, admin events) that itself
calls `NotificationService` → socket layer. That's an infrastructure cycle: break it
with `@Lazy` on the handler's constructor parameter plus a comment naming the cycle. Don't let
feature services take part in it — they only see `NotificationService`.

## Scaling note

In-memory sessions are lost on restart and don't work across multiple instances. Before horizontal
scaling: STOMP → `enableStompBrokerRelay` (RabbitMQ/ActiveMQ); raw → a shared broker (Redis
pub/sub) behind `SocketConnectionHandler`.

## Related

- Feature scaffolding: `spring-boot-architecture`
- Offline catch-up: `spring-delta-sync-endpoint`
