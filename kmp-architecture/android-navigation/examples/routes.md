# Route Definitions — Examples

All routes are defined in a single `Route.kt` file as a sealed interface hierarchy:

```kotlin
sealed interface Route : NavKey {

    // Top-level routes
    @Serializable data object Login : Route, NavKey
    @Serializable data object ChatSelector : Route, NavKey
    @Serializable data object Chat : Route, NavKey

    // Nested feature routes (grouped under a parent)
    @Serializable data object Settings : Route, NavKey {
        @Serializable data object SettingsScreen : Route, NavKey
        @Serializable data object UserSettings : Route, NavKey
        @Serializable data object AppearanceSettings : Route, NavKey
    }

    @Serializable data object Games : Route, NavKey {
        @Serializable data object GamesSelector : Route, NavKey
        @Serializable data object DartCounter : Route, NavKey
    }
}
```

Use `data object` for screens with no parameters. For screens that need arguments, use `data class` with `@Serializable` fields — pass IDs, not complex objects:

```kotlin
// Route with arguments — pass IDs, never complex objects
@Serializable data class NoteDetail(val noteId: String) : Route, NavKey
```
