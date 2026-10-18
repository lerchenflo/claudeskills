# Root / Screen Composable Split — Examples

Both the Root and Screen composable live in the **same file** (e.g., `NoteListScreen.kt`).

- **Root Composable** (suffixed `Root`) — receives the ViewModel (via `koinViewModel()`) and any callbacks needed for navigation. Observes events. Passes state and `onAction` down.
- **Screen Composable** (suffixed `Screen`) — receives only `state` and `onAction`. No ViewModel reference. Can be previewed independently.

```kotlin
// NoteListScreen.kt — Root + Screen in a single file

@Composable
fun NoteListRoot(
    onNavigateToDetail: (String) -> Unit,
    viewModel: NoteListViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    ObserveAsEvents(viewModel.events) { event ->
        when (event) {
            is NoteListEvent.NavigateToDetail -> onNavigateToDetail(event.noteId)
            is NoteListEvent.ShowSnackbar -> { /* show snackbar */ }
        }
    }

    NoteListScreen(
        state = state,
        onAction = viewModel::onAction
    )
}

@Composable
fun NoteListScreen(
    state: NoteListState,
    onAction: (NoteListAction) -> Unit
) { ... }

// Added automatically with every MVI Screen - realistic sample state, wrapped in the app theme
@Preview
@Composable
private fun NoteListScreenPreview() {
    AppTheme {
        NoteListScreen(
            state = NoteListState(
                notes = listOf(
                    NoteUi(id = "1", title = "Groceries", formattedDate = "Mar 15, 2026"),
                    NoteUi(id = "2", title = "Ideas", formattedDate = "Mar 16, 2026")
                )
            ),
            onAction = {}
        )
    }
}
```
