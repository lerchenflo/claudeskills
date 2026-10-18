# Webserver — base setup

Always applied. Everything else builds on it.

## Contents
1. Dependencies
2. application.properties
3. Application class
4. core/GlobalExceptionHandler.kt
5. core/PublicController.kt
6. repository/ package

## 1. Dependencies (`build.gradle.kts`)

```kotlin
implementation("org.springframework.boot:spring-boot-starter-web")          // Boot 4 may generate -webmvc; either works
implementation("org.springframework.boot:spring-boot-starter-data-mongodb")
implementation("org.springframework.boot:spring-boot-starter-validation")   // @Valid request DTOs
implementation("org.jetbrains.kotlin:kotlin-reflect")
// Boot 4: tools.jackson.module:jackson-module-kotlin   |   Boot 3: com.fasterxml.jackson.module:jackson-module-kotlin
implementation("tools.jackson.module:jackson-module-kotlin")
```

Plugins: `kotlin("plugin.spring")` (opens Spring classes). Start.spring.io adds it for Kotlin.

## 2. application.properties

```properties
spring.application.name=<app>

# Boot 4: spring.mongodb.*   |   Boot 3: spring.data.mongodb.uri / .database
spring.mongodb.uri=${MONGODB_URI}
spring.mongodb.database=${MONGODB_DATABASE:app}
# Applies @Indexed / @CompoundIndex from the entities at startup
spring.data.mongodb.auto-index-creation=true

# Send the exception message in error bodies (our handler already does; this covers Spring's own errors)
spring.web.error.include-message=always
```

## 3. Application class

Register the repository package in the **same step** you create it: Spring Data only scans the
package named here, so a repository anywhere else silently never becomes a bean ("No qualifying
bean of type XRepository").

```kotlin
package <base>

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories

@SpringBootApplication
@EnableMongoRepositories(basePackages = ["<base>.repository"])
class <App>Application

fun main(args: Array<String>) {
    runApplication<<App>Application>(*args)
}
```

The WebSocket option adds `@EnableScheduling` here.

## 4. core/GlobalExceptionHandler.kt

Services just throw; this maps exceptions to status codes so no controller has try/catch. The
Security option adds one more handler (`BadCredentialsException` → 401) — see `security.md`.

```kotlin
package <base>.core

import jakarta.servlet.http.HttpServletRequest
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.http.converter.HttpMessageNotReadableException
import org.springframework.web.HttpRequestMethodNotSupportedException
import org.springframework.web.bind.MethodArgumentNotValidException
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import org.springframework.web.server.ResponseStatusException
import org.springframework.web.servlet.resource.NoResourceFoundException

@RestControllerAdvice
class GlobalExceptionHandler {
    private val logger = LoggerFactory.getLogger(GlobalExceptionHandler::class.java)

    // @Valid request DTO failed its jakarta.validation annotations
    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidation(e: MethodArgumentNotValidException): ResponseEntity<Map<String, Any>> =
        ResponseEntity.badRequest()
            .body(mapOf("errors" to e.bindingResult.allErrors.map { it.defaultMessage ?: "Invalid value" }))

    // require(...) in controllers/services
    @ExceptionHandler(IllegalArgumentException::class)
    fun handleIllegalArgument(e: IllegalArgumentException): ResponseEntity<Map<String, String?>> =
        ResponseEntity.badRequest().body(mapOf("error" to e.message))

    // Explicit 401/403/404/409 from services
    @ExceptionHandler(ResponseStatusException::class)
    fun handleStatus(e: ResponseStatusException, request: HttpServletRequest): ResponseEntity<Map<String, String?>> {
        if (e.statusCode.is5xxServerError) logger.error("${request.method} ${request.requestURI}: ${e.reason}", e)
        return ResponseEntity.status(e.statusCode).body(mapOf("error" to e.reason))
    }

    @ExceptionHandler(NoResourceFoundException::class)
    fun handleNotFound(e: NoResourceFoundException): ResponseEntity<Map<String, String>> =
        ResponseEntity.status(HttpStatus.NOT_FOUND).body(mapOf("error" to "Not found: ${e.resourcePath}"))

    @ExceptionHandler(HttpRequestMethodNotSupportedException::class)
    fun handleMethod(e: HttpRequestMethodNotSupportedException): ResponseEntity<Map<String, String>> =
        ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(mapOf("error" to "Method ${e.method} not supported"))

    // Malformed JSON is a client bug: one warn line, no stack trace
    @ExceptionHandler(HttpMessageNotReadableException::class)
    fun handleUnreadable(e: HttpMessageNotReadableException, request: HttpServletRequest): ResponseEntity<Map<String, String>> {
        val cause = e.mostSpecificCause.message?.lineSequence()?.firstOrNull() ?: "unreadable body"
        logger.warn("Unreadable body on ${request.method} ${request.requestURI}: $cause")
        return ResponseEntity.badRequest().body(mapOf("error" to "Invalid request body"))
    }

    // Fallback: log with stack trace, never leak it to the client
    @ExceptionHandler(Exception::class)
    fun handleAny(e: Exception, request: HttpServletRequest): ResponseEntity<Map<String, String>> {
        logger.error("Unhandled ${e.javaClass.simpleName} on ${request.method} ${request.requestURI}", e)
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(mapOf("error" to "An unexpected error occurred"))
    }
}
```

Keep this class's own dependencies to LookupServices / logging only — it is created early, and
injecting a feature service here is a classic source of startup cycles.

## 5. core/PublicController.kt

A trivial unauthenticated endpoint for health checks and for verifying the setup with curl.

```kotlin
package <base>.core

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/public")
class PublicController {
    @GetMapping("/ping")
    fun ping(): Map<String, String> = mapOf("status" to "ok")
}
```

## 6. repository/ package

Create `<base>/repository/` now (the Security option puts `UserRepository` and
`RefreshTokenRepository` there). Every Spring Data interface goes in this package, nothing else.
