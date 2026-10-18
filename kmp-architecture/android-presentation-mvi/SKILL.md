---
name: android-presentation-mvi
description: |
  MVI presentation layer for Android/KMP - State, Action, Event, ViewModel, Root/Screen composable split, UI models, UiText error mapping, and process death with SavedStateHandle. Use this skill whenever creating or reviewing a ViewModel, defining screen state, actions, or events, structuring composables, mapping errors to UI strings, or handling process death. Trigger on phrases like "add a ViewModel", "create a screen", "MVI", "state", "action", "event", "screen composable", "UiText", "SavedStateHandle", "ObserveAsEvents", or "UI model".
---

# Android / KMP Presentation Layer (MVI)

## Overview

Every screen has:
1. **State** — a single data class holding all UI state fields.
2. **Action** (Intent) — a sealed interface of all user-triggered actions.
3. **Event** — a sealed interface of one-time side effects (navigation, snackbar).
4. **ViewModel** — holds `StateFlow<State>`, processes `Action`, emits `Event` via `Channel`.

---

## Examples

Full code examples live in `examples/`. Read the matching file before writing code for that topic:

| Topic | File |
|---|---|
| State / Action / Event definitions, `.update { }` | `examples/state-action-event.md` |
| ViewModel implementation, dispatcher rules, `SavedStateHandle` / process death | `examples/viewmodel.md` |
| Root + Screen composable split (single file), event observation, preview | `examples/composables.md` |
| `UiText` (when vs plain `String`), UI models (`<Model>Ui`), mappers | `examples/uitext-and-ui-models.md` |

---

## Rules

### State

- One data class per screen; always mutate via `_state.update { it.copy(...) }` — never replace the flow.

### ViewModel

- `MutableStateFlow` + `asStateFlow()` for state; `Channel` + `receiveAsFlow()` for events.
- Single `fun onAction(action: XAction)` entry point handling all user actions.

### Coroutine Dispatchers

- **Do not inject** `CoroutineDispatcher` unless the class dispatches to a non-main dispatcher AND is directly unit-tested. ViewModels using only `viewModelScope` need no injected dispatchers — tests use `Dispatchers.setMain(UnconfinedTestDispatcher())`.
- Wrap blocking code in `withContext(Dispatchers.IO)`.

### UiText vs String

- `UiText` for anything that is or could be a string resource (error messages, localizable text).
- Plain `String` for always-dynamic values (user names, formatted dates, amounts).

### UI Models

- When a domain model needs UI-specific formatting, create a presentation-layer model suffixed `Ui` with a `toXUi()` mapper.

### Composable Structure

- Root + Screen live in the **same file**.
- Root: `koinViewModel()`, observes events via `ObserveAsEvents`, passes `state` + `onAction` down.
- Screen: only `state` + `onAction`, no ViewModel reference, previewable.
- **Always add a `@Preview` for every MVI Screen composable automatically** — whenever a Screen is created (or an existing one without a preview is modified), add it in the same file without being asked. Private, named `<Screen>ScreenPreview`, realistic sample `State` (not just defaults when defaults render an empty screen), `onAction = {}`, wrapped in the app theme.

### Process Death

- Use `SavedStateHandle` for complex forms / critical input. Persist on each Action, restore in initial state. Only save what truly matters — not the entire state.

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| ViewModel | `<Screen>ViewModel` | `NoteListViewModel` |
| State | `<Screen>State` | `NoteListState` |
| Action | `<Screen>Action` | `NoteListAction` |
| Event | `<Screen>Event` | `NoteListEvent` |
| Root composable | `<Screen>Root` | `NoteListRoot` |
| Screen composable | `<Screen>Screen` | `NoteListScreen` |
| UI model | `<Model>Ui` | `NoteUi`, `TodoItemUi` |

---

## Checklist: Adding a New Screen

- [ ] Define `State`, `Action`, `Event` in `feature:presentation`
- [ ] Implement `ViewModel` in `feature:presentation`
- [ ] Create `<Screen>Root` composable (holds ViewModel, observes events)
- [ ] Create `<Screen>Screen` composable (pure state + onAction, previewable)
- [ ] Add `@Preview` for the Screen (automatic, realistic sample state, app theme)
- [ ] Map any domain errors to `UiText` via extension functions
- [ ] Add `SavedStateHandle` for any form fields that must survive process death
