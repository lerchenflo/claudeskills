# Feature Scaffold — Code Templates

Replace `X` / `x` with the feature name and `<base>` with the base package.

## Application class

Created once by the `spring-boot-project-init` skill (`examples/webserver.md`). The part features
rely on: `@EnableMongoRepositories(basePackages = ["<base>.repository"])`; add `@EnableScheduling` /
`@EnableAsync` there when a feature first uses `@Scheduled` / `@Async`.

## Model — `<feature>/model/X.kt`

```kotlin
@TypeAlias("x")
@Document("x_entries")
data class X(
    @Id val id: ObjectId = ObjectId.get(),
    val ownerId: ObjectId,
    val name: String,
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now(),
    val updatedBy: ObjectId,
    val deleted: Boolean = false,          // only if clients sync this collection
    @Version val version: Long? = null,    // only if concurrently modified
)
```

## Response DTO — `<feature>/model/XResponse.kt`

```kotlin
data class XResponse(
    val id: String,
    val name: String,
    val updatedAt: Long,
)

fun X.toXResponse() = XResponse(
    id = id.toHexString(),
    name = name,
    updatedAt = updatedAt.toEpochMilli(),
)
```

## Repository — `repository/XRepository.kt`

```kotlin
package <base>.repository

interface XRepository : MongoRepository<X, ObjectId> {
    fun findByOwnerIdAndDeletedFalse(ownerId: ObjectId): List<X>
}
```

## LookupService — `<feature>/XLookupService.kt`

The only class that injects `XRepository`. Reads + thin persistence. Never injects a write Service.

```kotlin
@Service
class XLookupService(
    private val xRepository: XRepository,
    // private val userLookupService: UserLookupService,  // lower-level lookups only
) {
    fun findById(id: ObjectId): X? = xRepository.findById(id).getOrNull()

    fun getById(id: ObjectId): X = findById(id)
        ?: throw ResponseStatusException(HttpStatus.NOT_FOUND, "X not found")

    fun findForOwner(ownerId: ObjectId): List<X> = xRepository.findByOwnerIdAndDeletedFalse(ownerId)

    fun save(x: X): X = xRepository.save(x)

    fun delete(id: ObjectId) = xRepository.deleteById(id)
}
```

## Service — `<feature>/XService.kt`

```kotlin
@Service
class XService(
    private val xLookupService: XLookupService,
    private val userLookupService: UserLookupService,   // other features: lookups only
    private val notificationService: NotificationService,
    private val loggingService: LoggingService,
) {
    fun upsert(entryId: ObjectId?, name: String, requesterId: ObjectId): X {
        val saved = withOptimisticRetry {
            val existing = entryId?.let { xLookupService.getById(it) }
            if (existing != null && existing.ownerId != requesterId) {
                throw ResponseStatusException(HttpStatus.FORBIDDEN, "Not your entry")
            }
            xLookupService.save(
                existing?.copy(name = name, updatedAt = Instant.now(), updatedBy = requesterId)
                    ?: X(ownerId = requesterId, name = name, updatedBy = requesterId)
            )
        }
        notificationService.notifyXChange(saved, deleted = false)
        loggingService.log(requesterId, LogType.X_UPSERTED)
        return saved
    }

    fun delete(id: ObjectId, requesterId: ObjectId) {
        val existing = xLookupService.getById(id)
        if (existing.ownerId != requesterId) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        val saved = xLookupService.save(existing.copy(deleted = true, updatedAt = Instant.now(), updatedBy = requesterId))
        notificationService.notifyXChange(saved, deleted = true)
    }
}
```

## Controller — `<feature>/XController.kt`

```kotlin
@RestController
@RequestMapping("/x")
class XController(
    private val xService: XService,
    private val xLookupService: XLookupService,
) {
    data class XRequest(
        val entryId: String?,                       // null = create
        @field:NotBlank(message = "Name must not be blank")
        @field:Size(max = 100, message = "Name too long")
        val name: String,
    )

    @PostMapping("/upsert")
    fun upsert(@Valid @RequestBody request: XRequest): XResponse {
        val requesterId = requireAuth()
        request.entryId?.let { require(ValidationUtils.validateObjectId(it)) { "Invalid entry id" } }
        return xService.upsert(request.entryId?.let(::ObjectId), request.name, requesterId).toXResponse()
    }

    @GetMapping("/mine")
    fun mine(): List<XResponse> {
        val requesterId = requireAuth()
        return xLookupService.findForOwner(requesterId).map { it.toXResponse() }
    }

    @DeleteMapping("/delete")
    fun delete(@RequestParam entryid: String) {
        val requesterId = requireAuth()
        require(ValidationUtils.validateObjectId(entryid)) { "Invalid entry id" }
        xService.delete(ObjectId(entryid), requesterId)
    }
}
```

## Polymorphic response (when needed)

```kotlin
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "_class")
@JsonSubTypes(
    JsonSubTypes.Type(value = XResponse.Simple::class, name = "simple"),
    JsonSubTypes.Type(value = XResponse.Full::class, name = "full"),
)
sealed interface XResponse {
    data class Simple(val id: String) : XResponse
    data class Full(val id: String, val details: String) : XResponse
}
```
