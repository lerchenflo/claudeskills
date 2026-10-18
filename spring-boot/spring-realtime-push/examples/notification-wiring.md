# Realtime/Push Wiring — Code Templates

## 1. Socket message subtype

```kotlin
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "_class")
@JsonSubTypes(
    JsonSubTypes.Type(value = SocketConnectionMessage.MessageChange::class, name = "messagechange"),
    // ... existing entries ...
    JsonSubTypes.Type(value = SocketConnectionMessage.XChange::class, name = "xchange"),   // ADD
)
sealed interface SocketConnectionMessage {
    // ... existing subtypes ...
    data class XChange(val x: XResponse, val newEntry: Boolean, val deleted: Boolean) : SocketConnectionMessage  // ADD
}
```

## 2. NotificationService methods

```kotlin
@Service
class NotificationService(
    private val socketConnectionHandler: SocketConnectionHandler,
    private val firebaseService: FirebaseService,
    private val apnsService: ApnsService,
    private val groupLookupService: GroupLookupService,   // lookups only, for recipient resolution
) {
    // Targeted
    fun notifyXUpdate(x: X, newEntry: Boolean, deleted: Boolean, actorId: ObjectId) {
        val msg = SocketConnectionMessage.XChange(x.toXResponse(), newEntry, deleted)
        recipientsOf(x).filter { it != actorId }.forEach { recipient ->
            if (!socketConnectionHandler.sendMessage(msg, receiverId = recipient)) {
                firebaseService.sendXNotificationToUser(recipient, x)
                apnsService.sendXNotificationToUser(recipient, x)
            }
        }
    }

    // Broadcast — no push fallback, offline clients sync later
    fun notifyXBroadcast(x: X, newEntry: Boolean, deleted: Boolean) {
        socketConnectionHandler.broadcast(
            SocketConnectionMessage.XChange(x.toXResponse(), newEntry, deleted),
            excludeUserId = null,   // editor usually needs it too (other devices)
        )
    }

    // Offline-only side notification
    fun notifyXSideEvent(recipient: ObjectId, x: X) {
        if (socketConnectionHandler.isConnected(recipient)) return
        firebaseService.sendXNotificationToUser(recipient, x)
        apnsService.sendXNotificationToUser(recipient, x)
    }
}
```

## 3. Push services (parallel signatures)

```kotlin
// FirebaseService
fun sendXNotificationToUser(userId: ObjectId, x: X) {
    firebaseTokenLookupService.tokensFor(userId).forEach { token ->
        val message = Message.builder()
            .setToken(token.token)
            .putData("type", "x")
            .putData("id", x.id.toHexString())
            .setAndroidConfig(AndroidConfig.builder().setPriority(AndroidConfig.Priority.HIGH).build())
            .build()
        try {
            FirebaseMessaging.getInstance().send(message)
        } catch (e: FirebaseMessagingException) {
            if (e.messagingErrorCode in INVALID_TOKEN_CODES) firebaseTokenLookupService.delete(token.id)
        }
    }
}

// ApnsService — same signature, Pushy client, .p8 auth key
fun sendXNotificationToUser(userId: ObjectId, x: X) { /* ... */ }
```

## 4. Call site in the feature service

```kotlin
val saved = xLookupService.save(entity)
notificationService.notifyXUpdate(saved, newEntry = isNew, deleted = false, actorId = requesterId)
```

## 5. Socket layer

- STOMP: `SocketPublisher`, created by `spring-boot-project-init` (`examples/websocket.md`).
- Raw WebSocket: `SocketConnectionHandler`, template in `examples/raw-websocket-handler.md`.
