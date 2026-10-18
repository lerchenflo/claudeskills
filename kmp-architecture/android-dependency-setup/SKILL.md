---
name: android-dependency-setup
description: |
  Dependency setup, version catalog, KSP wiring, and bundle management for Android projects. Use this skill whenever adding a new dependency, setting up a new project's dependencies, configuring libs.versions.toml, adding KSP processors, creating dependency bundles, or deciding which libraries to include. Trigger on phrases like "add a dependency", "set up dependencies", "version catalog", "libs.versions.toml", "add Room", "add Koin", "add Ktor", "add Coil", "add DataStore", "KSP setup", "dependency bundle", "new project setup", "what libraries do I need", or "configure gradle".
---

# Android Dependency Setup

## Core Philosophy

- **Version catalog only** — all versions and dependency coordinates live in `libs.versions.toml`. Zero hardcoded versions in build files.
- **Bundle related dependencies** — group libraries that are always used together into `[bundles]`.
- **Comment every dependency** — every `implementation(...)` line in a build file gets a short comment explaining *why* it is there.
- **Ask before adding optional libraries** — only add what the project actually needs. See "Optional Dependencies" below.
- **Use the latest version you know** — but always remind the user that versions may be outdated and they must verify before syncing.

---

## IMPORTANT: After Any Dependency Change

After adding or changing dependencies, **always** tell the user:

1. "Please verify all versions in `libs.versions.toml` are the latest stable releases."
2. "Run a Gradle sync before building."

**Do NOT attempt to build or run the project yourself** — let the user sync and verify first.

---

## Examples

Full code examples live in `examples/`. Read the matching file before writing config for that topic:

| Topic | File |
|---|---|
| Complete `libs.versions.toml` — `[versions]`, `[libraries]`, `[bundles]`, `[plugins]` | `examples/version-catalog.md` |
| KSP wiring (plugins, `ksp(...)`, Room schema dir), `build.gradle.kts` dependency declarations | `examples/ksp-and-gradle.md` |
| Full KMP DataStore + PreferenceManager setup (common factory, per-platform factories, Koin wiring, common error, checklist) | `examples/datastore-setup.md` |

---

## Base Dependencies (Always Add — No Questions Asked)

These go into every new project automatically:

| Library | Why |
|---|---|
| **Koin** (core, android, compose, viewmodel, annotations) | Dependency injection — constructor-based, lightweight, Compose-native |
| **DataStore** (datastore + datastore-preferences) | Local key-value storage, replacing SharedPreferences |
| **KotlinX Serialization** (plugin only for base; json lib added with Ktor) | JSON serialization for navigation args, local storage, API responses |
| **Room** (runtime + sqlite-bundled) | Local relational database with compile-time SQL verification |
| **KSP** | Annotation processing for Room and Koin — added automatically whenever Room is added |
| **KotlinX Coroutines** | Structured concurrency and async programming |
| **KotlinX Datetime** | Date and time handling |

---

## Optional Dependencies (Ask the User First)

Before adding any of these, **ask the user explicitly**:

| Library | Question to ask |
|---|---|
| **Coil** | "Will this project load images from network or local storage?" |
| **Ktor** (client + auth + logging + websockets + content-negotiation) | "Does this project need network/API calls?" |
| **Compose Navigation** | "Does this project use multi-screen navigation?" |

If the user says yes, add the full bundle (not individual libraries). If they say no, do not add it.

For any dependency not listed above, **ask the user** before adding it. Never silently add a dependency.

---

## KSP Rules

- Room and Koin annotations require KSP. **Always add KSP automatically when adding Room or Koin annotations** — do not ask.
- Add `alias(libs.plugins.ksp)`, `alias(libs.plugins.room)`, `alias(libs.plugins.koin.compiler)` plugins and `ksp(libs.room.compiler)` processor.
- Room schema directory (`room { schemaDirectory("$projectDir/schemas") }`) is required for migration support.

---

## Adding a Single New Dependency (Step by Step)

When adding a dependency that is not in the base or optional lists above:

1. Add the version to `[versions]` with a comment describing the library.
2. Add the library entry to `[libraries]` with a comment explaining its purpose.
3. If there are related libraries, create or extend a `[bundles]` entry.
4. If a Gradle plugin is required, add it to `[plugins]`.
5. Add `implementation(libs.xyz)` or `implementation(libs.bundles.xyz)` in the module's `build.gradle.kts` with a comment.
6. If KSP is required, add the processor with `ksp(libs.xyz.compiler)`.
7. **Remind the user**: "Please verify this is the latest stable version and run a Gradle sync."

---

## Checklist: New Project Dependency Setup

- [ ] Create `libs.versions.toml` with all base versions, libraries, bundles, and plugins (see `examples/version-catalog.md`)
- [ ] Add base dependencies: Koin, DataStore, KotlinX Serialization, Room, Coroutines, KotlinX Datetime
- [ ] Wire KSP for Room and Koin annotations (see `examples/ksp-and-gradle.md`)
- [ ] Ask user: "Will this project load images from network or local storage?" — if yes, add Coil
- [ ] Ask user: "Does this project need network/API calls?" — if yes, add Ktor bundle
- [ ] Ask user about any other project-specific dependencies
- [ ] Remind user to verify all versions are the latest stable releases
- [ ] Remind user to run Gradle sync before building
- [ ] Do NOT build or run — let the user sync and verify first

---

## Checklist: Adding a Dependency to an Existing Project

- [ ] Add version to `[versions]` in `libs.versions.toml` with a comment
- [ ] Add library to `[libraries]` with a comment explaining its purpose
- [ ] If related libraries exist, add to or create a `[bundles]` entry
- [ ] If a Gradle plugin is needed, add to `[plugins]`
- [ ] Add `implementation(...)` in the module's `build.gradle.kts` with a comment
- [ ] If KSP is required, add the processor dependency
- [ ] Remind user to verify the version and run Gradle sync
- [ ] Do NOT build or run
