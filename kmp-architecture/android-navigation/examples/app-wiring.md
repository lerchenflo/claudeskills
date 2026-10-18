# App.kt Wiring — Backstacks, NavDisplay, Nested Navigation

`App.kt` sets up backstacks, observes `Navigator` actions, and renders screens via `NavDisplay`.

## Backstacks

The root backstack holds top-level routes. Features with sub-navigation (Settings, Games) get their own backstacks:

```kotlin
val rootBackStack = rememberNavBackStack(
    configuration = SavedStateConfiguration {
        serializersModule = SerializersModule {
            polymorphic(NavKey::class) {
                subclass(Route.Login::class, Route.Login.serializer())
                subclass(Route.ChatSelector::class, Route.ChatSelector.serializer())
                subclass(Route.Settings::class, Route.Settings.serializer())
                subclass(Route.Games::class, Route.Games.serializer())
                // ... all top-level routes
            }
        }
    },
    Route.AutoLoginCredChecker // initial route
)

val settingsBackStack = rememberNavBackStack(
    configuration = SavedStateConfiguration {
        serializersModule = SerializersModule {
            polymorphic(NavKey::class) {
                subclass(Route.Settings.SettingsScreen::class, Route.Settings.SettingsScreen.serializer())
                subclass(Route.Settings.UserSettings::class, Route.Settings.UserSettings.serializer())
                // ... all Settings sub-routes
            }
        }
    },
    Route.Settings.SettingsScreen
)
```

## Observing Navigation Actions

```kotlin
val navigator = koinInject<Navigator>()

ObserveAsEvents(flow = navigator.navigationActions) { action ->
    val options = action.navigationOptions

    if (options.exitPreviousScreen && rootBackStack.size > 1) {
        rootBackStack.removeAt(rootBackStack.size - 1)
    }
    if (options.exitAllPreviousScreens) {
        rootBackStack.clear()
    }

    when (action) {
        is NavigationAction.Navigate -> rootBackStack.add(action.destination)
        is NavigationAction.NavigateBack -> {
            if (rootBackStack.size > 1) rootBackStack.removeAt(rootBackStack.size - 1)
        }
    }
}
```

## NavDisplay with Entry Provider

```kotlin
NavDisplay(
    backStack = rootBackStack,
    entryDecorators = listOf(
        rememberSaveableStateHolderNavEntryDecorator(),
        rememberViewModelStoreNavEntryDecorator()
    ),
    entryProvider = entryProvider {
        entry<Route.Login> { LoginScreen() }
        entry<Route.ChatSelector> { Chatauswahlscreen() }
        entry<Route.Chat> { ChatScreen() }

        // Nested NavDisplay for features with sub-navigation
        entry<Route.Settings> {
            NavDisplay(
                backStack = settingsBackStack,
                entryProvider = entryProvider {
                    entry<Route.Settings.SettingsScreen> { SettingsScreen(...) }
                    entry<Route.Settings.UserSettings> { UserSettings(...) }
                }
            )
        }
    }
)
```

## Sub-navigation within nested backstacks

Inside a nested `NavDisplay`, navigate by directly manipulating the feature's backstack:

```kotlin
// Navigate forward
settingsBackStack.add(Route.Settings.UserSettings)

// Navigate back
if (settingsBackStack.size > 1) {
    settingsBackStack.removeAt(settingsBackStack.size - 1)
}
```

To exit the entire feature sub-navigation back to the root, use the `Navigator`:

```kotlin
scope.launch { navigator.navigateBack() }
```
