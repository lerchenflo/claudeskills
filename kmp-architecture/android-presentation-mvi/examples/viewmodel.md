# ViewModel, Dispatchers & Process Death — Examples

## ViewModel

```kotlin
class NoteListViewModel(
    private val noteRepository: NoteRepository
) : ViewModel() {

    private val _state = MutableStateFlow(NoteListState())
    val state = _state.asStateFlow()

    private val _events = Channel<NoteListEvent>()
    val events = _events.receiveAsFlow()

    fun onAction(action: NoteListAction) {
        when (action) {
            is NoteListAction.OnRefreshClick -> loadNotes()
            is NoteListAction.OnNoteClick -> {
                viewModelScope.launch {
                    _events.send(NoteListEvent.NavigateToDetail(action.noteId))
                }
            }
        }
    }

    private fun loadNotes() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            noteRepository.getNotes()
                .onSuccess { notes ->
                    _state.update { it.copy(notes = notes.map { it.toNoteUi() }, isLoading = false) }
                }
                .onFailure { error ->
                    _state.update { it.copy(isLoading = false) }
                    _events.send(NoteListEvent.ShowSnackbar(error.toUiText()))
                }
        }
    }
}
```

## Coroutine Dispatchers

**Do not inject** unless the class is unit-tested and dispatches to a non-main dispatcher. For ViewModel tests, use `Dispatchers.setMain(UnconfinedTestDispatcher())` in test setup.

For blocking code that doesn't support suspension, wrap it:

```kotlin
suspend fun compressImage(bytes: ByteArray): ByteArray = withContext(Dispatchers.IO) {
    // blocking compression logic
}
```

Only inject `CoroutineDispatcher` when:
1. The class dispatches to a non-main dispatcher (e.g., `IO`), AND
2. That class is directly unit-tested.

## Process Death (SavedStateHandle)

When a screen involves complex forms or critical user input, restore essential fields using `SavedStateHandle`:

```kotlin
class NoteEditorViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val noteRepository: NoteRepository
) : ViewModel() {
    private val _state = MutableStateFlow(
        NoteEditorState(
            title = savedStateHandle["title"] ?: "",
            body = savedStateHandle["body"] ?: ""
        )
    )

    fun onAction(action: NoteEditorAction) {
        when (action) {
            is NoteEditorAction.OnTitleChange -> {
                savedStateHandle["title"] = action.title
                _state.update { it.copy(title = action.title) }
            }
        }
    }
}
```

Only save what truly matters after process death — not the entire state.
