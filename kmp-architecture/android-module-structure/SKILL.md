---
name: android-module-structure
description: Module layout, dependency rules, and package organization for KMP projects. Use this skill whenever deciding where new code should live, asking "how should I structure this", creating a new feature package, or making any decision about project-level architecture. Trigger on phrases like "set up the project", "add a feature", "how should I structure", "project structure", "build.gradle", "where does X live", or "package organization".
---

# KMP Module & Package Structure

## Core Philosophy

- **Two-module KMP project**: one shared module (`:composeApp`) and one Android entry point (`:androidApp`). This is the default Compose Multiplatform architecture.
- **Package-based feature separation**: features are organized as packages inside `:composeApp`, not as separate Gradle modules.
- **Clean Architecture layers within packages**: each feature package contains `domain/`, `data/`, and `presentation/` sub-packages.
- **Shared code** lives in dedicated top-level packages (`datasource/`, `utilities/`, `sharedUi/`, `di/`).

---

## Module Layout

```
:composeApp        — Shared KMP code (all features, UI, data, DI)
:androidApp        — Android entry point (Application class, MainActivity)
iosApp/            — iOS Xcode project wrapper (not a Gradle module)
```

`:androidApp` depends on `:composeApp`. All shared logic lives in `:composeApp`.

---

## Examples

| Topic | File |
|---|---|
| `settings.gradle.kts`, full package tree, platform source sets | `examples/package-layout.md` |

Read `examples/package-layout.md` when creating new packages or deciding exact placement within the tree.

---

## Rules for Placing Code

| Code type | Where it goes |
|---|---|
| Feature domain model | `<feature>/domain/` |
| Repository interface | `<feature>/domain/` (the feature that holds the implementation) |
| Repository implementation | `<feature>/data/` |
| Feature-specific DTO / Room entity | `<feature>/data/` |
| Feature-specific ViewModel / screen | `<feature>/presentation/` |
| Shared database (Room @Database, DAOs) | `datasource/database/` |
| Shared networking (HttpClient, API calls) | `datasource/network/` |
| Shared preferences (DataStore, tokens) | `datasource/preferences/` |
| Reusable UI components | `sharedUi/` |
| Shared utilities (UiText, formatters) | `utilities/` |
| Koin module definitions | `di/` |
| Navigation routes, Navigator | `app/navigation/` |
| Theme, app-level composables | `app/` |
| Platform-specific implementation (`actual`) | `androidMain/` / `iosMain/` / `jvmMain/` |

**Cross-feature imports go through `domain/` only.** A repository's interface lives in the `domain/` package of the feature that holds its implementation, together with the models it returns; the implementation lives in that feature's `data/`. Every other class that needs it, in the same feature or another one, depends on the interface, never on the implementation. A feature may import another feature's `domain/` (interfaces + models), but never its `data/` or `presentation/`. Shared utilities and UI components still belong in `utilities/` or `sharedUi/`.

---

## Key Libraries

| Concern | Library | Why this library |
|---|---|---|
| DI | Koin | Lightweight, constructor-based, first-class Compose support with `koinViewModel()` |
| Networking | Ktor Client | Kotlin-native HTTP client with coroutines, auth, and WebSocket support |
| Local DB | Room | Compile-time SQL verification, Flow support, auto-migration |
| Preferences | DataStore + KSafe | Type-safe preferences + encrypted storage for tokens |
| Navigation | Jetpack Navigation 3 | `NavDisplay` + `NavBackStack` with `@Serializable` routes |
| Serialization | KotlinX Serialization | Compile-time JSON codec — used by Ktor, Navigation, and DataStore |
| Image loading | Coil | Compose-native, coroutine-based, lightweight image loading and caching |

For detailed version catalog setup, bundles, and KSP wiring, see the **android-dependency-setup** skill.

---

## Checklist: Adding a New Feature

- [ ] Create the feature package under `composeApp/src/commonMain/kotlin/<root-package>/<feature>/`
- [ ] Add `domain/`, `data/`, `presentation/` sub-packages as needed
- [ ] Define `@Serializable` route(s) in `app/navigation/Route.kt`
- [ ] Add screen entry/entries in `App.kt`'s `NavDisplay`
- [ ] Register repositories and ViewModels in `di/Modules.kt`
- [ ] Verify cross-feature imports only reach another feature's `domain/` (no `data/` or `presentation/` imports)
