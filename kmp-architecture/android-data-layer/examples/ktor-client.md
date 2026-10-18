# Ktor HttpClient — Examples

## HttpClient Factory (`core:data`)

Configure the client once. Accept the engine externally so tests can swap in a mock engine:

```kotlin
object HttpClientFactory {
    fun create(engine: HttpClientEngine): HttpClient = HttpClient(engine) {
        install(ContentNegotiation) { json() }
        install(Auth) {
            bearer {
                loadTokens { /* load from DataStore */ }
                refreshTokens { /* call refresh endpoint, save new tokens */ }
            }
        }
        install(Logging) { logger = Logger.DEFAULT; level = LogLevel.ALL }
        defaultRequest { contentType(ContentType.Application.Json) }
    }
}
```

Inject `HttpClient` via Koin. For KMP, use the platform default engine.

## Safe Call Helpers usage

Use `safeCall` / `responseToResult` helpers and typed extension functions (`HttpClient.get`, `HttpClient.post`, `HttpClient.delete`) to keep data source call sites clean and uniform. See the **android-error-handling** skill (`examples/safe-call-helpers.md`) for the full implementation of these helpers.

```kotlin
suspend fun getNotes(): Result<List<NoteDto>, DataError.Network> {
    return httpClient.get(route = "/notes")
}
```

## Token Storage

Store tokens in DataStore (in `core:data` or a dedicated `:core:auth` / `:feature:auth:data` module). The Ktor `Auth` plugin reads/writes tokens and handles 401 refresh automatically.
