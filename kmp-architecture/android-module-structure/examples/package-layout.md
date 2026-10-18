# Package Layout — Full Reference

## Module declarations

Both modules are declared in `settings.gradle.kts`:

```kotlin
include(":composeApp")
include(":androidApp")
```

`:androidApp` depends on `:composeApp`. All shared logic — features, UI, data, DI — lives in `:composeApp`.

## Full package tree

All shared code lives under `composeApp/src/commonMain/kotlin/<root-package>/`:

```
app/                — App lifecycle, navigation, theme, logging
├── navigation/     — Route definitions, Navigator, ObserveAsEvents
├── theme/          — SchneaggchatTheme, colors, typography
└── logging/        — LoggingRepository, LogEntry

chat/               — Chat feature
├── domain/         — Domain models (Message, User, Group, etc.)
├── data/           — Repositories, DTOs (@Entity + @Serializable)
└── presentation/   — ViewModels, screen composables, UI components

login/              — Authentication feature
├── domain/
├── data/
└── presentation/

settings/           — User settings feature
├── domain/
├── data/
└── presentation/

games/              — Games feature
└── presentation/   — Game screens + ViewModels

todolist/           — To-do list feature
├── domain/
├── data/
└── presentation/

schneaggmap/        — Map feature
└── presentation/

datasource/         — Shared data access layer
├── database/       — Room @Database, DAOs, type converters
├── network/        — Ktor HttpClient, NetworkUtils, TokenManager, socket
└── preferences/    — DataStore + KSafe encrypted storage

di/                 — Koin DI module definitions
utilities/          — Shared helpers (UiText, AudioPlayer, CryptoUtil, etc.)
sharedUi/           — Reusable Compose components (popups, buttons, loading)
```

## Platform source sets

KMP `expect`/`actual` declarations go in the appropriate source sets:

```
composeApp/src/
├── commonMain/     — Shared code (bulk of the app)
├── androidMain/    — Android-specific implementations
├── iosMain/        — iOS-specific implementations
└── jvmMain/        — Desktop-specific implementations
```
