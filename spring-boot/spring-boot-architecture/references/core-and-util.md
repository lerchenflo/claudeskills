# core/ and util/ — Templates

## core/GlobalExceptionHandler.kt

One `@RestControllerAdvice` mapping exceptions to status codes, so services just throw.

| Exception | Status | Body | Thrown by |
|---|---|---|---|
| `MethodArgumentNotValidException` | 400 | `{"errors": [...]}` | `@Valid` DTOs |
| `IllegalArgumentException` | 400 | message | `require(...)` in controllers/services |
| `ResponseStatusException` | its status | message | explicit 403/404/409 |
| `NoResourceFoundException` | 404 | — | unknown static path |
| `HttpRequestMethodNotSupportedException` | 405 | — | wrong verb |
| `HttpMessageNotReadableException` | 400 | — | malformed JSON |
| `Exception` (fallback) | 500 | generic text, never the stack trace | anything else; log it with stack trace |

Code: `spring-boot-project-init` skill, `examples/webserver.md` (+ the `BadCredentialsException` → 401
handler in `examples/security.md`). Once `util/LoggingService` exists, also write an
`EXCEPTION_THROWN` audit row from the `Exception` fallback.

Keep the handler's own dependencies to LookupServices / LoggingService — it is constructed early
and must not pull in feature services.

## core/MongoConfig.kt

`@Configuration` holding `MongoCustomConversions` (custom `@ReadingConverter`/`@WritingConverter`
pairs for sealed value types) and anything index-related that annotations can't express.
`spring.data.mongodb.auto-index-creation=true` in `application.properties` so `@Indexed` /
`@CompoundIndex` on entities are applied.

## core/ startup and scheduled tasks

- Startup migrations / seed data: one `@Component` with `@EventListener(ApplicationReadyEvent::class)`
  (or `@PostConstruct` for trivial ones). Must be idempotent.
- Periodic cleanup: `@Component` + `@Scheduled(cron = "...")`, requires `@EnableScheduling` on the
  application class. Goes through LookupServices like everything else.

## core/security/

Full working code (JwtService, JwtAuthFilter, RequireAuth/SecurityContextHolder resolution,
SecurityConfig, HashEncoder, AdminGuard, refresh-token rotation, auth endpoints) lives in the
`spring-boot-project-init` skill, `examples/security.md`. Invariants to keep when editing it:

- Principal is the **userId hex string**, never `UserDetails`; `optionalAuth()` must ignore
  `AnonymousAuthenticationToken` (its principal is the String `"anonymousUser"`).
- `SecurityConfig` is an allowlist: new routes stay authenticated unless added on purpose.
- Every JWT carries a `type` claim and every validator checks it.
- Refresh tokens are stored hashed and rotated atomically (`findAndModify`).
- `AdminGuard` checks the role from the DB and answers 404 to non-admins.

### ratelimit/ (only if needed)

bucket4j + Redis `ProxyManager`; `RateLimitFilter` added **after** `JwtAuthFilter` so buckets can key
on userId; `@ConfigurationProperties` class for limits; IP resolver that trusts forwarded headers only
from configured proxy CIDRs.

## util/

| Helper | Purpose |
|---|---|
| `withOptimisticRetry { retry -> }` | Retries on `OptimisticLockingFailureException` (max 10, linear backoff ≤1 s). Wrap read-modify-write on `@Version` entities. |
| `ValidationUtils` | `object` with `validateObjectId`, `validateEmail`, `validatePassword`, `validatePaginationPage(Size)`, file/MIME/size checks. Controllers call `require(ValidationUtils.x(...)) { "..." }`. |
| `requireOrLog(cond, { debug }, { clientMsg })` | `require` that logs server-side context (lazily) before throwing 400. |
| `AppLogger` | Colored console logger (`debug/info/warn/error`); use instead of `println`. |
| `LoggingService` + `LogType` enum + `logs` collection | Audit log; `getLastLogByLogtype(userId, type)` doubles as a cheap per-user cooldown (e.g. email resend). Don't TTL the collection if used for cooldowns. |
| `JsonMapper` | Shared Jackson `ObjectMapper` (Kotlin + JSR-310 modules). |

`withOptimisticRetry` template:

```kotlin
inline fun <T> withOptimisticRetry(maxRetries: Int = 10, operation: (retryCount: Int) -> T): T {
    var retryCount = 0
    while (true) {
        try {
            return operation(retryCount)
        } catch (e: OptimisticLockingFailureException) {
            retryCount++
            if (retryCount > maxRetries) throw e
            Thread.sleep(min(100L * retryCount, 1000L))
        }
    }
}
```

`LoggingService` is infrastructure: it may inject LookupServices but no feature `*Service`, so any
service can depend on it without creating a cycle.
