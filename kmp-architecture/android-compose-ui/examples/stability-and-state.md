# Stability, Recomposition & State Ownership — Examples

## Stability & Recomposition

Strong skipping mode is enabled by default in modern Compose — no explicit opt-in needed.

Only annotate a state data class with `@Stable` when it contains fields the Compose compiler considers unstable (e.g., `List`, `Map`, `Set`, interfaces, or abstract types). If all fields are primitive types, `String`, or other stable types, no annotation is needed.

```kotlin
// Needs @Stable — contains a List (unstable by default)
@Stable
data class NoteListState(
    val notes: List<NoteUi> = emptyList(),
    val isLoading: Boolean = false
)

// No annotation needed — all fields are stable
data class NoteDetailState(
    val title: String = "",
    val body: String = "",
    val isSaving: Boolean = false
)
```

## State Ownership

All state lives in the ViewModel. Do not use `remember` or `rememberSaveable` for application state — that belongs in the ViewModel's `StateFlow` and is surfaced via `collectAsStateWithLifecycle()`.

The only exception is Compose-internal state that the framework requires you to hold in composition, such as `LazyListState`, `ScrollState`, or `PagerState`. For these, use `remember*` as needed:

```kotlin
// Acceptable — Compose-owned UI state
val lazyListState = rememberLazyListState()

// Reacting to Compose-owned state with derivedStateOf
val showScrollToTop by remember {
    derivedStateOf { lazyListState.firstVisibleItemIndex > 5 }
}
```

`derivedStateOf` should only be used in these rare scenarios where Compose-internal state drives a derived value. If the derivation can happen in the ViewModel, it should.

Always collect ViewModel state with lifecycle awareness:

```kotlin
val state by viewModel.state.collectAsStateWithLifecycle()
```

## TextField

Text input state lives in the ViewModel. Every keystroke dispatches an Action:

```kotlin
// In the Screen composable
TextField(
    value = state.title,
    onValueChange = { onAction(NoteEditorAction.OnTitleChange(it)) }
)
```

The ViewModel updates state (and optionally persists to `SavedStateHandle`) in response to the Action — see the **android-presentation-mvi** skill for the full pattern.
