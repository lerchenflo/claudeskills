# WebSocket connection (STOMP)

STOMP over WebSocket at `/ws`. STOMP gives the socket the same shape as the REST side: clients
`SEND` to a destination, and Spring routes it to an annotated method — `@MessageMapping` is the
socket's `@RequestMapping`. No hand-written `when (type)` dispatch, no `_class` envelope, no
session registry: Spring keeps the sessions, serializes concurrent sends, and handles heartbeats.

| REST | STOMP |
|---|---|
| `@RestController` + `@RequestMapping("/x")` | `@Controller` + `@MessageMapping("x.action")` |
| `@Valid @RequestBody body: Req` | `@Valid @Payload body: Req` |
| `requireAuth()` | `principal.userId()` (method param `principal: Principal`) |
| return value = response | return value + `@SendToUser("/queue/x")` = reply to the sending session |
| `GlobalExceptionHandler` (`@ExceptionHandler`) | `SocketExceptionHandler` (`@MessageExceptionHandler` → `/user/queue/errors`) |
| server push: — | `SimpMessagingTemplate.convertAndSendToUser(userId, "/queue/x", payload)` |

Destination conventions used below:
- `/app/**` — client → server, routed to `@MessageMapping` (the prefix is stripped: `SEND /app/ping`
  → `@MessageMapping("ping")`).
- `/user/queue/**` — server → one user (all their sessions). Client subscribes to
  `/user/queue/x`; server sends with `convertAndSendToUser(userId, "/queue/x", ...)`.
- `/topic/**` — server → every subscriber. Only server code may send here (enforced in §4).

## Contents
1. Dependencies + SecurityConfig change
2. notifications/websocket/SocketDestinations.kt
3. notifications/websocket/WebSocketConfig.kt
4. notifications/websocket/StompAuthInterceptor.kt — CONNECT auth + destination rules
5. notifications/websocket/PrincipalExt.kt — `principal.userId()`
6. notifications/websocket/SocketPublisher.kt — server push + presence
7. core/SocketExceptionHandler.kt
8. core/PingSocketController.kt — first `@MessageMapping`, verifies the setup
9. Adding socket endpoints to a feature
10. Without Security
11. Client contract
12. Testing

Resulting files:

```
<base>/
  core/                       SocketExceptionHandler, PingSocketController
  notifications/websocket/    WebSocketConfig, StompAuthInterceptor, SocketDestinations,
                              PrincipalExt, SocketPublisher
```

## 1. Dependencies + SecurityConfig change

```kotlin
implementation("org.springframework.boot:spring-boot-starter-websocket")   // includes spring-messaging
```

With Security, add `/ws` to the `permitAll` list in `SecurityConfig`:

```kotlin
// STOMP authenticates in the CONNECT frame (StompAuthInterceptor), not on the HTTP handshake:
// browsers can't set headers on the handshake. A handshake that does carry a valid Bearer token
// is still picked up. Nothing can be sent or subscribed before an authenticated CONNECT.
.requestMatchers("/ws").permitAll()
```

## 2. notifications/websocket/SocketDestinations.kt

All destination strings in one place, shared by controllers, the interceptor and the publisher.

```kotlin
package <base>.notifications.websocket

object SocketDestinations {
    const val ENDPOINT = "/ws"
    const val APP_PREFIX = "/app"
    const val USER_PREFIX = "/user"
    const val QUEUE_PREFIX = "/queue"
    const val TOPIC_PREFIX = "/topic"

    // Per-user queues (server sends to "/queue/x", client subscribes to "/user/queue/x")
    const val ERRORS = "/queue/errors"
    const val PONG = "/queue/pong"

    /**
     * Broadcast topics any logged-in user may subscribe to. Topics scoped to a resource (e.g. one
     * group's channel) must NOT go here - authorize them in StompAuthInterceptor.canSubscribe.
     */
    val PUBLIC_TOPICS: Set<String> = setOf(
        // "$TOPIC_PREFIX/announcements",
    )
}
```

## 3. notifications/websocket/WebSocketConfig.kt

```kotlin
package <base>.notifications.websocket

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.messaging.simp.config.ChannelRegistration
import org.springframework.messaging.simp.config.MessageBrokerRegistry
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker
import org.springframework.web.socket.config.annotation.StompEndpointRegistry
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer
import org.springframework.web.socket.config.annotation.WebSocketTransportRegistration

@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig(
    private val stompAuthInterceptor: StompAuthInterceptor,
) : WebSocketMessageBrokerConfigurer {

    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint(SocketDestinations.ENDPOINT)
        // Default origin policy: same-origin browsers + clients without an Origin header (native apps).
        // Browser frontend on another origin: .setAllowedOriginPatterns("https://app.example.com")
    }

    override fun configureMessageBroker(registry: MessageBrokerRegistry) {
        registry.setApplicationDestinationPrefixes(SocketDestinations.APP_PREFIX)
        registry.setUserDestinationPrefix(SocketDestinations.USER_PREFIX)
        registry.enableSimpleBroker(SocketDestinations.QUEUE_PREFIX, SocketDestinations.TOPIC_PREFIX)
            // Server and client heartbeat every 10 s. A peer that vanished (radio off, app
            // suspended) never sends a close frame; missing heartbeats are how the broker notices
            // and drops the session, which also fires SessionDisconnectEvent for presence.
            .setHeartbeatValue(longArrayOf(10_000, 10_000))
            .setTaskScheduler(stompHeartbeatScheduler())
    }

    override fun configureClientInboundChannel(registration: ChannelRegistration) {
        registration.interceptors(stompAuthInterceptor)
    }

    override fun configureWebSocketTransport(registry: WebSocketTransportRegistration) {
        registry
            .setMessageSizeLimit(64 * 1024)            // largest inbound frame
            .setSendTimeLimit(10_000)                   // one send blocking longer -> peer stopped reading
            .setSendBufferSizeLimit(512 * 1024)         // outbound backlog before the session is cut off
    }

    // Note: once a TaskScheduler bean exists, Boot no longer creates its own, so @Scheduled jobs
    // also run on this pool - hence 2 threads, not 1.
    @Bean
    fun stompHeartbeatScheduler(): ThreadPoolTaskScheduler = ThreadPoolTaskScheduler().apply {
        poolSize = 2
        setThreadNamePrefix("stomp-heartbeat-")
    }
}
```

Single instance only: the simple broker keeps subscriptions in memory. Before running several
instances, switch `enableSimpleBroker` to `enableStompBrokerRelay` (RabbitMQ/ActiveMQ) — the
controllers and the publisher stay unchanged.

## 4. notifications/websocket/StompAuthInterceptor.kt

Runs on every inbound frame. Three jobs:
1. **CONNECT** — authenticate. Uses the handshake principal if the upgrade request carried a valid
   Bearer token, else the `Authorization` header of the CONNECT frame. The user set here is bound to
   the session; every later frame and every `@MessageMapping` call gets it as `Principal`.
2. **SEND** — only to `/app/**`. Without this a client could `SEND /topic/x` and the simple broker
   would deliver it to every subscriber, bypassing all server-side checks.
3. **SUBSCRIBE** — only own user queues and allowed topics. The simple broker lets anyone
   subscribe to anything otherwise.

```kotlin
package <base>.notifications.websocket

import <base>.core.security.JwtService
import org.springframework.messaging.Message
import org.springframework.messaging.MessageChannel
import org.springframework.messaging.MessageDeliveryException
import org.springframework.messaging.simp.stomp.StompCommand
import org.springframework.messaging.simp.stomp.StompHeaderAccessor
import org.springframework.messaging.support.ChannelInterceptor
import org.springframework.messaging.support.MessageHeaderAccessor
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.stereotype.Component

@Component
class StompAuthInterceptor(
    private val jwtService: JwtService,
) : ChannelInterceptor {

    override fun preSend(message: Message<*>, channel: MessageChannel): Message<*> {
        val accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor::class.java)
            ?: return message

        when (accessor.command) {
            StompCommand.CONNECT -> {
                if (accessor.user == null) {
                    val userId = accessor.getFirstNativeHeader("Authorization")
                        ?.let { jwtService.userIdFrom(it, JwtService.TokenType.ACCESS) }
                        // Thrown here -> client gets a STOMP ERROR frame and the socket is closed
                        ?: throw MessageDeliveryException("Not logged in")
                    // Same principal shape as JwtAuthFilter: name = userId hex string
                    accessor.user = UsernamePasswordAuthenticationToken(userId.toHexString(), null, emptyList())
                }
            }

            StompCommand.SEND -> {
                requireUser(accessor)
                val destination = accessor.destination.orEmpty()
                if (!destination.startsWith("${SocketDestinations.APP_PREFIX}/")) {
                    throw MessageDeliveryException("Clients may only send to ${SocketDestinations.APP_PREFIX}/**")
                }
            }

            StompCommand.SUBSCRIBE -> {
                requireUser(accessor)
                val destination = accessor.destination.orEmpty()
                if (!canSubscribe(accessor.user!!.name, destination)) {
                    throw MessageDeliveryException("Subscription to $destination not allowed")
                }
            }

            else -> Unit
        }
        return message
    }

    private fun requireUser(accessor: StompHeaderAccessor) {
        if (accessor.user == null) throw MessageDeliveryException("Not logged in")
    }

    /**
     * `/user/queue/...` is always safe: Spring resolves it to the subscriber's own session-scoped
     * queue, so a user can't read another user's queue through it. Resource topics
     * (e.g. "/topic/group.<id>") need a membership check here - inject the feature's LookupService.
     */
    private fun canSubscribe(userIdHex: String, destination: String): Boolean = when {
        destination.startsWith("${SocketDestinations.USER_PREFIX}${SocketDestinations.QUEUE_PREFIX}/") -> true
        destination in SocketDestinations.PUBLIC_TOPICS -> true
        else -> false
    }
}
```

Expiry: a session stays authenticated after its access token expires (like an open HTTP/2
stream). If that matters, store the token's expiry in the session attributes at CONNECT and reject
SEND frames after it; the client then reconnects with a refreshed token.

## 5. notifications/websocket/PrincipalExt.kt

`requireAuth()` reads `SecurityContextHolder`, which is empty on STOMP message threads. Socket
handlers take a `principal: Principal` parameter instead; this turns it into the userId.

```kotlin
package <base>.notifications.websocket

import org.bson.types.ObjectId
import org.springframework.http.HttpStatus
import org.springframework.web.server.ResponseStatusException
import java.security.Principal

/** The socket equivalent of requireAuth(). StompAuthInterceptor guarantees the principal exists. */
fun Principal.userId(): ObjectId =
    name.takeIf(ObjectId::isValid)?.let(::ObjectId)
        ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in")
```

## 6. notifications/websocket/SocketPublisher.kt

The one place server code pushes through. Features don't call it directly — they go through a
`NotificationService` (see `spring-realtime-push`), which uses `sendToUser`'s `false` to fall back
to push notifications.

Presence is tracked here from the session events rather than read from `SimpUserRegistry` inside
those events: the registry updates on the same events in no guaranteed order.

```kotlin
package <base>.notifications.websocket

import org.bson.types.ObjectId
import org.slf4j.LoggerFactory
import org.springframework.context.event.EventListener
import org.springframework.messaging.simp.SimpMessagingTemplate
import org.springframework.messaging.simp.stomp.StompHeaderAccessor
import org.springframework.stereotype.Component
import org.springframework.web.socket.messaging.SessionConnectedEvent
import org.springframework.web.socket.messaging.SessionDisconnectEvent
import java.util.concurrent.ConcurrentHashMap

@Component
class SocketPublisher(
    private val messagingTemplate: SimpMessagingTemplate,
) {
    private val logger = LoggerFactory.getLogger(SocketPublisher::class.java)

    /** userId hex -> open STOMP session ids. A user may be connected from several devices. */
    private val sessionsByUser = ConcurrentHashMap<String, MutableSet<String>>()

    fun isConnected(userId: ObjectId): Boolean = sessionsByUser.containsKey(userId.toHexString())

    /**
     * Sends [payload] to every session of [userId] on [destination] (e.g. "/queue/messages";
     * the client subscribes to "/user/queue/messages").
     * @return false if the user has no session -> caller falls back to push.
     */
    fun sendToUser(userId: ObjectId, destination: String, payload: Any): Boolean {
        if (!isConnected(userId)) return false
        messagingTemplate.convertAndSendToUser(userId.toHexString(), destination, payload)
        return true
    }

    /** To every subscriber of a "/topic/..." destination. */
    fun broadcast(destination: String, payload: Any) {
        messagingTemplate.convertAndSend(destination, payload)
    }

    @EventListener
    fun onConnected(event: SessionConnectedEvent) {
        val userId = event.user?.name ?: return
        val sessionId = StompHeaderAccessor.wrap(event.message).sessionId ?: return
        var cameOnline = false
        sessionsByUser.compute(userId) { _, sessions ->
            (sessions ?: ConcurrentHashMap.newKeySet()).also {
                cameOnline = it.isEmpty()
                it += sessionId
            }
        }
        if (cameOnline) {
            logger.debug("User $userId online")
            // First session of this user -> presence notification to friends etc. goes here
        }
    }

    /** May fire more than once per session (documented Spring behavior) - must stay idempotent. */
    @EventListener
    fun onDisconnected(event: SessionDisconnectEvent) {
        val userId = event.user?.name ?: return
        var wentOffline = false
        sessionsByUser.computeIfPresent(userId) { _, sessions ->
            val removed = sessions.remove(event.sessionId)
            if (sessions.isEmpty()) {
                wentOffline = removed
                null   // drops the map entry
            } else sessions
        }
        if (wentOffline) {
            logger.debug("User $userId offline")
            // Last session closed -> lastSeen update / presence notification goes here
        }
    }
}
```

Cycle warning: once presence hooks call a `NotificationService` that itself injects
`SocketPublisher`, break it with `@Lazy` on the parameter here, with a comment naming the cycle.

## 7. core/SocketExceptionHandler.kt

The `GlobalExceptionHandler` of the socket side. An exception in a `@MessageMapping` method lands
here and the error goes back to the sending session only, on `/user/queue/errors` — the session
stays open.

```kotlin
package <base>.core

import <base>.notifications.websocket.SocketDestinations
import org.slf4j.LoggerFactory
import org.springframework.messaging.converter.MessageConversionException
import org.springframework.messaging.handler.annotation.MessageExceptionHandler
import org.springframework.messaging.handler.annotation.support.MethodArgumentNotValidException
import org.springframework.messaging.simp.annotation.SendToUser
import org.springframework.web.bind.annotation.ControllerAdvice
import org.springframework.web.server.ResponseStatusException

@ControllerAdvice
class SocketExceptionHandler {
    private val logger = LoggerFactory.getLogger(SocketExceptionHandler::class.java)

    data class SocketError(val error: String, val details: List<String> = emptyList())

    // @Valid @Payload failed (note: the messaging MethodArgumentNotValidException, not the MVC one)
    @MessageExceptionHandler(MethodArgumentNotValidException::class)
    @SendToUser(SocketDestinations.ERRORS, broadcast = false)
    fun handleValidation(e: MethodArgumentNotValidException) = SocketError(
        error = "Invalid payload",
        details = e.bindingResult?.allErrors?.map { it.defaultMessage ?: "Invalid value" }.orEmpty(),
    )

    // Malformed JSON / wrong types
    @MessageExceptionHandler(MessageConversionException::class)
    @SendToUser(SocketDestinations.ERRORS, broadcast = false)
    fun handleConversion(e: MessageConversionException) = SocketError("Invalid message body")

    @MessageExceptionHandler(IllegalArgumentException::class)
    @SendToUser(SocketDestinations.ERRORS, broadcast = false)
    fun handleIllegalArgument(e: IllegalArgumentException) = SocketError(e.message ?: "Invalid request")

    @MessageExceptionHandler(ResponseStatusException::class)
    @SendToUser(SocketDestinations.ERRORS, broadcast = false)
    fun handleStatus(e: ResponseStatusException) = SocketError(e.reason ?: e.statusCode.toString())

    @MessageExceptionHandler(Exception::class)
    @SendToUser(SocketDestinations.ERRORS, broadcast = false)
    fun handleAny(e: Exception): SocketError {
        logger.error("Unhandled socket error: ${e.javaClass.simpleName}", e)
        return SocketError("An unexpected error occurred")
    }
}
```

## 8. core/PingSocketController.kt

Smallest round trip: routing, payload validation, principal, reply to sender.

```kotlin
package <base>.core

import <base>.notifications.websocket.SocketDestinations
import <base>.notifications.websocket.userId
import jakarta.validation.Valid
import jakarta.validation.constraints.Size
import org.springframework.messaging.handler.annotation.MessageMapping
import org.springframework.messaging.handler.annotation.Payload
import org.springframework.messaging.simp.annotation.SendToUser
import org.springframework.stereotype.Controller
import java.security.Principal
import java.time.Instant

@Controller
class PingSocketController {

    data class PingRequest(
        @field:Size(max = 100) val note: String? = null,
    )

    data class Pong(val userId: String, val note: String?, val serverTime: Instant)

    // Client: SEND /app/ping {"note":"hi"}  ->  receives on /user/queue/pong
    @MessageMapping("ping")
    @SendToUser(SocketDestinations.PONG, broadcast = false)
    fun ping(@Valid @Payload request: PingRequest, principal: Principal): Pong =
        Pong(principal.userId().toHexString(), request.note, Instant.now())
}
```

## 9. Adding socket endpoints to a feature

Same layering as REST (`spring-boot-architecture`): a thin `<Feature>SocketController` in the
feature package, business logic and authorization in the feature's Service.

```kotlin
@Controller
class LocationSocketController(
    private val locationService: LocationService,
) {
    data class LocationUpdateRequest(
        @field:DecimalMin("-90.0") @field:DecimalMax("90.0") val lat: Double,
        @field:DecimalMin("-180.0") @field:DecimalMax("180.0") val long: Double,
    )

    // Client: SEND /app/location.update {"lat":47.4,"long":9.7}
    // No @SendToUser: fire-and-forget. The service pushes results via NotificationService.
    @MessageMapping("location.update")
    fun update(@Valid @Payload body: LocationUpdateRequest, principal: Principal) {
        locationService.updateLocation(principal.userId(), body.lat, body.long)
    }
}
```

Rules:
- Name destinations `<feature>.<action>`; keep one `@Controller` per feature for its socket routes.
- Always act as `principal.userId()` — never trust a user id inside the payload.
- Need a reply to the sender only? Return a value + `@SendToUser("/queue/<feature>", broadcast = false)`.
  Need to reach other users? Call the service, which notifies via `NotificationService` →
  `SocketPublisher.sendToUser`.
- Resource-scoped broadcast topics need a `canSubscribe` check in `StompAuthInterceptor`.

## 10. Without Security

- Skip the CONNECT branch and the `requireUser` calls in `StompAuthInterceptor`; keep the SEND and
  SUBSCRIBE destination rules (the "/topic" bypass exists without auth too).
- No user identity → no `/user/...` delivery via `convertAndSendToUser`, no presence. Drop
  `PrincipalExt.kt` and the presence part of `SocketPublisher`; keep `broadcast`.
- `@SendToUser(..., broadcast = false)` still works: Spring falls back to the session id.

## 11. Client contract

1. Open `ws://<host>/ws`.
2. `CONNECT` with headers `accept-version:1.2`, `heart-beat:10000,10000`,
   `Authorization:Bearer <accessToken>`.
3. `SUBSCRIBE` to `/user/queue/errors` first, then whatever the app needs (`/user/queue/...`).
4. `SEND` to `/app/<route>` with `content-type:application/json`.
5. On an `ERROR` frame / close: refresh the access token if it expired, reconnect, resubscribe.

Libraries: KMP → Krossbow (`krossbow-stomp-core` + `krossbow-websocket-ktor`); JS →
`@stomp/stompjs` (`connectHeaders: { Authorization: "Bearer ..." }`).

## 12. Testing

Fastest end-to-end check is a Spring Boot test with `WebSocketStompClient` (random port):
connect with a JWT from `JwtService.generateAccessToken`, subscribe to `/user/queue/pong`, send
`/app/ping`, assert the reply. Also assert the negatives: CONNECT without token fails, `SEND
/topic/x` and `SUBSCRIBE /topic/x` are rejected.
