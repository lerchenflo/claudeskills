# Security — JWT auth with refresh-token rotation

Stateless JWT auth. The access token (15 min) authenticates every request; the refresh token
(30 days) is stored hashed in Mongo, one row per device, and rotated on every refresh.

How a request gets its user: `JwtAuthFilter` validates `Authorization: Bearer <access token>` and
puts the userId (hex string) into `SecurityContextHolder` → any controller calls `requireAuth()`
to get it back as an `ObjectId`. The principal is a plain String on purpose: no `UserDetails`, no
DB hit per request.

## Contents
1. Dependencies + properties
2. core/security/JwtService.kt
3. core/security/JwtAuthFilter.kt
4. core/security/RequireAuth.kt — SecurityContextHolder resolution
5. core/security/SecurityConfig.kt
6. core/security/HashEncoder.kt
7. core/security/AdminGuard.kt
8. user/ — User entity, repository, lookup, `/users/me`
9. authentication/model/RefreshToken.kt + repository
10. authentication/AuthService.kt
11. authentication/AuthController.kt
12. GlobalExceptionHandler addition
13. Client contract + follow-ups

Resulting files:

```
<base>/
  core/security/  JwtService, JwtAuthFilter, RequireAuth, SecurityConfig, HashEncoder, AdminGuard
  authentication/ AuthController, AuthService, model/RefreshToken
  user/           UserController, UserLookupService, model/User, model/UserRole, model/UserResponse
  repository/     UserRepository, RefreshTokenRepository
```

## 1. Dependencies + properties

```kotlin
implementation("org.springframework.boot:spring-boot-starter-security")
implementation("io.jsonwebtoken:jjwt-api:0.13.0")
runtimeOnly("io.jsonwebtoken:jjwt-impl:0.13.0")
runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.13.0")
testImplementation("org.springframework.security:spring-security-test")
```

```properties
# HS256 key. Must be >= 32 bytes or startup fails (WeakKeyException) - that is intended.
# Generate: openssl rand -base64 48
jwt.secret=${JWT_SECRET}
```

## 2. core/security/JwtService.kt

Every token carries a `type` claim and every validation checks it. Without that, a 30-day refresh
token (or an email-verification link token) would be accepted as an access token, because they
are all signed with the same key.

```kotlin
package <base>.core.security

import io.jsonwebtoken.Claims
import io.jsonwebtoken.JwtException
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.Keys
import org.bson.types.ObjectId
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.time.Duration
import java.util.Date
import java.util.UUID
import javax.crypto.SecretKey

@Service
class JwtService(
    @Value("\${jwt.secret}") jwtSecret: String,
) {
    enum class TokenType(val claim: String) {
        ACCESS("access_token"),
        REFRESH("refresh_token"),
        // Single-purpose link tokens; add more as needed (account deletion, email change, ...)
        EMAIL_VERIFICATION("email_verification"),
        PASSWORD_RESET("password_reset"),
    }

    companion object {
        val ACCESS_TOKEN_VALIDITY: Duration = Duration.ofMinutes(15)
        val REFRESH_TOKEN_VALIDITY: Duration = Duration.ofDays(30)
        private const val TYPE_CLAIM = "type"
    }

    private val secretKey: SecretKey = Keys.hmacShaKeyFor(jwtSecret.toByteArray())

    fun generateAccessToken(userId: ObjectId): String =
        generate(userId, TokenType.ACCESS, ACCESS_TOKEN_VALIDITY)

    fun generateRefreshToken(userId: ObjectId): String =
        generate(userId, TokenType.REFRESH, REFRESH_TOKEN_VALIDITY)

    /** For email verification / password reset links. [extraClaims] e.g. the email being verified. */
    fun generatePurposeToken(
        userId: ObjectId,
        type: TokenType,
        validity: Duration,
        extraClaims: Map<String, String> = emptyMap(),
    ): String = generate(userId, type, validity, extraClaims)

    /** The token's user if it is valid, unexpired and of [expected] type, else null. Accepts a "Bearer " prefix. */
    fun userIdFrom(token: String, expected: TokenType): ObjectId? =
        parse(token, expected)?.subject?.takeIf(ObjectId::isValid)?.let(::ObjectId)

    /** All claims of a valid token of [expected] type, else null - for reading extra claims. */
    fun parse(token: String, expected: TokenType): Claims? {
        val raw = token.removePrefix("Bearer ").trim()
        if (raw.isEmpty()) return null
        val claims = try {
            Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(raw).payload
        } catch (e: JwtException) {
            return null   // bad signature, expired, malformed
        } catch (e: IllegalArgumentException) {
            return null
        }
        return claims.takeIf { it[TYPE_CLAIM] == expected.claim }
    }

    private fun generate(
        userId: ObjectId,
        type: TokenType,
        validity: Duration,
        extraClaims: Map<String, String> = emptyMap(),
    ): String {
        val now = Date()
        return Jwts.builder()
            .subject(userId.toHexString())
            .id(UUID.randomUUID().toString())   // jti: two tokens issued in the same millisecond still differ
            .claim(TYPE_CLAIM, type.claim)
            .claims(extraClaims)
            .issuedAt(now)
            .expiration(Date(now.time + validity.toMillis()))
            .signWith(secretKey, Jwts.SIG.HS256)
            .compact()
    }
}
```

## 3. core/security/JwtAuthFilter.kt

Never rejects anything itself — it only *adds* an authentication when the header is valid.
Rejecting is `SecurityConfig`'s job (`anyRequest().authenticated()` → 401), so public endpoints
keep working for callers with a missing or expired token.

```kotlin
package <base>.core.security

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.http.HttpHeaders
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

// @Component also registers it as a plain servlet filter; OncePerRequestFilter makes the second
// invocation a no-op, so it effectively runs once, inside the security chain.
@Component
class JwtAuthFilter(
    private val jwtService: JwtService,
) : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain,
    ) {
        val header = request.getHeader(HttpHeaders.AUTHORIZATION)
        if (header != null && header.startsWith("Bearer ")) {
            jwtService.userIdFrom(header, JwtService.TokenType.ACCESS)?.let { userId ->
                // Principal = userId hex string. Three-arg constructor marks it authenticated.
                SecurityContextHolder.getContext().authentication =
                    UsernamePasswordAuthenticationToken(userId.toHexString(), null, emptyList())
            }
        }
        filterChain.doFilter(request, response)
    }
}
```

## 4. core/security/RequireAuth.kt — SecurityContextHolder resolution

Top-level functions, so every controller handler starts with `val requesterId = requireAuth()`
without injecting anything.

```kotlin
package <base>.core.security

import org.bson.types.ObjectId
import org.springframework.http.HttpStatus
import org.springframework.security.authentication.AnonymousAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.web.server.ResponseStatusException

/** The logged-in user's id, or 401. First line of every authenticated controller handler. */
fun requireAuth(): ObjectId =
    optionalAuth() ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in")

/**
 * The logged-in user's id, or null. Only for permitAll endpoints that behave differently when a
 * valid access token happens to be present (e.g. logout with an expired access token).
 *
 * The anonymous check matters: on requests without a token Spring Security's anonymous filter puts
 * an AnonymousAuthenticationToken whose principal is the String "anonymousUser" into the context.
 * A bare `principal as? String` would hand that to ObjectId() and turn every anonymous call into a
 * 400 "invalid hexadecimal representation".
 */
fun optionalAuth(): ObjectId? {
    val auth = SecurityContextHolder.getContext().authentication
    if (auth == null || auth is AnonymousAuthenticationToken || !auth.isAuthenticated) return null
    return (auth.principal as? String)?.takeIf(ObjectId::isValid)?.let(::ObjectId)
}
```

## 5. core/security/SecurityConfig.kt

Allowlist, never denylist: a new route is authenticated unless someone adds it here on purpose.

```kotlin
package <base>.core.security

import jakarta.servlet.DispatcherType
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpStatus
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.config.http.SessionCreationPolicy
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.security.provisioning.InMemoryUserDetailsManager
import org.springframework.security.web.SecurityFilterChain
import org.springframework.security.web.authentication.HttpStatusEntryPoint
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter

@Configuration
@EnableWebSecurity
class SecurityConfig(
    private val jwtAuthFilter: JwtAuthFilter,
) {
    // Empty user store: stops Boot from generating a default user and logging its password.
    @Bean
    fun userDetailsService(): UserDetailsService = InMemoryUserDetailsManager()

    @Bean
    fun filterChain(http: HttpSecurity): SecurityFilterChain = http
        // No cookies/sessions -> CSRF has nothing to protect; tokens travel in the Authorization header
        .csrf { it.disable() }
        .sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }
        .authorizeHttpRequests { auth ->
            auth
                // Login, register, refresh, logout
                .requestMatchers("/auth/**").permitAll()
                // Health check etc. - list further public paths explicitly
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/error").permitAll()
                // ERROR/FORWARD: container-internal re-dispatches of a request that was already
                // authorized. ASYNC: the re-dispatch after an async/SSE response completes - it has no
                // SecurityContext (OncePerRequestFilter skips async dispatches), so authorizing it
                // again would fail a request that was already allowed.
                .dispatcherTypeMatchers(DispatcherType.ERROR, DispatcherType.FORWARD, DispatcherType.ASYNC).permitAll()
                // Everything else, including the /ws handshake, needs a valid access token
                .anyRequest().authenticated()
        }
        // Missing/invalid token -> 401 (clients refresh on 401), not a redirect to a login page
        .exceptionHandling { it.authenticationEntryPoint(HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)) }
        .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter::class.java)
        .build()
}
```

Browser clients on another origin need `.cors { }` plus a `CorsConfigurationSource` bean; native
apps don't.

## 6. core/security/HashEncoder.kt

```kotlin
package <base>.core.security

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.stereotype.Component

@Component
class HashEncoder {
    private val bcrypt = BCryptPasswordEncoder()

    fun encode(raw: String): String = bcrypt.encode(raw)!!

    fun matches(raw: String, hashed: String): Boolean = bcrypt.matches(raw, hashed)
}
```

BCrypt only looks at the first 72 bytes and recent Spring Security versions throw above that —
`AuthService.register` caps the UTF-8 byte length for this reason.

## 7. core/security/AdminGuard.kt

```kotlin
package <base>.core.security

import <base>.user.UserLookupService
import <base>.user.model.UserRole
import org.bson.types.ObjectId
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component
import org.springframework.web.server.ResponseStatusException

/**
 * requireAuth() proves the caller is logged in; this also checks the role. The role is read from
 * the DB rather than a JWT claim, so revoking admin takes effect on the next request instead of
 * when the access token expires.
 *
 * 404, not 403, for non-admins: a 403 would confirm the admin surface exists.
 */
@Component
class AdminGuard(
    private val userLookupService: UserLookupService,
) {
    fun requireAdmin(): ObjectId {
        val userId = requireAuth()
        if (userLookupService.findById(userId)?.role != UserRole.ADMIN) {
            throw ResponseStatusException(HttpStatus.NOT_FOUND)
        }
        return userId
    }
}
```

Usage: `val adminId = adminGuard.requireAdmin()` as the first line of admin handlers. Promote the
first admin directly in the DB (`role: "ADMIN"`).

## 8. user/

`user/model/UserRole.kt`

```kotlin
package <base>.user.model

enum class UserRole { USER, ADMIN }
```

`user/model/User.kt` — `java.time.Instant` (stored as a BSON Date, so TTL indexes and date
queries work; `kotlin.time.Instant` is stored as a subdocument).

```kotlin
package <base>.user.model

import org.bson.types.ObjectId
import org.springframework.data.annotation.Id
import org.springframework.data.annotation.TypeAlias
import org.springframework.data.mongodb.core.index.Indexed
import org.springframework.data.mongodb.core.mapping.Document
import java.time.Instant

@TypeAlias("user")
@Document("users")
data class User(
    @Id val id: ObjectId = ObjectId.get(),
    @Indexed(unique = true) val username: String,   // stored lowercase
    @Indexed(unique = true) val email: String,      // stored lowercase
    val hashedPassword: String,
    val role: UserRole = UserRole.USER,
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now(),
)
```

`user/model/UserResponse.kt` — never return the entity (it holds the password hash).

```kotlin
package <base>.user.model

import java.time.Instant

data class UserResponse(
    val id: String,
    val username: String,
    val email: String,
    val role: UserRole,
    val createdAt: Instant,
)

fun User.toUserResponse() = UserResponse(
    id = id.toHexString(),
    username = username,
    email = email,
    role = role,
    createdAt = createdAt,
)
```

`repository/UserRepository.kt`

```kotlin
package <base>.repository

import <base>.user.model.User
import org.bson.types.ObjectId
import org.springframework.data.mongodb.repository.MongoRepository

interface UserRepository : MongoRepository<User, ObjectId> {
    fun findByUsername(username: String): User?
    fun existsByUsername(username: String): Boolean
    fun existsByEmail(email: String): Boolean
}
```

`user/UserLookupService.kt` — sole owner of `UserRepository` (see `spring-boot-architecture`).

```kotlin
package <base>.user

import <base>.repository.UserRepository
import <base>.user.model.User
import org.bson.types.ObjectId
import org.springframework.stereotype.Service
import kotlin.jvm.optionals.getOrNull

@Service
class UserLookupService(
    private val userRepository: UserRepository,
) {
    fun findById(id: ObjectId): User? = userRepository.findById(id).getOrNull()
    fun findByUsername(username: String): User? = userRepository.findByUsername(username)
    fun existsByUsername(username: String): Boolean = userRepository.existsByUsername(username)
    fun existsByEmail(email: String): Boolean = userRepository.existsByEmail(email)
    fun save(user: User): User = userRepository.save(user)
}
```

`user/UserController.kt` — the smallest authenticated endpoint; handy to verify the setup.

```kotlin
package <base>.user

import <base>.core.security.requireAuth
import <base>.user.model.UserResponse
import <base>.user.model.toUserResponse
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException

@RestController
@RequestMapping("/users")
class UserController(
    private val userLookupService: UserLookupService,
) {
    @GetMapping("/me")
    fun me(): UserResponse {
        val requesterId = requireAuth()
        // A valid token for a deleted account: treat as logged out
        val user = userLookupService.findById(requesterId)
            ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in")
        return user.toUserResponse()
    }
}
```

## 9. authentication/model/RefreshToken.kt + repository

```kotlin
package <base>.authentication.model

import org.bson.types.ObjectId
import org.springframework.data.annotation.Id
import org.springframework.data.annotation.TypeAlias
import org.springframework.data.mongodb.core.index.CompoundIndex
import org.springframework.data.mongodb.core.index.CompoundIndexes
import org.springframework.data.mongodb.core.index.Indexed
import org.springframework.data.mongodb.core.mapping.Document
import java.time.Instant

/**
 * One row per device session, rotated IN PLACE: /auth/refresh atomically swaps [hashedToken] to
 * the new token's hash and moves the presented hash into [previousHashedToken]. A client that never
 * received the refresh response (connection dropped) retries with the old token, matches on
 * [previousHashedToken], and gets [rawToken] - the current token - back instead of being logged
 * out. That grace lasts until the client demonstrably advances the chain, not until a timer fires.
 *
 * Tradeoff: [rawToken] means a DB read leak exposes live refresh tokens. Drop it (and the replay
 * branch in AuthService.refresh) if forced re-logins on flaky networks are acceptable.
 *
 * Login dedups on (userId, deviceName), so the collection holds exactly one row per logged-in device.
 */
@TypeAlias("refreshtoken")
@Document("refresh_tokens")
@CompoundIndexes(
    CompoundIndex(name = "user_hash", def = "{'userId': 1, 'hashedToken': 1}"),
    CompoundIndex(name = "user_prev_hash", def = "{'userId': 1, 'previousHashedToken': 1}"),
    CompoundIndex(name = "user_device", def = "{'userId': 1, 'deviceName': 1}"),
)
data class RefreshToken(
    @Id val id: ObjectId = ObjectId.get(),
    val userId: ObjectId,
    /** SHA-256 of the currently valid refresh token of this device. */
    val hashedToken: String,
    /** Hash this row was last rotated away from; null until the first rotation. */
    val previousHashedToken: String? = null,
    /** Current raw token, returned on replay recovery only. */
    val rawToken: String,
    val deviceName: String,
    /** Slides forward on every rotation. java.time.Instant = BSON Date, so the TTL index really reaps expired rows. */
    @Indexed(expireAfter = "0s")
    val expiresAt: Instant,
    val createdAt: Instant = Instant.now(),
)
```

`repository/RefreshTokenRepository.kt`

```kotlin
package <base>.repository

import <base>.authentication.model.RefreshToken
import org.bson.types.ObjectId
import org.springframework.data.mongodb.repository.MongoRepository

interface RefreshTokenRepository : MongoRepository<RefreshToken, ObjectId> {
    fun findFirstByUserIdAndDeviceName(userId: ObjectId, deviceName: String): RefreshToken?
    fun findFirstByUserIdAndPreviousHashedToken(userId: ObjectId, previousHashedToken: String): RefreshToken?
    fun deleteByUserId(userId: ObjectId): Long
}
```

## 10. authentication/AuthService.kt

`AuthService` owns `RefreshTokenRepository` directly (it is the only user of it) and uses
`MongoTemplate` for the atomic rotation, which a derived query can't express.

```kotlin
package <base>.authentication

import <base>.authentication.model.RefreshToken
import <base>.core.security.HashEncoder
import <base>.core.security.JwtService
import <base>.repository.RefreshTokenRepository
import <base>.user.UserLookupService
import <base>.user.model.User
import org.bson.types.ObjectId
import org.slf4j.LoggerFactory
import org.springframework.dao.DuplicateKeyException
import org.springframework.data.mongodb.core.FindAndModifyOptions
import org.springframework.data.mongodb.core.MongoTemplate
import org.springframework.data.mongodb.core.query.Criteria
import org.springframework.data.mongodb.core.query.Query
import org.springframework.data.mongodb.core.query.Update
import org.springframework.http.HttpStatus
import org.springframework.security.authentication.BadCredentialsException
import org.springframework.stereotype.Service
import org.springframework.web.server.ResponseStatusException
import java.security.MessageDigest
import java.time.Instant
import java.util.Base64

@Service
class AuthService(
    private val jwtService: JwtService,
    private val hashEncoder: HashEncoder,
    private val userLookupService: UserLookupService,
    private val refreshTokenRepository: RefreshTokenRepository,
    private val mongoTemplate: MongoTemplate,
) {
    private val logger = LoggerFactory.getLogger(AuthService::class.java)

    data class TokenPair(val accessToken: String, val refreshToken: String)

    // Compared against when the username doesn't exist, so "unknown user" takes as long as
    // "wrong password" and response timing can't be used to enumerate accounts.
    private val dummyHash = hashEncoder.encode("dummy-password-for-timing")

    fun register(username: String, email: String, password: String): User {
        val normalizedUsername = username.trim().lowercase()
        val normalizedEmail = email.trim().lowercase()
        require(password.toByteArray(Charsets.UTF_8).size <= 72) { "Password too long" }

        if (userLookupService.existsByUsername(normalizedUsername) || userLookupService.existsByEmail(normalizedEmail)) {
            throw ResponseStatusException(HttpStatus.CONFLICT, "Username or email already taken")
        }

        return try {
            userLookupService.save(
                User(
                    username = normalizedUsername,
                    email = normalizedEmail,
                    hashedPassword = hashEncoder.encode(password),
                )
            )
        } catch (e: DuplicateKeyException) {
            // Two concurrent registrations passed the exists-check; the unique index caught the second
            throw ResponseStatusException(HttpStatus.CONFLICT, "Username or email already taken")
        }
    }

    fun login(username: String, password: String, deviceName: String): TokenPair {
        val user = userLookupService.findByUsername(username.trim().lowercase())

        // Unknown user and wrong password are one path with one answer, so callers can't enumerate accounts
        val passwordOk = hashEncoder.matches(password, user?.hashedPassword ?: dummyHash)
        if (user == null || !passwordOk) {
            logger.warn("Failed login for username=${username.take(100)}")
            throw BadCredentialsException("Invalid credentials")
        }

        val accessToken = jwtService.generateAccessToken(user.id)
        val refreshToken = jwtService.generateRefreshToken(user.id)

        // Reuse this device's session row instead of inserting a second one. If the in-place
        // rotation loses a race with a concurrent refresh of the same row, insert a fresh row;
        // the stale one ages out via the TTL index.
        val existing = refreshTokenRepository.findFirstByUserIdAndDeviceName(user.id, deviceName)
        if (existing == null || rotateTokenRow(user.id, existing.hashedToken, refreshToken, deviceName) == null) {
            refreshTokenRepository.save(
                RefreshToken(
                    userId = user.id,
                    hashedToken = hashToken(refreshToken),
                    rawToken = refreshToken,
                    deviceName = deviceName,
                    expiresAt = refreshExpiry(),
                )
            )
        }

        return TokenPair(accessToken, refreshToken)
    }

    fun refresh(refreshToken: String, deviceName: String): TokenPair {
        val userId = jwtService.userIdFrom(refreshToken, JwtService.TokenType.REFRESH)
            ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid refresh token")
        userLookupService.findById(userId)
            ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid refresh token")

        val presentedHash = hashToken(refreshToken)
        val newRefreshToken = jwtService.generateRefreshToken(userId)

        // Exactly one concurrent caller can win this findAndModify
        if (rotateTokenRow(userId, presentedHash, newRefreshToken, deviceName) != null) {
            return TokenPair(jwtService.generateAccessToken(userId), newRefreshToken)
        }

        // No row holds this hash as current. Either the client lost the previous refresh response
        // (or lost a race with a concurrent refresh) and is replaying the token that was just
        // rotated away -> hand back the row's current token; or the token is dead (logged out,
        // expired, password changed) -> 401 forces a re-login.
        val recovery = refreshTokenRepository.findFirstByUserIdAndPreviousHashedToken(userId, presentedHash)
        if (recovery != null) {
            return TokenPair(jwtService.generateAccessToken(userId), recovery.rawToken)
        }

        throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid refresh token")
    }

    /**
     * Ends a session. Idempotent: an unknown, expired or already rotated token is a no-op, because a
     * client pressing logout must never be stuck with a session it cannot drop. The refresh token
     * identifies the session (it is server-signed, so presenting it is proof enough);
     * [authenticatedUserId] only carries an all-devices logout from a client whose refresh token is
     * gone. Already-issued access tokens stay valid until they expire (no blacklist).
     */
    fun logout(refreshToken: String?, allDevices: Boolean, authenticatedUserId: ObjectId?) {
        val tokenUserId = refreshToken?.let { jwtService.userIdFrom(it, JwtService.TokenType.REFRESH) }
        val userId = tokenUserId ?: authenticatedUserId ?: return

        when {
            allDevices -> refreshTokenRepository.deleteByUserId(userId)
            tokenUserId != null && refreshToken != null -> {
                val hash = hashToken(refreshToken)
                // previousHashedToken too: logging out with the token presented right before a
                // rotation must still end the session
                mongoTemplate.remove(
                    Query(
                        Criteria.where("userId").`is`(userId).orOperator(
                            Criteria.where("hashedToken").`is`(hash),
                            Criteria.where("previousHashedToken").`is`(hash),
                        )
                    ),
                    RefreshToken::class.java,
                )
            }
        }
    }

    /**
     * Atomic in-place rotation of the row whose current hash is [expectedCurrentHash]. Returns the
     * row as it was before, or null if none matched (rotated by someone else, or never existed).
     */
    private fun rotateTokenRow(
        userId: ObjectId,
        expectedCurrentHash: String,
        newRawToken: String,
        deviceName: String,
    ): RefreshToken? = mongoTemplate.findAndModify(
        Query(Criteria.where("userId").`is`(userId).and("hashedToken").`is`(expectedCurrentHash)),
        Update()
            .set("previousHashedToken", expectedCurrentHash)
            .set("hashedToken", hashToken(newRawToken))
            .set("rawToken", newRawToken)
            .set("deviceName", deviceName)
            .set("expiresAt", refreshExpiry()),
        FindAndModifyOptions.options().returnNew(false),
        RefreshToken::class.java,
    )

    private fun refreshExpiry(): Instant = Instant.now().plus(JwtService.REFRESH_TOKEN_VALIDITY)

    // SHA-256, not BCrypt: refresh tokens are long random strings (no brute-force risk), and the
    // hash must be deterministic so rows can be looked up by it.
    private fun hashToken(token: String): String =
        Base64.getEncoder().encodeToString(MessageDigest.getInstance("SHA-256").digest(token.toByteArray()))
}
```

## 11. authentication/AuthController.kt

```kotlin
package <base>.authentication

import <base>.core.security.optionalAuth
import <base>.user.model.UserResponse
import <base>.user.model.toUserResponse
import jakarta.validation.Valid
import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Pattern
import jakarta.validation.constraints.Size
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/auth")
class AuthController(
    private val authService: AuthService,
) {
    data class RegisterRequest(
        @field:NotBlank @field:Size(min = 3, max = 30)
        @field:Pattern(regexp = "^[A-Za-z0-9_.]+$", message = "Username may only contain letters, digits, _ and .")
        val username: String,
        @field:NotBlank @field:Email @field:Size(max = 254)
        val email: String,
        @field:NotBlank @field:Size(min = 8, max = 72)
        @field:Pattern(
            regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$",
            message = "Password needs an uppercase letter, a lowercase letter and a digit",
        )
        val password: String,
    )

    data class LoginRequest(
        @field:NotBlank @field:Size(max = 100) val username: String,
        @field:NotBlank @field:Size(max = 72) val password: String,
        @field:NotBlank @field:Size(max = 200) val deviceName: String,
    )

    data class RefreshRequest(
        @field:NotBlank @field:Size(max = 2000) val refreshToken: String,
        @field:NotBlank @field:Size(max = 200) val deviceName: String,
    )

    data class LogoutRequest(
        @field:Size(max = 2000) val refreshToken: String? = null,
        val allDevices: Boolean = false,
    )

    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    fun register(@Valid @RequestBody body: RegisterRequest): UserResponse =
        authService.register(body.username, body.email, body.password).toUserResponse()

    @PostMapping("/login")
    fun login(@Valid @RequestBody body: LoginRequest): AuthService.TokenPair =
        authService.login(body.username, body.password, body.deviceName)

    @PostMapping("/refresh")
    fun refresh(@Valid @RequestBody body: RefreshRequest): AuthService.TokenPair =
        authService.refresh(body.refreshToken, body.deviceName)

    // permitAll like all of /auth/**: must work with an expired access token
    @PostMapping("/logout")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    fun logout(@Valid @RequestBody body: LogoutRequest) =
        authService.logout(body.refreshToken, body.allDevices, optionalAuth())
}
```

## 12. GlobalExceptionHandler addition

Add to `core/GlobalExceptionHandler.kt` (from `webserver.md`) **above** the `Exception` fallback,
otherwise every wrong password is logged as a 500 with a stack trace:

```kotlin
// import org.springframework.security.authentication.BadCredentialsException

@ExceptionHandler(BadCredentialsException::class)
fun handleBadCredentials(e: BadCredentialsException): ResponseEntity<Map<String, String>> =
    ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(mapOf("error" to "Invalid credentials"))
```

## 13. Client contract + follow-ups

Client side:
- Send `Authorization: Bearer <accessToken>` on every request (and on the `/ws` handshake).
- On 401: call `/auth/refresh` once, store **both** returned tokens, retry. Serialize refreshes
  behind one mutex — parallel refreshes are handled server-side, but one in flight is cleaner.
- 401 from `/auth/refresh` → logged out, show login.
- `deviceName` should be stable per installation (it dedups sessions).

Follow-ups to tell the user about (not part of the bootstrap):
- **Password change / reset** must call `refreshTokenRepository.deleteByUserId(userId)`, or stolen
  sessions survive the change.
- **Rate limiting** on `/auth/**` — login is brute-forceable until it exists.
- Email verification / password reset links: `generatePurposeToken(userId, TokenType.PASSWORD_RESET,
  Duration.ofHours(1), mapOf("email" to email))` and `parse(token, TokenType.PASSWORD_RESET)`.
