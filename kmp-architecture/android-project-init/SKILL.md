---
name: android-project-init
description: |
  Interactive project initialization wizard for Kotlin Multiplatform / Compose Multiplatform projects. Bootstraps all infrastructure (dependencies, modules, navigation, networking, database, preferences, DI, error handling) after the IDE wizard creates a bare KMP project. Use this skill whenever setting up a new project's infrastructure, bootstrapping a KMP project, or configuring the initial architecture. Trigger on phrases like "initialize project", "bootstrap project", "set up new project", "init project", "project init", "scaffold infrastructure", "new KMP project setup", "set up from scratch", or "configure new project".
---

# KMP Project Initialization Wizard

This skill runs an interactive interview that bootstraps all infrastructure for a new KMP project. It assumes the IDE wizard already created the bare project (Gradle files exist). Every piece of generated code delegates to the specialized architecture skills — this skill orchestrates, it does not define patterns.

---

## Examples

| Topic | File |
|---|---|
| Full plan template presented to the user for approval | `examples/plan-template.md` |

---

## Step 1: Auto-Detection

Before asking anything, silently read these files to detect project basics:

- `settings.gradle.kts` — `rootProject.name`, included modules
- Root `build.gradle.kts` — applied plugins
- Main module `build.gradle.kts` (usually `composeApp/`) — target platforms, namespace/package, existing dependencies
- `gradle/libs.versions.toml` — whether a version catalog exists and what it already contains

Use detected values as defaults. Do not ask for information you can read.

---

## Step 2: Interview

Ask questions using `AskUserQuestion`. Batch up to 4 questions per call. Skip questions where the answer was auto-detected (just confirm). Skip follow-ups for infrastructure the user declined.

### Round 1 — Project Basics

Only ask what could NOT be detected. If everything was detected, condense into a single confirmation.

1. **Project name and package** — "I detected project name `X` with package `Y`. Is this correct?"
2. **Target platforms** — "I detected targets: [Android, iOS, Desktop]. Correct?"
3. **Module strategy** — "Multi-module structure (`:core:*`, `:feature:*`) or single-module with package-based organization?"
4. **App description** — "In one sentence, what does this app do?"

### Round 2 — Infrastructure Choices

4 questions covering the main decisions:

1. **Navigation** — "Do you need multi-screen navigation? (Jetpack Navigation 3 with type-safe routes)"
2. **Networking** — "Does this project need network/API calls?"
3. **Database** — "Do you need a local database? (Room + KSP)"
4. **Preferences** — "Do you need local key-value preferences? (DataStore)"

### Round 3 — Patterns and Extras

Up to 4 questions:

1. **Error handling** — "Set up the typed Result wrapper + DataError pattern? (Recommended if you have network or DB calls)"
2. **Image loading** — "Will this project load images from network or local storage? (Coil)"
3. **Initial features** — "Name 0-3 features to scaffold (e.g., auth/login, settings, main list)"
4. **Testing** — "Set up testing infrastructure? (JUnit5, Turbine, AssertK)"

### Conditional Follow-ups

Only ask these if the user's prior answers require more detail:

- If **networking = yes**: "Authenticated + non-authenticated HTTP clients? Bearer token auth with refresh? WebSocket support?"
- If **preferences = yes**: "Do you need encrypted/secure storage (KSafe) for tokens or secrets?"
- If **features named**: "For each feature, briefly describe the screens (e.g., 'auth — login + register')"

---

## Step 3: Present the Plan

After all questions, present the structured plan from `examples/plan-template.md` for approval. Wait for explicit approval before generating any code.

---

## Step 4: Generate Code

After approval, generate in this exact order. **Follow the referenced skill for every piece of code.**

### Phase 1: Dependencies

Follow **android-dependency-setup** skill:
- Create or update `gradle/libs.versions.toml` with all needed versions, libraries, bundles, plugins
- Only include dependencies the user confirmed
- Update module `build.gradle.kts` files to use the catalog entries

### Phase 2: Module Structure (if multi-module)

Follow **android-module-structure** skill:
- Create module directories with `build.gradle.kts`
- Update `settings.gradle.kts`
- Wire inter-module dependencies

### Phase 3: Error Handling (if selected)

Follow **android-error-handling** skill:
- `Result<T, E>` sealed interface + extension helpers
- `DataError` sealed interface with Network and Local variants
- `UiText` sealed interface for UI error mapping

### Phase 4: Networking (if selected)

Follow **android-data-layer** skill:
- `HttpClientFactory` or `createHttpClient()` function
- Safe call helpers (`safeCall`, `responseToResult`)
- If authenticated: Bearer token auth with token storage
- If WebSockets: WebSocket client configuration
- Platform-specific HTTP engines (expect/actual)

### Phase 5: Database (if selected)

Follow **android-data-layer** skill:
- Room `@Database` abstract class with `@ConstructedBy`
- KSP wiring for Room compiler in build files
- Schema export directory configuration
- Platform-specific database builder (expect/actual)
- Type converters class (if needed)

### Phase 6: Preferences (if selected)

Follow **android-dependency-setup** skill (`examples/datastore-setup.md`):
- DataStore factory function (expect/actual for file path)
- `PreferenceManager` class with typed preference keys
- If encrypted: KSafe setup for secrets/tokens

### Phase 7: DI

Follow **android-di-koin** skill:
- Shared Koin module with all infrastructure singletons (database, HTTP clients, repositories, preferences)
- Platform-specific modules (expect/actual) for database builder, HTTP engine, DataStore
- ViewModel registrations for any scaffolded features
- `startKoin` wiring in Application class / app entry point

### Phase 8: Navigation (if selected)

Follow **android-navigation** skill:
- `Route` sealed interface with nested routes for each feature
- `Navigator` class with navigation event flow
- `NavigationAction` sealed interface
- `ObserveAsEvents` composable helper
- Feature nav graph extensions
- `NavHost` / `NavDisplay` setup in the root `App` composable

### Phase 9: Feature Scaffolding (if requested)

For each feature, follow the full skill stack:
- **Domain**: models, repository interfaces — per **android-error-handling**
- **Data**: repository implementations, DTOs, mappers, data sources — per **android-data-layer**
- **Presentation**: State, Action, Event, ViewModel, Root + Screen composables — per **android-presentation-mvi** + **android-compose-ui**
- **DI**: register in Koin module — per **android-di-koin**
- **Navigation**: add route + nav graph — per **android-navigation**

### Phase 10: Testing (if selected)

Follow **android-testing** skill:
- Add test dependencies to version catalog and module build files
- Create coroutine test dispatcher rule
- Create example fake repository if features were scaffolded

---

## Post-Generation Checklist

After all code is generated, **always** tell the user:

1. "Please verify all dependency versions in `libs.versions.toml` are the latest stable releases — my knowledge may be outdated."
2. "Run a Gradle sync before building."
3. "Review the generated code and adjust package names if needed."

**Do NOT attempt to build or run the project** — let the user sync and verify first.

---

## Rules

- **Never assume** — if something is ambiguous, ask. The interview exists to prevent assumptions.
- **Batch questions** — use AskUserQuestion with up to 4 questions per call. Never ask one question at a time when you can batch.
- **Detect before asking** — read Gradle files first. Only ask for what you cannot detect.
- **Respect existing code** — if infrastructure already exists in the project, ask the user if they want to keep or replace it.
- **Follow the skills** — every generated file must follow the patterns in the corresponding architecture skill. Do not invent new conventions.
- **Order matters** — generate dependencies before code that uses them. Generate domain before data before presentation.
- **Single-module adaptation** — if the user chose single-module, use package directories (`feature/auth/domain/`, `feature/auth/data/`, `feature/auth/presentation/`) instead of Gradle modules. Same layering rules, no module boundaries.
