# Sync Endpoint — Code Templates

## Shared `IdTimeStamp` (define once, e.g. in the user feature or util/)

```kotlin
data class IdTimeStamp(
    @field:NotBlank @field:Size(max = 100) val id: String,
    @field:NotBlank @field:Size(max = 30) val timeStamp: String,   // epoch millis as string
)
```

## Shape A — id/timestamp diff

### Controller

```kotlin
@PostMapping("/sync")
fun syncX(
    @RequestParam(value = "page", defaultValue = "0") page: Int,
    @RequestParam(value = "page_size", defaultValue = "400") pageSize: Int,
    @Valid @RequestBody clientEntries: List<IdTimeStamp>,
): XSyncResponse {
    val requesterId = requireAuth()
    require(ValidationUtils.validatePaginationPage(page)) { "Invalid page number" }
    require(ValidationUtils.validatePaginationPageSize(pageSize)) { "Invalid page size" }
    return xService.xSync(requesterId, clientEntries, page, pageSize)
}
```

### Service

```kotlin
data class XSyncResponse(
    val updatedEntries: List<XResponse>,
    val deletedEntries: List<String>,
    val moreEntries: Boolean,
)

fun xSync(requesterId: ObjectId, clientEntries: List<IdTimeStamp>, page: Int, pageSize: Int): XSyncResponse {
    val clientMap = clientEntries.associate { it.id to it.timeStamp }
    val visible = xLookupService.findVisibleFor(requesterId)          // scoped + deleted=false
    val serverIds = visible.map { it.id.toHexString() }.toSet()

    val changed = visible.filter { entry ->
        val clientTs = clientMap[entry.id.toHexString()] ?: return@filter true   // unknown → add
        clientTs.toLongOrNull()?.let { entry.updatedAt.toEpochMilli() > it } ?: true
    }.sortedByDescending { it.updatedAt }

    val start = page * pageSize
    val paged = changed.drop(start).take(pageSize).map { it.toXResponse() }

    // Deletions relative to the client's full known set — page 0 only.
    val deleted = if (page == 0) clientMap.keys.filter { it !in serverIds } else emptyList()

    return XSyncResponse(paged, deleted, moreEntries = start + pageSize < changed.size)
}
```

## Shape B — version watermark

### Counter

```kotlin
enum class SyncCollection(val key: String) { X("x_entries") }

@Document("counters")
data class VersionCounter(@Id val id: String, val seq: Long)

@Component
class VersionCounterService(private val mongoTemplate: MongoTemplate) {
    private val inFlight = ConcurrentHashMap<SyncCollection, ConcurrentSkipListSet<Long>>()

    fun next(c: SyncCollection): Long = mongoTemplate.findAndModify(
        Query(Criteria.where("_id").`is`(c.key)),
        Update().inc("seq", 1),
        FindAndModifyOptions.options().returnNew(true).upsert(true),
        VersionCounter::class.java,
    )!!.seq

    fun current(c: SyncCollection): Long =
        mongoTemplate.findById(c.key, VersionCounter::class.java)?.seq ?: 0L

    /** Allocate a version, keep it "in flight" until [block] (the write) finishes. */
    fun <T> withVersion(c: SyncCollection, block: (Long) -> T): T {
        val set = inFlight.computeIfAbsent(c) { ConcurrentSkipListSet() }
        val v = next(c)
        set.add(v)
        try { return block(v) } finally { set.remove(v) }
    }

    /** Highest version guaranteed fully written. Bound every sync query by this. */
    fun safeWatermark(c: SyncCollection): Long {
        val lowestInFlight = inFlight[c]?.firstOrNull()
        return if (lowestInFlight != null) lowestInFlight - 1 else current(c)
    }
}
```

### Writing

```kotlin
versionCounterService.withVersion(SyncCollection.X) { v ->
    xLookupService.save(entity.copy(version = v, updatedAt = Instant.now()))
}
```

Every mutation (including soft delete) gets a new version.

### Controller + service

```kotlin
@GetMapping("/sync")
fun syncX(
    @RequestParam(defaultValue = "0") since: Long,
    @RequestParam(value = "page_size", defaultValue = "400") pageSize: Int,
): XVersionSyncResponse {
    val requesterId = requireAuth()
    require(since >= 0) { "Invalid since version" }
    require(ValidationUtils.validatePaginationPageSize(pageSize)) { "Invalid page size" }
    return xService.xSync(requesterId, since, pageSize)
}

data class XVersionSyncResponse(
    val updatedEntries: List<XResponse>,
    val deletedEntries: List<String>,
    val latestVersion: Long,
    val moreEntries: Boolean,
)

fun xSync(requesterId: ObjectId, since: Long, pageSize: Int): XVersionSyncResponse {
    val upTo = versionCounterService.safeWatermark(SyncCollection.X)
    val scopeIds = scopeLookupService.visibleScopeIds(requesterId)          // computed server-side
    val rows = xLookupService.findVersionRange(scopeIds, since, upTo, pageSize) // version in (since, upTo], sorted asc
    val (deleted, live) = rows.partition { it.deleted }
    val more = rows.size == pageSize
    return XVersionSyncResponse(
        updatedEntries = live.map { it.toXResponse() },
        deletedEntries = deleted.map { it.id.toHexString() },
        // Full page → resume after the last row. Short page → the whole (since, upTo] range was
        // scanned, so the client may jump to upTo.
        latestVersion = if (more) rows.last().version else maxOf(since, upTo),
        moreEntries = more,
    )
}
```

Scope changes (gaining access to a group whose rows have versions below the client's cursor) are
not covered by the range query — handle them separately (e.g. `joinedAtVersion` → full replay for
that scope).
