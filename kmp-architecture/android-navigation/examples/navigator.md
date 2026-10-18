# Navigator, NavigationAction & ObserveAsEvents — Examples

## Navigator Class

`Navigator` lives in `app/navigation/` and wraps navigation actions in a `Channel`:

```kotlin
class Navigator {
    private val _navigationActions = Channel<NavigationAction>()
    val navigationActions = _navigationActions.receiveAsFlow()

    suspend fun navigate(
        destination: Route,
        navigationOptions: NavigationOptions = NavigationOptions()
    ) {
        _navigationActions.send(NavigationAction.Navigate(destination, navigationOptions))
    }

    suspend fun navigateBack(navigationOptions: NavigationOptions = NavigationOptions()) {
        _navigationActions.send(NavigationAction.NavigateBack(navigationOptions))
    }

    data class NavigationOptions(
        val exitPreviousScreen: Boolean = false,
        val exitAllPreviousScreens: Boolean = false,
        val removeAllScreensByRoute: List<Route> = emptyList(),
        val removeAllExceptByRoute: Route? = null
    )
}
```

`Navigator` is registered as a Koin singleton. ViewModels inject it and call `navigate()` / `navigateBack()` from coroutines.

## NavigationAction

```kotlin
sealed interface NavigationAction {
    val navigationOptions: Navigator.NavigationOptions

    data class Navigate(
        val destination: Route,
        override val navigationOptions: Navigator.NavigationOptions = Navigator.NavigationOptions()
    ) : NavigationAction

    data class NavigateBack(
        override val navigationOptions: Navigator.NavigationOptions = Navigator.NavigationOptions()
    ) : NavigationAction
}
```

## ObserveAsEvents Utility

Lifecycle-aware event collector used for one-time navigation events:

```kotlin
@Composable
fun <T> ObserveAsEvents(flow: Flow<T>, onEvent: (T) -> Unit) {
    val lifecycleOwner = LocalLifecycleOwner.current
    LaunchedEffect(key1 = lifecycleOwner.lifecycle) {
        lifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            withContext(Dispatchers.Main.immediate) {
                flow.collect(onEvent)
            }
        }
    }
}
```
