# State, Action, Event — Examples

## State

A single data class holding all UI state fields:

```kotlin
data class NoteListState(
    val notes: List<NoteUi> = emptyList(),
    val isLoading: Boolean = false,
    val error: UiText? = null
)
```

Always update state with `.update { }` — never replace the entire flow:

```kotlin
_state.update { it.copy(isLoading = true) }
```

## Action (Intent)

A sealed interface of all user-triggered actions:

```kotlin
sealed interface NoteListAction {
    data object OnRefreshClick : NoteListAction
    data class OnNoteClick(val noteId: String) : NoteListAction
    data class OnDeleteNote(val noteId: String) : NoteListAction
}
```

## Event (one-time side effects)

A sealed interface of one-time side effects (navigation, snackbar):

```kotlin
sealed interface NoteListEvent {
    data class NavigateToDetail(val noteId: String) : NoteListEvent
    data class ShowSnackbar(val message: UiText) : NoteListEvent
}
```
