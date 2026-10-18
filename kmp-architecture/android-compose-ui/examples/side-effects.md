# Side Effects — Examples

Side effects should be avoided when possible. If something can be handled by the ViewModel through an Action, do that instead of using a side effect in a composable.

When a side effect is truly necessary (e.g., interacting with Android lifecycle APIs that have no ViewModel equivalent), extract it into a dedicated composable to keep the Screen composable clean:

```kotlin
// Extracted into its own composable
@Composable
fun ObserveLifecycle(onStart: () -> Unit, onStop: () -> Unit) {
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_START -> onStart()
                Lifecycle.Event.ON_STOP -> onStop()
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }
}
```

`LaunchedEffect` is acceptable when genuinely needed, but question whether the work belongs in the ViewModel first. Do not use custom `CompositionLocal`s.

## LaunchedEffect usage (when justified)

```kotlin
// Justified — one-time scroll on a Compose-owned state change,
// no ViewModel equivalent exists
LaunchedEffect(state.scrollToTopTrigger) {
    if (state.scrollToTopTrigger) {
        lazyListState.animateScrollToItem(0)
    }
}
```
