---
name: android-data-layer
description: |
  Data layer patterns for Android/KMP - data sources, repositories, DTOs, mappers, Room entities, Ktor HttpClient, safe call helpers, token storage, and offline-first. Use this skill whenever writing or reviewing a data source or repository, creating DTOs or Room entities, writing mappers, setting up the Ktor HttpClient, handling network errors, or implementing token refresh. Trigger on phrases like "create a repository", "create a data source", "add a DAO", "Ktor client", "write a mapper", "DTO", "Room entity", "network call", "token storage", or "offline-first".
---

# Android / KMP Data Layer

## Error Handling

This skill uses `Result<T, E>`, `DataError`, and the extension helpers defined in the **android-error-handling** skill. Refer to that skill for the full `Result` wrapper, `DataError` sealed interface, and `map`/`onSuccess`/`onFailure`/`asEmptyResult` extensions.

---

## Examples

Full code examples live in `examples/`. Read the matching file before writing code for that topic:

| Topic | File |
|---|---|
| Data source / repository interfaces, implementations, mappers | `examples/data-sources-and-repositories.md` |
| Ktor `HttpClientFactory`, safe call usage, token storage | `examples/ktor-client.md` |
| Room DAO naming, full DAO example, migrations | `examples/room-dao.md` |

---

## Data Source vs Repository

- **Data source** — accesses a single data source (local DB, remote API, file system). Most classes in the data layer are data sources.
- **Repository** — combines multiple data sources (e.g., a remote API + a local DB for offline-first). Only use the term "repository" when the class genuinely coordinates multiple sources.

## Domain Layer Contracts

- Pure Kotlin — no Android/framework imports.
- Contains: domain models, data source/repository **interfaces**, error types.
- **Every data source or repository used by a ViewModel must have an interface in `domain`** — enforces that `presentation` never depends on `data`, and enables testing.

## DTOs and Domain Models

- Always separate: DTOs (data layer) ↔ Domain Models (domain layer).
- Domain models never go directly into Room entities or Ktor request/response bodies.
- Mappers are simple extension functions living in the data layer alongside the DTO.

## Implementations

- Name implementations for what makes them unique — never suffix with `Impl` (`RoomNoteDataSource`, `KtorNoteDataSource`, `OfflineFirstNoteRepository`).

## Ktor

- Configure the client once in a factory; accept the engine externally so tests can swap in a mock engine. Inject `HttpClient` via Koin. For KMP, use the platform default engine.
- Use `safeCall` / `responseToResult` helpers and typed `HttpClient.get`/`post`/`delete` extensions — full implementation in the **android-error-handling** skill.

## Token Storage

Store tokens in DataStore (in `core:data` or a dedicated `:core:auth` / `:feature:auth:data` module). The Ktor `Auth` plugin reads/writes tokens and handles 401 refresh automatically.

## Room

- Every read query in two forms: one-shot suspend (`getById`) + reactive Flow (`getByIdAsFlow`). Writes (`@Insert`/`@Update`/`@Delete`) are suspend-only.
- Migrations: prefer auto-migrations; ask the user before heavy manual migrations (or dropping the DB).

## Offline-First (when applicable)

Follow **Room as single source of truth**: fetch from network → persist to Room → expose DB `Flow` to the ViewModel. The ViewModel never observes network responses directly.

This pattern is optional — apply it when the project requires offline support.

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Data source interface | `<Entity><Local/Remote>DataSource` | `NoteLocalDataSource`, `NoteRemoteDataSource` |
| Data source impl | describe what makes it unique | `RoomNoteDataSource`, `KtorNoteDataSource` |
| Repository interface | `<Entity>Repository` (multi-source only) | `NoteRepository` |
| Repository impl | describe what makes it unique | `OfflineFirstNoteRepository` |
| DTO | `<Model>Dto` | `NoteDto` |
| Room entity | `<Model>Entity` | `NoteEntity` |
| Mapper | extension fun on source type | `fun NoteDto.toNote()` |
| DAO one-shot query | `<action><By…>` | `getById`, `getAll`, `getByPassengerId` |
| DAO reactive query | `<action><By…>AsFlow` | `getByIdAsFlow`, `getAllAsFlow` |

---

## Checklist: Adding a New Data Source or Repository

- [ ] Define domain model(s) in `feature:domain`
- [ ] Define data source or repository interface in `feature:domain`
- [ ] Define feature-specific error type(s) in `feature:domain` (implement `Error`) — see **android-error-handling** skill
- [ ] Define DTOs and Room entities in `feature:data`
- [ ] Write mappers as extension functions in `feature:data`
- [ ] Implement data source (single source) or repository (multi-source) in `feature:data`, named for what makes it unique
