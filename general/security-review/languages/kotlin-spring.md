# Kotlin / Spring Boot Security Guide

Applies to `.kt` files, Spring Boot (`@RestController`, `@Service`, Spring Security, Spring Data).

## Attacker-Controlled Inputs (Spring)

| Source | Notes |
|--------|-------|
| `@RequestParam`, `@PathVariable`, `@RequestBody`, `@RequestPart` | Always attacker-controlled |
| `@RequestHeader`, `HttpServletRequest.getHeader(...)` | Attacker-controlled (incl. `X-Forwarded-For` unless a trusted proxy strips/sets it) |
| Multipart file name + content (`MultipartFile.originalFilename`) | Attacker-controlled — path traversal risk when used in file paths |
| WebSocket handshake headers + frame payloads | Attacker-controlled |
| `Authentication.principal` | Trusted only AFTER token validation; check what sets it |

## Framework Mitigations (usually safe — don't flag)

- Spring Data repositories / `MongoTemplate` with `Criteria.where(...).is(...)` — parameterized, no NoSQL injection with typed values (`ObjectId`, `Long`).
- Thymeleaf `th:text` — auto-escaped. Flag only `th:utext` with user data.
- Jackson `@JsonTypeInfo(use = Id.NAME)` + explicit `@JsonSubTypes` — safe polymorphism. Flag `Id.CLASS` / `enableDefaultTyping` (gadget deserialization).
- `BCryptPasswordEncoder` for passwords — safe.

## Patterns to Flag

### Auth / Session
- `SessionCreationPolicy.STATELESS` + JWT: check token type confusion (refresh/email/reset tokens accepted as access tokens — verify a `type`/`typ` claim is enforced).
- JWT: `parseClaimsJws` vs `parseClaimsJwt` (unsigned!), missing expiry check, HS256 secret length < 32 bytes, secret reuse for other crypto purposes.
- CSRF disabled (`csrf { disable() }`): fine for pure Bearer-token APIs, but FLAG if any state-changing endpoint is reachable via cookies/GET or served HTML forms post to it.
- **GET endpoints that mutate state** — CSRF-able even without cookies via link prefetch, and violate safe-method caching assumptions.
- `permitAll()` lists: check every entry — actuator endpoints (`/actuator/**` exposes heapdump/env unless restricted), error pages, static resources overlapping API paths.

### Injection
- `Query(BasicQuery(userString))` or `$where` with interpolated strings — NoSQL injection.
- `ProcessBuilder` / `Runtime.exec` with user input.
- String-concatenated `MongoTemplate` field names from user input (operator injection via keys starting `$`).

### Files
- `File(baseDir, userProvidedName)` — traversal if name contains `../`. Kotlin `resolve()` same issue. Verify filename validated/generated server-side.
- Serving files by id: check id validated as `ObjectId`/numeric before path construction.
- Multipart uploads: check size limits (`spring.servlet.multipart.max-file-size`), content-type validation, image decode before persist (decode-then-reencode is a strong mitigation).

### Crypto
- Key derivation from substring of another secret (e.g. `SHA-256(jwtSecret.take(20))`) — reduces entropy, couples rotation. Flag as Medium.
- Static IV/nonce with AES-GCM — catastrophic. Verify random nonce per encryption.
- `Random`/`ThreadLocalRandom` for tokens — flag; require `SecureRandom`.
- Token comparison with `==` on strings is fine on hashed lookups; flag timing-sensitive raw comparisons only when secret is long-lived.

### Info Disclosure
- `ResponseStatusException(..., e.message)` leaking internals; stack traces in responses; `@ExceptionHandler` returning exception details.
- User enumeration: register/login/reset endpoints returning different messages/status for existing vs missing accounts.
- IDs/emails in logs that double as audit trail readable via admin/stats pages.

### Authorization (IDOR)
- Every endpoint taking an entity id: verify ownership/membership check against `requireAuth()` principal, not just authentication.
- Group operations: verify admin flag checked, not just membership.
- Media endpoints (`/profilepic/{id}`, `/images/{id}`): commonly forgotten authz — can any authenticated user fetch any other user's/conversation's media?

### Rate Limiting / DoS
- `X-Forwarded-For` trust: flag if client IP resolver trusts XFF without a trusted-proxy allowlist (rate-limit bypass + log spoofing).
- Log-collection-based rate limits: check the query is per-user AND per-type; check unauthenticated paths can't flood.
- Unbounded page_size on sync/pagination endpoints.

### WebSocket
- Handshake auth: verify token validated BEFORE session registered.
- Per-message authz: session userId pinned at handshake, not read from client frames.
- No message size/rate limits on inbound frames.

## Spring Boot Config Red Flags

- `management.endpoints.web.exposure.include=*` or actuator permitAll → env/heapdump exposure.
- `spring.mongodb.embedded`, default creds in compose files, DB admin GUIs (mongo-express) on exposed ports without auth.
- Missing `server.error.include-stacktrace=never` (Boot default is safe; flag if set to `always`).
- Secrets in `application.properties` committed to git (check git history, not just current file).
- CORS: `allowedOrigins("*")` combined with credentials.
