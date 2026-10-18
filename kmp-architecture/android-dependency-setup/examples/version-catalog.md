# Version Catalog (`libs.versions.toml`) — Full Example

## `[versions]`

```toml
[versions]
# Build tooling
agp = "9.1.0"                          # Android Gradle Plugin
kotlin = "2.3.20"                       # Kotlin compiler
ksp = "2.3.5"                           # Kotlin Symbol Processing — must track Kotlin version

# Compose
composeMultiplatform = "1.10.3"         # JetBrains Compose Multiplatform
composeBom = "2026.03.01"              # AndroidX Compose BOM — pins all Compose artifact versions

# AndroidX
androidx-activity = "1.13.0"            # Activity Compose integration
androidx-lifecycle = "2.10.0"           # Lifecycle-aware components (ViewModel, runtime)

# Database
room = "2.8.4"                          # Room ORM
sqlite = "2.6.2"                        # Bundled SQLite engine

# DI
koin-core = "4.2.0"                     # Koin DI framework
koin-annotations = "4.2.0"             # Koin annotation processor definitions
koin-plugin = "0.6.2"                   # Koin KSP compiler plugin

# Local storage
datastore = "1.2.1"                     # Jetpack DataStore

# Async
kotlinx-coroutines = "1.10.2"          # Coroutines core

# Date/Time
kotlinx-datetime = "0.7.1"             # Multiplatform date/time

# Networking (optional — add only when project needs API calls)
ktor = "3.4.2"                          # Ktor HTTP client

# Image loading (optional — add only when project loads images)
coilCompose = "3.4.0"                   # Coil image loader for Compose

# Serialization — version is tied to the Kotlin plugin, no separate version needed
```

## `[libraries]`

```toml
[libraries]
# --- Database (Room) ---
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }           # Room ORM runtime — entity/DAO definitions
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }         # Room KSP annotation processor — generates DAO impls
sqlite-bundled = { module = "androidx.sqlite:sqlite-bundled", version.ref = "sqlite" }   # Bundled SQLite so behavior is consistent across devices

# --- DI (Koin) ---
koin-core = { module = "io.insert-koin:koin-core", version.ref = "koin-core" }                                     # Core DI container
koin-android = { module = "io.insert-koin:koin-android", version.ref = "koin-core" }                               # Android context integration (startKoin in Application)
koin-androidx-compose = { module = "io.insert-koin:koin-androidx-compose", version.ref = "koin-core" }              # Compose integration
koin-compose-viewmodel = { module = "io.insert-koin:koin-compose-viewmodel", version.ref = "koin-core" }           # koinViewModel() injection in composables
koin-compose-viewmodel-navigation = { module = "io.insert-koin:koin-compose-viewmodel-navigation", version.ref = "koin-core" } # ViewModel scoping tied to nav destinations
koin-annotations = { module = "io.insert-koin:koin-annotations", version.ref = "koin-annotations" }                # Annotation-based Koin module definitions (@Module, @Single, etc.)

# --- Local Storage (DataStore) ---
datastore = { module = "androidx.datastore:datastore", version.ref = "datastore" }                       # Proto DataStore for typed/structured data
datastore-preferences = { module = "androidx.datastore:datastore-preferences", version.ref = "datastore" } # Preferences DataStore for simple key-value pairs

# --- Async (Coroutines) ---
kotlinx-coroutines = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "kotlinx-coroutines" } # Structured concurrency primitives

# --- Date/Time ---
kotlinx-datetime = { module = "org.jetbrains.kotlinx:kotlinx-datetime", version.ref = "kotlinx-datetime" } # Multiplatform date, time, and timezone handling

# --- Networking (Ktor) — only add if project needs network calls ---
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }                                 # Ktor HTTP client core API
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }                             # OkHttp engine (Android)
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }   # Auto JSON serialization of request/response bodies
ktor-client-logging = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }                           # HTTP request/response logging for debugging
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }   # KotlinX Serialization adapter for content negotiation
ktor-client-auth = { module = "io.ktor:ktor-client-auth", version.ref = "ktor" }                                 # Bearer token auth with automatic refresh
ktor-client-websockets = { module = "io.ktor:ktor-client-websockets", version.ref = "ktor" }                     # WebSocket support for real-time communication

# --- Image Loading (Coil) — only add if project loads images ---
coil3-coil-compose = { module = "io.coil-kt.coil3:coil-compose", version.ref = "coilCompose" } # Async image loading and caching for Compose
```

## `[bundles]`

Group libraries that are always used together. Using bundles keeps `build.gradle.kts` files clean:

```toml
[bundles]
# DI — all Koin artifacts needed for a Compose Android app
koin = [
    "koin-core",
    "koin-android",
    "koin-androidx-compose",
    "koin-compose-viewmodel",
    "koin-compose-viewmodel-navigation",
    "koin-annotations",
]

# Database — Room runtime + bundled SQLite engine
room = [
    "room-runtime",
    "sqlite-bundled",
]

# Local storage — both DataStore flavors
datastore = [
    "datastore",
    "datastore-preferences",
]

# Networking — full Ktor client stack (only add when networking is needed)
ktor = [
    "ktor-client-core",
    "ktor-client-okhttp",
    "ktor-client-content-negotiation",
    "ktor-client-auth",
    "ktor-client-logging",
    "ktor-serialization-kotlinx-json",
    "ktor-client-websockets",
]
```

## `[plugins]`

```toml
[plugins]
androidApplication = { id = "com.android.application", version.ref = "agp" }
androidLibrary = { id = "com.android.library", version.ref = "agp" }
composeMultiplatform = { id = "org.jetbrains.compose", version.ref = "composeMultiplatform" }
composeCompiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
kotlinMultiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
room = { id = "androidx.room", version.ref = "room" }
jetbrains-kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
koin-compiler = { id = "io.insert-koin.compiler.plugin", version.ref = "koin-plugin" }
```
