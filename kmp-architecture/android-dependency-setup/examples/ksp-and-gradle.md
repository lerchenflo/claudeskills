# KSP Wiring & build.gradle.kts Declarations — Examples

## KSP Wiring

Room and Koin annotations require KSP. **Always add KSP automatically when adding Room or Koin annotations** — do not ask.

### Plugins block (in the module's `build.gradle.kts`):

```kotlin
plugins {
    // ... other plugins ...
    alias(libs.plugins.ksp)              // Kotlin Symbol Processing for Room + Koin
    alias(libs.plugins.room)             // Room Gradle plugin for schema export
    alias(libs.plugins.koin.compiler)    // Koin annotation compiler
}
```

### KSP processor dependencies (bottom of the same `build.gradle.kts`):

```kotlin
dependencies {
    // Room KSP compiler — generates DAO implementations at compile time
    ksp(libs.room.compiler)
}
```

### Room schema directory (required for migration support):

```kotlin
room {
    schemaDirectory("$projectDir/schemas")
}
```

## build.gradle.kts — Dependency Declarations

Every `implementation` line gets a comment. Use bundles wherever one exists:

```kotlin
dependencies {
    // DI — Koin for dependency injection
    implementation(libs.bundles.koin)

    // Database — Room for local relational storage with compile-time SQL checks
    implementation(libs.bundles.room)

    // Local storage — DataStore for key-value preferences and typed data
    implementation(libs.bundles.datastore)

    // Async — Coroutines for structured concurrency
    implementation(libs.kotlinx.coroutines)

    // Date/Time — KotlinX Datetime
    implementation(libs.kotlinx.datetime)

    // --- Optional (only if user confirmed) ---

    // Networking — Ktor HTTP client for API calls
    implementation(libs.bundles.ktor)

    // Image loading — Coil for async image loading in Compose
    implementation(libs.coil3.coil.compose)
}
```
