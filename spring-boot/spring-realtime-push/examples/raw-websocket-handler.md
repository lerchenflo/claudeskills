# Raw WebSocket handler (non-STOMP projects)

For projects that use a raw WebSocket at `/ws` with a JSON `_class` envelope instead of STOMP
(e.g. existing apps whose clients already speak this protocol). New projects get STOMP from
`spring-boot-project-init` (`examples/websocket.md`) — there `@MessageMapping` methods replace the
`when (parsed)` dispatch in `handleTextMessage` below.

## Contents
1. Dependencies + app class
2. notifications/websocket/model/SocketConnectionMessage.kt
3. notifications/websocket/model/SocketConnection.kt
4. notifications/websocket/AuthHandshakeInterceptor.kt (Security only)
5. notifications/websocket/WebSocketConfig.kt
6. notifications/websocket/SocketConnectionHandler.kt
7. Without Security
8. Testing the connection

## 1. Dependencies + app class

```kotlin
implementation("org.springframework.boot:spring-boot-starter-websocket")
```

Add `@EnableScheduling` to the application class — the keepalive sweep is a `@Scheduled` job and
silently never runs without it.

## 2. notifications/websocket/model/SocketConnectionMessage.kt

One JSON envelope for both directions, discriminated by `_class`. Every subtype is registered
twice in the same change (data class + `@JsonSubTypes` entry); a missing entry only fails at
runtime.

Jackson 3 (Boot 4) still uses the `com.fasterxml.jackson.annotation` package for annotations.

```kotlin
package <base>.notifications.websocket.model

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "_class")
@JsonSubTypes(
    JsonSubTypes.Type(value = SocketConnectionMessage.Connected::class, name = "connected"),
)
sealed interface SocketConnectionMessage {
    /** Server -> client right after the handshake; lets the client know the session is live. */
    data class Connected(val userId: String) : SocketConnectionMessage
}
```

## 3. notifications/websocket/model/SocketConnection.kt

```kotlin
package <base>.notifications.websocket.model

import org.bson.types.ObjectId
import org.springframework.web.socket.WebSocketSession
import java.time.Instant

data class SocketConnection(
    val sessionId: String,
    val userId: ObjectId,
    /** Always the ConcurrentWebSocketSessionDecorator, never the raw session. */
    val session: WebSocketSession,
    val startedAt: Instant = Instant.now(),
) {
    /** Last proof of life: the connect, or the latest pong to a keepalive ping. */
    @Volatile
    var lastPongAt: Instant = startedAt
}
```

## 4. notifications/websocket/AuthHandshakeInterceptor.kt (Security only)

The handshake is a normal HTTP GET, so it already went through `JwtAuthFilter` and
`SecurityConfig` (`anyRequest().authenticated()` rejects it with 401 before this runs). The
interceptor reads the userId from the `SecurityContextHolder` via `optionalAuth()` and stores it in
the session attributes — the socket handler runs on other threads later, where the security context
no longer exists.

```kotlin
package <base>.notifications.websocket

import <base>.core.security.optionalAuth
import org.springframework.http.HttpStatus
import org.springframework.http.server.ServerHttpRequest
import org.springframework.http.server.ServerHttpResponse
import org.springframework.stereotype.Component
import org.springframework.web.socket.WebSocketHandler
import org.springframework.web.socket.server.HandshakeInterceptor

@Component
class AuthHandshakeInterceptor : HandshakeInterceptor {
    companion object {
        const val USER_ID_ATTRIBUTE = "userId"
    }

    override fun beforeHandshake(
        request: ServerHttpRequest,
        response: ServerHttpResponse,
        wsHandler: WebSocketHandler,
        attributes: MutableMap<String, Any>,
    ): Boolean {
        // Defense in depth: SecurityConfig already requires auth for /ws. Refusing here, before the
        // upgrade, answers with a real 401 instead of opening a socket and closing it right away.
        val userId = optionalAuth() ?: run {
            response.setStatusCode(HttpStatus.UNAUTHORIZED)
            return false
        }
        attributes[USER_ID_ATTRIBUTE] = userId
        return true
    }

    override fun afterHandshake(
        request: ServerHttpRequest,
        response: ServerHttpResponse,
        wsHandler: WebSocketHandler,
        exception: Exception?,
    ) = Unit
}
```

Browsers can't set an `Authorization` header on `new WebSocket(...)`. Native/desktop clients
(OkHttp, Ktor, URLSession) can. For a browser client, add a short-lived single-use "ws ticket"
endpoint rather than putting the access token in the URL (URLs end up in proxy logs).

## 5. notifications/websocket/WebSocketConfig.kt

```kotlin
package <base>.notifications.websocket

import org.springframework.context.annotation.Configuration
import org.springframework.web.socket.config.annotation.EnableWebSocket
import org.springframework.web.socket.config.annotation.WebSocketConfigurer
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry

@Configuration
@EnableWebSocket
class WebSocketConfig(
    private val socketConnectionHandler: SocketConnectionHandler,
    private val authHandshakeInterceptor: AuthHandshakeInterceptor,
) : WebSocketConfigurer {
    override fun registerWebSocketHandlers(registry: WebSocketHandlerRegistry) {
        registry.addHandler(socketConnectionHandler, "/ws")
            .addInterceptors(authHandshakeInterceptor)
        // Default origin policy: same-origin browsers + clients that send no Origin (native apps).
        // Browser frontends on another origin: .setAllowedOriginPatterns("https://app.example.com")
    }
}
```

## 6. notifications/websocket/SocketConnectionHandler.kt

What it gets right, and why each piece is there:
- **Thread-safe sends.** Messages are sent from request threads, the keepalive job, etc.; Tomcat
  throws on overlapping writes to one session. `ConcurrentWebSocketSessionDecorator` serializes
  them and cuts off a peer that stopped reading.
- **Several sessions per user** (phone + desktop, or a stale session next to a fresh reconnect):
  `sendMessage` sends to all of them.
- **Dead-peer detection.** A peer that vanished (radio off, app suspended) never sends a close
  frame, and TCP keeps accepting writes for minutes — so sends "succeed" and the user looks online.
  The handler pings every 30 s and closes sessions without a pong for 75 s. Pong-based on purpose:
  Tomcat counts our own pings as activity, so an idle timeout would never fire.
- **Idempotent cleanup.** `unregister` runs from the close callback *and* from `closeDeadConnection`
  (a dead transport may never deliver the callback).

```kotlin
package <base>.notifications.websocket

import <base>.notifications.websocket.model.SocketConnection
import <base>.notifications.websocket.model.SocketConnectionMessage
import org.bson.types.ObjectId
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component
import org.springframework.web.socket.CloseStatus
import org.springframework.web.socket.PingMessage
import org.springframework.web.socket.PongMessage
import org.springframework.web.socket.TextMessage
import org.springframework.web.socket.WebSocketSession
import org.springframework.web.socket.handler.ConcurrentWebSocketSessionDecorator
import org.springframework.web.socket.handler.TextWebSocketHandler
// Boot 4 (Jackson 3). Boot 3: com.fasterxml.jackson.databind.ObjectMapper
import tools.jackson.databind.json.JsonMapper
import java.io.IOException
import java.time.Duration
import java.time.Instant
import java.util.concurrent.CopyOnWriteArrayList

@Component
class SocketConnectionHandler(
    // Spring's auto-configured mapper: same settings (Kotlin module, dates) as REST responses
    private val jsonMapper: JsonMapper,
) : TextWebSocketHandler() {

    companion object {
        const val PING_INTERVAL_MS = 30_000L
        /** 2.5 ping intervals: one lost pong is tolerated, two in a row are not. */
        private val PONG_TIMEOUT: Duration = Duration.ofMillis(PING_INTERVAL_MS * 5 / 2)
        /** A single send blocking longer than this means the peer stopped reading. */
        private const val SEND_TIME_LIMIT_MS = 10_000
        /** Outbound bytes allowed to queue behind a slow send before the session is cut off. */
        private const val SEND_BUFFER_LIMIT_BYTES = 512 * 1024
    }

    private val logger = LoggerFactory.getLogger(SocketConnectionHandler::class.java)
    private val connections = CopyOnWriteArrayList<SocketConnection>()

    fun isConnected(userId: ObjectId): Boolean = connections.any { it.userId == userId }

    /**
     * Sends to every live session of [receiverId].
     * @return true if at least one session accepted it; false = user offline -> caller falls back to push.
     */
    fun sendMessage(message: SocketConnectionMessage, receiverId: ObjectId): Boolean {
        val targets = connections.filter { it.userId == receiverId }
        if (targets.isEmpty()) return false
        val text = TextMessage(jsonMapper.writeValueAsString(message))
        var delivered = false
        for (connection in targets) {
            if (trySend(connection, text)) delivered = true
        }
        return delivered
    }

    fun broadcast(message: SocketConnectionMessage, excludeUserId: ObjectId? = null) {
        val text = TextMessage(jsonMapper.writeValueAsString(message))
        for (connection in connections) {
            if (connection.userId != excludeUserId) trySend(connection, text)
        }
    }

    override fun afterConnectionEstablished(session: WebSocketSession) {
        val userId = session.attributes[AuthHandshakeInterceptor.USER_ID_ATTRIBUTE] as? ObjectId
        if (userId == null) {
            // Only reachable if the interceptor was not registered - never accept an anonymous session
            session.close(CloseStatus.POLICY_VIOLATION)
            return
        }

        val connection = SocketConnection(
            sessionId = session.id,
            userId = userId,
            session = ConcurrentWebSocketSessionDecorator(session, SEND_TIME_LIMIT_MS, SEND_BUFFER_LIMIT_BYTES),
        )
        val wasOffline: Boolean
        synchronized(connections) {
            wasOffline = connections.none { it.userId == userId }
            connections += connection
        }

        trySend(connection, TextMessage(jsonMapper.writeValueAsString(SocketConnectionMessage.Connected(userId.toHexString()))))

        if (wasOffline) {
            // First session of this user -> they just came online (presence notifications go here)
        }
    }

    override fun handleTextMessage(session: WebSocketSession, message: TextMessage) {
        val senderId = connections.find { it.sessionId == session.id }?.userId ?: return
        val parsed = try {
            jsonMapper.readValue(message.payload, SocketConnectionMessage::class.java)
        } catch (e: Exception) {
            logger.warn("Unparseable socket message from user $senderId: ${e.message}")
            return
        }
        when (parsed) {
            // Route client -> server message types here. Treat payloads as untrusted input and
            // always act as senderId, never as an id the client put into the message.
            is SocketConnectionMessage.Connected -> logger.warn("Ignoring server-only message type from user $senderId")
        }
    }

    override fun handlePongMessage(session: WebSocketSession, message: PongMessage) {
        connections.find { it.sessionId == session.id }?.lastPongAt = Instant.now()
    }

    override fun handleTransportError(session: WebSocketSession, exception: Throwable) {
        // The container closes the session afterwards; afterConnectionClosed does the cleanup
        if (!exception.isPeerGone()) logger.warn("Socket transport error on ${session.id}: ${exception.describe()}")
    }

    override fun afterConnectionClosed(session: WebSocketSession, status: CloseStatus) {
        unregister(session.id)
    }

    @Scheduled(fixedDelay = PING_INTERVAL_MS)
    fun keepaliveSweep() {
        val now = Instant.now()
        for (connection in connections) {
            if (Duration.between(connection.lastPongAt, now) > PONG_TIMEOUT) {
                logger.info("Socket of user ${connection.userId} silent since ${connection.lastPongAt}, closing as dead")
                closeDeadConnection(connection)
                continue
            }
            try {
                connection.session.sendMessage(PingMessage())
            } catch (e: Exception) {
                if (!e.isPeerGone()) logger.warn("Ping to user ${connection.userId} failed: ${e.describe()}")
                closeDeadConnection(connection)
            }
        }
    }

    /** A failed send means the session is dead: close and unregister it. */
    private fun trySend(connection: SocketConnection, text: TextMessage): Boolean = try {
        connection.session.sendMessage(text)
        true
    } catch (e: Exception) {
        if (!e.isPeerGone()) logger.error("Send to user ${connection.userId} failed: ${e.describe()}")
        closeDeadConnection(connection)
        false
    }

    private fun closeDeadConnection(connection: SocketConnection) {
        try {
            connection.session.close(CloseStatus.SESSION_NOT_RELIABLE)
        } catch (e: Exception) {
            if (!e.isPeerGone()) logger.error("Closing dead socket of user ${connection.userId} failed: ${e.describe()}")
        }
        unregister(connection.sessionId)
    }

    /** Idempotent: unknown session -> no-op, so close callback and closeDeadConnection can both call it. */
    private fun unregister(sessionId: String) {
        val removed: SocketConnection?
        val nowOffline: Boolean
        synchronized(connections) {
            removed = connections.find { it.sessionId == sessionId }
            if (removed != null) connections.remove(removed)
            nowOffline = removed != null && connections.none { it.userId == removed.userId }
        }
        if (nowOffline) {
            // Last session of this user closed -> they just went offline (lastSeen / presence go here)
        }
    }

    /**
     * A vanished peer shows up as an IOException (dead TCP) or Tomcat's IllegalStateException
     * (send raced the close). Both are normal traffic, not server faults - don't log them as errors.
     */
    private fun Throwable.isPeerGone(): Boolean =
        generateSequence(this) { it.cause.takeIf { cause -> cause !== it } }
            .any { it is IOException || it is IllegalStateException }

    private fun Throwable.describe(): String = "${this::class.simpleName}: ${message ?: "no message"}"
}
```

Services that need presence or push from inside this handler usually also call into it
(`NotificationService` → handler → presence service → `NotificationService`). Break that cycle with
`@Lazy` on the handler's constructor parameter plus a comment naming the cycle.

Sessions live in memory: lost on restart, not shared across instances. Add a broker (Redis pub/sub)
before running more than one instance.

## 7. Without Security

No user identity exists, so sessions can only be broadcast to:

- Skip `AuthHandshakeInterceptor` and the `.addInterceptors(...)` call.
- `SocketConnection` without `userId`; in `afterConnectionEstablished` don't read the attribute,
  just register the session.
- Remove `sendMessage`, `isConnected`, the online/offline hooks, and `excludeUserId`
  (`broadcast(message)` to all). `Connected` carries the `session.id` instead of a userId.

If the user adds Security later, switch to the authenticated version above.

## 8. Testing the connection

With [websocat](https://github.com/vi/websocat):

```bash
websocat -H "Authorization: Bearer $ACCESS_TOKEN" ws://localhost:8080/ws
# expect: {"_class":"connected","userId":"..."}
websocat ws://localhost:8080/ws        # without token -> 401, no upgrade
```
