# Previews & Accessibility — Examples

## Previews

Every Screen composable should have at least one meaningful `@Preview` that shows a realistic state:

```kotlin
@Preview
@Composable
private fun NoteListScreenPreview() {
    AppTheme {
        NoteListScreen(
            state = NoteListState(
                notes = listOf(
                    NoteUi("1", "Meeting notes", "Mar 15"),
                    NoteUi("2", "Shopping list", "Mar 14")
                )
            ),
            onAction = {}
        )
    }
}
```

Wrap previews in the app theme so they reflect real appearance. Use realistic sample data, not empty states (unless previewing the empty state specifically).

## Accessibility

Use meaningful `contentDescription` on all interactive or informational visual elements. Always use string resources to allow localization:

```kotlin
Icon(
    imageVector = Icons.Default.Delete,
    contentDescription = stringResource(R.string.cd_delete_note)
)

Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = stringResource(R.string.cd_profile_picture)
)
```

For decorative elements that convey no information, set `contentDescription = null`.
