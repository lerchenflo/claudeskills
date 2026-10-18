# Compose UI Tests & Robot Pattern — Examples

## Basic Compose UI Test

Write integration tests where database/network interactions are non-trivial. Write E2E tests for complex user flows using `ComposeTestRule`:

```kotlin
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun noteList_displaysNotes_afterLoad() {
    composeTestRule.setContent {
        NoteListScreen(
            state = NoteListState(notes = listOf(NoteUi("1", "Hello", "Mar 15"))),
            onAction = {}
        )
    }
    composeTestRule.onNodeWithText("Hello").assertIsDisplayed()
}
```

## Robot Pattern (Complex UI / E2E Tests)

For complex end-to-end or multi-step UI tests, use the **Robot Pattern** to separate test intent from Compose interactions. A robot encapsulates all `composeTestRule` interactions for a screen, keeping tests readable and DRY.

### Structure

Every robot function returns `this` so calls can be chained like a builder:

```kotlin
// Robot class — owns all UI interactions for the screen
class NoteListRobot(private val composeTestRule: ComposeContentTestRule) {

    fun setContent(
        state: NoteListState,
        onAction: (NoteListAction) -> Unit = {}
    ) = apply {
        composeTestRule.setContent {
            NoteListScreen(state = state, onAction = onAction)
        }
    }

    fun assertNoteVisible(title: String) = apply {
        composeTestRule.onNodeWithText(title).assertIsDisplayed()
    }

    fun clickNote(title: String) = apply {
        composeTestRule.onNodeWithText(title).performClick()
    }

    fun assertEmptyState() = apply {
        composeTestRule.onNodeWithTag("empty_state").assertIsDisplayed()
    }
}
```

### Usage in Tests

```kotlin
class NoteListScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    private val robot by lazy { NoteListRobot(composeTestRule) }

    @Test
    fun displaysNotes_afterLoad() {
        robot
            .setContent(NoteListState(notes = listOf(NoteUi("1", "Hello", "Mar 15"))))
            .assertNoteVisible("Hello")
    }

    @Test
    fun showsEmptyState_whenNoNotes() {
        robot
            .setContent(NoteListState(notes = emptyList()))
            .assertEmptyState()
    }

    @Test
    fun clickingNote_triggersAction() {
        var clickedId: String? = null
        robot
            .setContent(
                state = NoteListState(notes = listOf(NoteUi("1", "Hello", "Mar 15"))),
                onAction = { if (it is NoteListAction.OnNoteClick) clickedId = it.noteId }
            )
            .assertNoteVisible("Hello")
            .clickNote("Hello")
    }
}
```

**When to use:** Apply the robot pattern when a screen has 3+ UI test cases, when multiple tests share the same setup/assertion sequences, or when testing complex multi-step user flows (e.g., fill form → submit → assert result).
