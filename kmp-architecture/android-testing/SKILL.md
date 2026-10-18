---
name: android-testing
description: |
  Testing patterns for Android/KMP - ViewModel unit tests with JUnit5, Turbine, AssertK, UnconfinedTestDispatcher, fake repositories, SavedStateHandle, and Compose UI tests. Use this skill ONLY when the user explicitly asks for testing. Do not proactively suggest tests or add test infrastructure. Trigger on phrases like "write a test", "unit test the ViewModel", "test a repository", "Turbine", "fake repository", "UnconfinedTestDispatcher", "runTest", "ComposeTestRule", or "JUnit5".
---

> **Important:** This skill should ONLY be applied when the user explicitly asks for testing. Do not proactively suggest tests, add test dependencies, or create test infrastructure.

# Android / KMP Testing

## Stack

| Concern | Library |
|---|---|
| Test framework | JUnit5 |
| Assertions | AssertK |
| Flow / StateFlow testing | Turbine |
| Coroutine testing | `kotlinx-coroutines-test` + `UnconfinedTestDispatcher` |
| UI testing | `ComposeTestRule` |

---

## Examples

Full code examples live in `examples/`. Read the matching file before writing tests:

| Topic | File |
|---|---|
| ViewModel test setup, Turbine state/event tests, fakes, `SavedStateHandle`, dispatcher injection | `examples/viewmodel-tests.md` |
| Compose UI tests, robot pattern | `examples/compose-ui-tests.md` |

---

## Rules

- ViewModel tests: `Dispatchers.setMain(UnconfinedTestDispatcher())` in `@BeforeEach`, `Dispatchers.resetMain()` in `@AfterEach`.
- Test `StateFlow` and event `Flow` with Turbine (`.test { awaitItem() }`).
- Prefer **fakes** (simple in-memory implementations) over mocks — fakes are simpler and catch more real bugs.
- `SavedStateHandle` is instantiated directly in tests — no mocking needed.
- Inject `CoroutineDispatcher` only when a class dispatches to a non-main dispatcher AND is directly unit-tested; ViewModels using only `viewModelScope` need none.
- Use the robot pattern when a screen has 3+ UI test cases, shared setup/assertion sequences, or multi-step flows. Every robot function returns `this` (`= apply { }`) for chaining.

---

## What to Test

- Unit-test every ViewModel and any non-trivial domain/data logic.
- Unit-test any logic that is likely to change.
- Use fakes over mocks where possible.
- Write integration tests where DB/network interactions are non-trivial.
- Write E2E Compose tests for critical user flows.
- Use the robot pattern for complex UI/E2E tests with multiple test cases or shared interaction sequences.
