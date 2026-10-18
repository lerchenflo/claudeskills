---
name: android-error-handling
description: |
  Generic Result wrapper, error types, and extension helpers for Android/KMP - Result<T, E>, DataError, EmptyResult, map, onSuccess, onFailure. Use this skill whenever defining error types, creating a Result wrapper, handling success/failure flows, mapping errors, or working with typed errors anywhere in the app (not just data layer — also validation, auth, domain logic). Trigger on phrases like "Result wrapper", "error handling", "DataError", "onSuccess", "onFailure", "EmptyResult", "map result", "error type", "validation error", or "typed errors".
---

# Android / KMP Error Handling

A generic, typed `Result<T, E>` that works across all layers — data, domain, presentation, validation, anywhere a function can succeed or fail with a typed error. `typealias EmptyResult<E> = Result<Unit, E>` for success-without-data.

---

## Examples

Full code lives in `examples/`. Read the matching file before writing code for that topic:

| Topic | File |
|---|---|
| `Result<T, E>` definition + `map`/`onSuccess`/`onFailure`/`asEmptyResult` helpers | `examples/result-wrapper.md` |
| `DataError` (Network/Local), feature-specific errors, `.toUiText()` mapping | `examples/error-types.md` |
| Full Ktor safe call helpers (`safeCall`, `responseToResult`, typed `get`/`post`/`delete`) | `examples/safe-call-helpers.md` |

---

## Rules

- `Result` + extension helpers live in `core:domain`; safe call helpers in `core:data`.
- All helpers return `Result` so they can be chained.
- Feature-specific errors implement `Error`. Multiple validation errors are not supported — always return a single error type per Result.
- Every user-facing error type gets a `.toUiText()` extension: feature-specific errors in the feature's `presentation` module, shared errors (`DataError`) in `core:presentation`. Purely internal errors need no mapping.
- In `safeCall`, always rethrow `CancellationException`.

---

## Exception Handling Philosophy

Never throw exceptions for expected failures — always return `Result.Error`. Catch exceptions at the layer that is responsible for the exception:

| Exception origin | Catch in | Example |
|---|---|---|
| HTTP / network | Data layer | `UnresolvedAddressException` → `DataError.Network.NO_INTERNET` |
| Database / disk | Data layer | `SQLiteFullException` → `DataError.Local.DISK_FULL` |
| Business logic | Domain layer | Invalid input → `Result.Error(ValidationError.TOO_SHORT)` |
| Presentation | Presentation layer | Catch and map to `Result.Error` at that layer |

The layer that owns the exception catches it and converts it to a typed `Result.Error`. Upper layers never see raw exceptions for expected failures.

---

## When to Use What

| Scenario | Error type | Example return |
|---|---|---|
| Network call | `DataError.Network` | `Result<List<NoteDto>, DataError.Network>` |
| Local DB access | `DataError.Local` | `Result<Note, DataError.Local>` |
| Repository (multi-source) | `DataError` (supertype) | `Result<List<Note>, DataError>` |
| Domain validation | Custom `Error` enum | `EmptyResult<PasswordValidationError>` |
| Auth logic | Custom `Error` enum | `Result<User, AuthError>` |

The `Result` wrapper is not limited to the data layer — use it anywhere a function has typed success and failure outcomes.

---

## Checklist: Adding a New Error Flow

- [ ] Define the error type implementing `Error` (feature `domain` or `core:domain`)
- [ ] Return `Result<T, YourError>` / `EmptyResult<YourError>` — never throw for expected failures
- [ ] Catch exceptions at the owning layer, convert to `Result.Error`
- [ ] Add `.toUiText()` if the error is user-facing
- [ ] Chain with `onSuccess`/`onFailure`/`map` at call sites
