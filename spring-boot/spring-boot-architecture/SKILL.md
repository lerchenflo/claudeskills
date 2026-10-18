---
name: spring-boot-architecture
description: House architecture for Kotlin + Spring Boot + MongoDB backends — feature packages with Controller / Service / LookupService / model, all Spring Data repositories in one `repository/` package registered via @EnableMongoRepositories, a LookupService that owns each repository so it can be injected anywhere without circular dependencies, plus core/ (exception handler, config, security) and util/ conventions. Use this skill whenever structuring a Spring Boot project, adding a feature/controller/service/repository/entity to a Spring Boot backend, deciding where a class should live, or fixing a circular dependency / BeanCurrentlyInCreationException. Trigger on phrases like "spring boot", "new feature", "new controller", "new service", "new repository", "MongoRepository", "lookup service", "circular dependency", "@Lazy", "package structure", "EnableMongoRepositories", "SecurityConfig", "GlobalExceptionHandler". For bootstrapping a fresh start.spring.io project (deps, JWT auth, WebSocket) use spring-boot-project-init. If the project has its own local skill (e.g. a project map), read that too — it lists the project's concrete deviations.
---

# Spring Boot Architecture (Kotlin + MongoDB)

Opinionated layout for Spring Boot backends. Every feature looks the same, every repository has
exactly one owner, and dependencies only flow in one direction so the context never hits a cycle.

## Examples & references

| What | File |
|---|---|
| Code templates: controller, service, lookup service, repository, entity + response DTO | `examples/feature-scaffold.md` |
| `core/` (exception handler, Mongo config, security package, startup hooks, scheduled tasks) and `util/` (optimistic retry, validation, logging, audit log) templates | `references/core-and-util.md` |
| Bootstrap code: application class, GlobalExceptionHandler, full `core/security/` (JWT), WebSocket endpoint | `spring-boot-project-init` skill |

Read the matching file before writing code — the rules below are the "why", the files are the "how".

---

## 1. Package layout

Base package = `<group>.<app>` (where the `@SpringBootApplication` class lives).

```
<base>/
  <App>Application.kt          @SpringBootApplication + @EnableMongoRepositories(basePackages = ["<base>.repository"])
  core/
    GlobalExceptionHandler.kt  @RestControllerAdvice
    MongoConfig.kt             converters, index setup
    security/                  only if the app has auth (see §6)
  repository/                  ALL Spring Data repository interfaces, nothing else
  util/                        cross-cutting helpers (retry, validation, logger, audit log)
  <feature>/
    <Feature>Controller.kt
    <Feature>Service.kt
    <Feature>LookupService.kt
    model/
      <Entity>.kt              @Document
      <Entity>Response.kt      client DTO + to<Entity>Response() mapper
      <Feature>Request.kt      only when the request DTO is shared; otherwise nest it in the controller
  <feature>/<subfeature>/      same shape, nested when it only makes sense inside the parent
```

Rules:
- One package per feature; model package is always named **`model/`** (not `<feature>model/`).
- **Never** put a repository inside a feature package. Spring Data only scans the package named in
  `@EnableMongoRepositories`, so a repository elsewhere is silently not created → "No qualifying bean".
- When creating a new project: create `repository/` and add `@EnableMongoRepositories(basePackages =
  ["<base>.repository"])` to the application class **in the same step**, before the first repository.

## 2. Layers and what each may inject

| Layer | Annotation | Responsibility | May inject |
|---|---|---|---|
| `XController` | `@RestController` | HTTP mapping, auth (`requireAuth()`), param validation, entity → DTO mapping | `XService`, `XLookupService` (for pure reads), other features' **LookupServices** |
| `XService` | `@Service` | Business logic, authorization checks, orchestration, notifications, audit log | own `XLookupService`, other **LookupServices**, infra services (notification, logging, file storage), `MongoTemplate` for atomic ops |
| `XLookupService` | `@Service` | **Owns `XRepository`**: reads + thin persistence (`save`, `delete`, `exists`) | own repositories, `MongoTemplate`, *lower-level* LookupServices |
| `XRepository` | (interface) | Spring Data derived queries | — |

### The repository-ownership rule

- Every repository has exactly **one owner: its feature's LookupService**. Create the LookupService
  together with the repository, even if it starts with two methods.
- Prefer that `XService` does **not** inject `XRepository` at all — it calls `xLookupService.save(...)`,
  `xLookupService.findById(...)`. Inject the repository/`MongoTemplate` in the service only when an
  operation can't be expressed through the lookup (atomic `findAndModify`, bulk `updateMulti`); say
  why in a one-line comment.
- Other features **never** inject `XRepository` or `XService` to read X — they inject
  `XLookupService`.

### Why this prevents cycles

Services depend on lookups; lookups depend only on repositories and lower lookups; nothing depends
on a Service except its own Controller (and orchestrating services at the top). That makes the graph
a DAG:

```
Controller → Service → LookupService → Repository
                 ↘ other LookupServices ↗
```

Hard rules that keep it a DAG:
1. A LookupService must **never** inject a `*Service` (write service) — only repos, `MongoTemplate`,
   and other LookupServices.
2. LookupService → LookupService edges go one direction only (e.g. `GroupLookup → UserLookup`, never
   back). If two lookups need each other, move the shared query into the lower one or into the
   service that needs both.
3. Service → Service injection is a smell. If `AService` needs data from B, inject `BLookupService`.
   If it needs B's *side effect* (e.g. create a group when an event is created), that's acceptable
   only top-down; never let B inject A back.
4. `@Lazy` is a last resort, only at infrastructure boundaries (e.g. WebSocket handler ↔ notification
   service), always with a comment naming the cycle it breaks. Never use it to paper over a
   feature-level cycle — restructure via a LookupService instead.

## 3. Controller rules

- `@RestController` + `@RequestMapping("/<feature>")`.
- First line of every authenticated handler: `val requesterId = requireAuth()`.
- Request DTOs: nested `data class` in the controller with `jakarta.validation` annotations
  (`@field:NotBlank`, `@field:Size`, ...) consumed via `@Valid @RequestBody`.
- Validate every id string before `ObjectId(id)`: `require(ValidationUtils.validateObjectId(id)) { "Invalid id" }`
  (the exception handler maps `IllegalArgumentException` → 400).
- Return `*Response` DTOs via `toXResponse()`, never raw entities.
- No business logic, no repository access.

## 4. Service rules

- Constructor injection only, `private val`.
- Authorization lives here: every method taking `requesterId` must compare it to the resource's
  owner/participants before reading or mutating — recording `updatedBy` is not authorization.
- Throw `ResponseStatusException(HttpStatus.X, "...")` for 403/404/409; use `require(...)` for 400.
- Wrap contended read-modify-write in `withOptimisticRetry { }` (entity has `@Version`).
- Audit-worthy actions: `loggingService.log(userId, LogType.X)`; add the enum value.
- Realtime/push goes through one notification service only — see `spring-realtime-push`.

## 5. Entity & model conventions

- `@Document("<plural_snake_or_lower>")` entity, `@Id val id: ObjectId = ObjectId.get()`.
- Always add a short `@TypeAlias("x")` so `_class` doesn't store the fully-qualified class name —
  otherwise moving/renaming the class breaks reading old documents.
- `createdAt`/`updatedAt` (`Instant`), `updatedBy: ObjectId` for user-editable data.
- Mongo TTL indexes only work on BSON Dates. `java.time.Instant` maps to a Date; `kotlin.time.Instant`
  is stored as a subdocument unless you register a converter — then `@Indexed(expireAfter=...)` is
  silently inert and you need a `@Scheduled` cleanup task instead.
- Anything clients sync: soft delete `deleted: Boolean = false` (+ `deletedAt`) — see
  `spring-delta-sync-endpoint`.
- Contended documents: `@Version val version: Long? = null` for optimistic locking.
- Always a separate `XResponse` DTO + `fun X.toXResponse()` mapper in `model/`.
- Polymorphic responses: sealed class + `@JsonTypeInfo(use = NAME, include = PROPERTY, property = "_class")`
  + `@JsonSubTypes` — register every subtype in both places in the same change.
- Enums for status/type fields, stored as strings.

## 6. Security package (`core/security/`)

Create it whenever the app has authenticated endpoints. Standard contents (full working code
lives in the `spring-boot-project-init` skill, `examples/security.md` — use that skill to add it):

| File | Purpose |
|---|---|
| `SecurityConfig.kt` | Stateless filter chain, CSRF off, explicit `permitAll` allowlist, everything else `authenticated()`, 401 entry point |
| `JwtService.kt` | Issue/validate access + refresh tokens, `type` claim per token kind |
| `JwtAuthFilter.kt` | `OncePerRequestFilter`, sets principal = userId hex string |
| `RequireAuth.kt` | top-level `requireAuth(): ObjectId` (+ `optionalAuth()`) |
| `HashEncoder.kt` | BCrypt wrapper |
| `AdminGuard.kt` | only if there is an admin surface: role checked from DB, 404 for non-admins |
| `ratelimit/` | only if rate limiting is needed (bucket4j + Redis filter after the JWT filter) |

Auth endpoints (login/register/refresh) live in a feature package `authentication/`, not in
`core/security/`.

## 7. Checklist: adding a feature

1. `<feature>/model/<Entity>.kt` + `<Entity>Response.kt` (+ mapper).
2. `repository/<Entity>Repository.kt` (`MongoRepository<Entity, ObjectId>`).
3. `<feature>/<Feature>LookupService.kt` owning the repository.
4. `<feature>/<Feature>Service.kt` using the lookup.
5. `<feature>/<Feature>Controller.kt`.
6. New public route? Add it explicitly to `SecurityConfig` permitAll — otherwise leave it authenticated.
7. Optional follow-ups: `spring-realtime-push`, `spring-delta-sync-endpoint`,
   `spring-endpoint-security-check`.

## 8. Checklist: new project

Use the `spring-boot-project-init` skill — it bootstraps the application class with
`@EnableMongoRepositories`, `repository/`, `core/GlobalExceptionHandler`, and optionally
`core/security/` (JWT auth) and the WebSocket endpoint. Then add `util/` basics from
`references/core-and-util.md` as needed and features via §7.
