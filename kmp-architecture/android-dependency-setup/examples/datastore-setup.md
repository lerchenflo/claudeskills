# DataStore + PreferenceManager Setup (KMP) — Full Example

DataStore requires a platform-specific file path to store preferences. In a KMP project this means you cannot just create a `DataStore<Preferences>` in `commonMain` — each platform must supply its own path. The pattern below uses a **common factory function** that accepts a path-producing lambda, plus **per-platform factory functions** that call it with the correct OS-level path, plus **per-platform Koin modules** that register the result as a singleton.

## Pattern Overview

1. **`commonMain`** — a `createDataStore(producePath)` factory function and a shared `DATA_STORE_FILE_NAME` constant.
2. **Each platform source set** (`androidMain`, `iosMain`, `jvmMain`) — a factory function that calls `createDataStore()` with the correct platform-specific file path.
3. **Each platform source set** — a Koin module that registers `single<DataStore<Preferences>>` using its platform factory.
4. **`commonMain` shared module** — `Preferencemanager(get(), ...)` resolves `DataStore<Preferences>` from whichever platform module was loaded.
5. **Each platform's `startKoin`** — must include the platform DataStore module alongside the shared module.

## 1. Common Factory Function

File: `commonMain/<project-package>/di/createDataStore.kt`

```kotlin
package <project-package>.di

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import androidx.datastore.preferences.core.Preferences
import okio.Path.Companion.toPath

fun createDataStore(producePath: () -> String): DataStore<Preferences> {
    return PreferenceDataStoreFactory.createWithPath(
        produceFile = { producePath().toPath() }
    )
}

internal const val DATA_STORE_FILE_NAME = "prefs.preferences_pb"
```

## 2. Android Factory

File: `androidMain/<project-package>/di/createAndroidDataStore.kt`

Uses `context.filesDir` for the standard Android files directory.

```kotlin
package <project-package>.di

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences

fun createAndroidDataStore(context: Context): DataStore<Preferences> {
    return createDataStore {
        context.filesDir.resolve(DATA_STORE_FILE_NAME).absolutePath
    }
}
```

## 3. iOS Factory

File: `iosMain/<project-package>/di/createIosDataStore.kt`

Uses Foundation `NSFileManager` to resolve the Documents directory. Requires `@OptIn(ExperimentalForeignApi::class)`.

```kotlin
package <project-package>.di

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import kotlinx.cinterop.ExperimentalForeignApi
import platform.Foundation.NSDocumentDirectory
import platform.Foundation.NSFileManager
import platform.Foundation.NSUserDomainMask

@OptIn(ExperimentalForeignApi::class)
fun iosDatastoreBuilder(): DataStore<Preferences> {
    val documentDir = NSFileManager.defaultManager.URLForDirectory(
        directory = NSDocumentDirectory,
        inDomain = NSUserDomainMask,
        appropriateForURL = null,
        create = false,
        error = null
    )
    val dbFile = documentDir?.path + "/" + DATA_STORE_FILE_NAME
    return createDataStore { dbFile }
}
```

## 4. Desktop / JVM Factory

File: `jvmMain/<project-package>/di/createDesktopDataStore.kt`

Resolves the OS-appropriate application data directory. Replace `<AppName>` with the actual app name.

```kotlin
package <project-package>.di

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import java.io.File

fun desktopDatastoreBuilder(): DataStore<Preferences> {
    val os = System.getProperty("os.name").lowercase()
    val userHome = System.getProperty("user.home")
    val appDataDir = when {
        os.contains("win") -> File(System.getenv("APPDATA"), "<AppName>")
        os.contains("mac") -> File(userHome, "Library/Application Support/<AppName>")
        else -> File(userHome, ".local/share/<AppName>")
    }
    if (!appDataDir.exists()) { appDataDir.mkdirs() }
    val savefile = File(appDataDir, DATA_STORE_FILE_NAME)
    return createDataStore { savefile.absolutePath }
}
```

## 5. Platform Koin Modules

Each platform defines a Koin module that registers `DataStore<Preferences>` as a singleton.

**Android** (`androidMain/<project-package>/di/AndroidModules.kt`):

```kotlin
val androidDataStoreModule = module {
    single<DataStore<Preferences>> { createAndroidDataStore(androidContext()) }
}
```

**iOS** (`iosMain/<project-package>/di/IosModules.kt`):

```kotlin
val iosDatastoreModule = module {
    single<DataStore<Preferences>> { iosDatastoreBuilder() }
}
```

**Desktop** (`jvmMain/<project-package>/di/DesktopModules.kt`):

```kotlin
val desktopDataStoreModule = module {
    single<DataStore<Preferences>> { desktopDatastoreBuilder() }
}
```

## 6. Shared Module Wiring

In the shared Koin module (`commonMain`), inject `DataStore<Preferences>` via `get()`. Koin resolves it from whichever platform module was loaded at startup:

```kotlin
val sharedModule = module {
    single { Preferencemanager(get(), get(), get()) }
    // ...
}
```

## 7. Koin Initialization

Each platform's `startKoin` call **must include the platform DataStore module** alongside the shared module:

```kotlin
// Android
startKoin {
    androidContext(context)
    modules(androidDataStoreModule, sharedModule, /* ... */)
}

// iOS
startKoin {
    modules(iosDatastoreModule, sharedModule, /* ... */)
}

// Desktop
startKoin {
    modules(desktopDataStoreModule, sharedModule, /* ... */)
}
```

## Common Koin Error

> **If you see:** `No definition found for class 'androidx.datastore.core.DataStore'`
>
> **Root cause:** The shared module declares `Preferencemanager(get(), ...)` which calls `get<DataStore<Preferences>>()`, but no platform module has registered that type.
>
> **Fix:** Ensure every platform's `startKoin` includes the platform-specific DataStore module (`androidDataStoreModule`, `iosDatastoreModule`, or `desktopDataStoreModule`).

## Checklist: DataStore Setup for a New KMP Project

- [ ] Add `datastore` and `datastore-preferences` to `libs.versions.toml` (already in base dependencies)
- [ ] Add `implementation(libs.bundles.datastore)` in the module's `build.gradle.kts`
- [ ] Create `commonMain/.../di/createDataStore.kt` with `createDataStore()` factory and `DATA_STORE_FILE_NAME`
- [ ] Create `androidMain/.../di/createAndroidDataStore.kt` with `createAndroidDataStore(context)`
- [ ] Create `iosMain/.../di/createIosDataStore.kt` with `iosDatastoreBuilder()`
- [ ] Create `jvmMain/.../di/createDesktopDataStore.kt` with `desktopDatastoreBuilder()` — replace `<AppName>`
- [ ] Add `androidDataStoreModule` in `androidMain/.../di/AndroidModules.kt`
- [ ] Add `iosDatastoreModule` in `iosMain/.../di/IosModules.kt`
- [ ] Add `desktopDataStoreModule` in `jvmMain/.../di/DesktopModules.kt`
- [ ] Include each platform's DataStore module in its `startKoin { modules(...) }` call
- [ ] In the shared Koin module, inject `DataStore<Preferences>` via `get()` into `Preferencemanager`
