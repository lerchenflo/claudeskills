# UiText & UI Models — Examples

## UiText (`core:presentation`)

`UiText` wraps strings that originate from — or could originate from — a string resource:

```kotlin
sealed interface UiText {
    data class DynamicString(val value: String) : UiText
    class StringResource(val id: Int, val args: Array<Any> = emptyArray()) : UiText
}
```

**When to use `UiText`:** For any string that comes from a string resource, could be localized, or might be either a resource or a dynamic value depending on context (e.g., error messages that map to `R.string.*`).

**When to use plain `String`:** For values that are always dynamic and never come from resources — e.g., a user's name, a formatted date, a currency amount. These should be exposed as `String` directly in the state or UI model.

```kotlin
// UiText — error message that maps to a string resource
data class NoteListState(
    val error: UiText? = null
)

// Plain String — always dynamic, never a resource
data class NoteUi(
    val authorName: String,
    val formattedDate: String
)
```

Define `DataError.toUiText()` extension functions in `core:presentation` (or feature `presentation`) that map error enums to `UiText.StringResource` — see the **android-error-handling** skill.

## UI Model (Presentation Model)

When a domain model needs UI-specific formatting (dates, units, currency), create a dedicated UI model in the presentation layer:

```kotlin
data class NoteUi(
    val id: String,
    val title: String,
    val formattedDate: String  // e.g. "Mar 15, 2026"
)

fun Note.toNoteUi(): NoteUi = NoteUi(
    id = id,
    title = title,
    formattedDate = date.format(...)
)
```

UI models are always suffixed with `Ui` (e.g., `NoteUi`, `TodoItemUi`).
