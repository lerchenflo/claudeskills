---
name: android-navigation
description: |
  Type-safe Navigation 3 for KMP - Route sealed interface, NavDisplay, NavBackStack, Navigator class, nested backstacks, and ObserveAsEvents. Use this skill whenever setting up navigation, defining routes, adding a new screen, navigating between features, or working with backstacks. Trigger on phrases like "set up navigation", "add a route", "navigate between screens", "NavDisplay", "NavBackStack", "type-safe nav", "Navigator", or "add a screen".
---

# KMP Navigation (Navigation 3)

## Principles

- **Type-safe navigation** with `@Serializable` route objects implementing `NavKey`.
- **Single `Route.kt`** sealed interface defines all routes for the entire app.
- **Feature grouping** via nested sealed interfaces (e.g., `Route.Settings.*`, `Route.Games.*`).
- **`NavDisplay`** renders screens based on the current backstack.
- **`Navigator`** class provides a channel-based API for ViewModels to trigger navigation.
- **Nested backstacks** for feature sub-navigation (Settings, Games).
- `data object` for parameterless screens; `data class` with `@Serializable` fields for screens with arguments — pass IDs, not complex objects.
- Every route's serializer must be registered in the owning backstack's `SerializersModule`.

---

## Examples

Full code examples live in `examples/`. Read the matching file before writing code for that topic:

| Topic | File |
|---|---|
| `Route.kt` sealed interface, nested groups, routes with arguments | `examples/routes.md` |
| `Navigator` class, `NavigationAction`, `ObserveAsEvents` utility | `examples/navigator.md` |
| Backstack setup, observing nav actions, `NavDisplay` + entry provider, nested backstacks | `examples/app-wiring.md` |

---

## How Navigation Flows

1. ViewModel injects the `Navigator` Koin singleton and calls `navigate()` / `navigateBack()` from a coroutine.
2. `App.kt` collects `navigator.navigationActions` via `ObserveAsEvents` and mutates the root backstack.
3. `NavDisplay` renders the top of the backstack via its `entryProvider`.
4. Features with sub-navigation get their own backstack + nested `NavDisplay`; inside them, navigate by directly manipulating the feature backstack (`featureBackStack.add(...)` / `removeAt(...)`). Exiting the feature goes through the `Navigator`.

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Route object | `Route.<ScreenName>` | `Route.ChatSelector`, `Route.Settings.UserSettings` |
| Feature group | Nested sealed interface | `Route.Settings { ... }`, `Route.Games { ... }` |
| Navigator | Single Koin singleton | `koinInject<Navigator>()` |
| Backstack variable | `<feature>BackStack` | `rootBackStack`, `settingsBackStack`, `gamesBackStack` |

---

## Checklist: Adding a New Screen

- [ ] Add `@Serializable data object` to `Route.kt` (top-level or nested under feature group)
- [ ] Register the route's serializer in the appropriate `rememberNavBackStack` `SerializersModule`
- [ ] Add `entry<Route.NewScreen> { ... }` in the corresponding `NavDisplay`'s `entryProvider`
- [ ] If navigated from a ViewModel, use `navigator.navigate(Route.NewScreen)`
- [ ] If navigated within a nested backstack, use `featureBackStack.add(Route.NewScreen)`
