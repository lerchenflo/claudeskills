---
name: android-compose-ui
description: |
  Compose UI patterns for Android/KMP - stability, recomposition, side effects, lazy lists, animations, previews, accessibility, modifier extensions, and design system composables. Use this skill whenever writing or reviewing composables, optimizing recomposition, adding animations, creating previews, writing custom modifiers, structuring a design system, or making any Compose UI decision beyond the MVI/ViewModel layer. Trigger on phrases like "composable", "recomposition", "LaunchedEffect", "Modifier", "LazyColumn", "preview", "animation", "design system", "stability", "contentDescription", "graphicsLayer", "slot API", or "Compose performance".
---

# Android / KMP Compose UI Patterns

## Core Principle

The UI is dumb. Composables render state and forward user actions — nothing more. All state lives in the ViewModel. All logic lives in the ViewModel, domain, or data layer. Compose code should contain zero business logic, zero data transformation, and minimal side effects.

---

## Examples

Full code examples live in `examples/`. Read the matching file before writing code for that topic:

| Topic | File |
|---|---|
| Stability, `@Stable`, state ownership, `derivedStateOf`, TextField | `examples/stability-and-state.md` |
| Side effects, `DisposableEffect`, `LaunchedEffect` | `examples/side-effects.md` |
| Lazy list keys, low-level animations, deferred state reads | `examples/lazy-layouts-and-animations.md` |
| Modifier extensions, design system, slot APIs | `examples/modifiers-and-design-system.md` |
| Previews, `contentDescription` / accessibility | `examples/previews-and-accessibility.md` |

---

## Rules

### Stability & Recomposition

- Strong skipping mode is enabled by default in modern Compose — no explicit opt-in needed.
- Only annotate a state data class with `@Stable` when it contains fields the compiler considers unstable (`List`, `Map`, `Set`, interfaces, abstract types). All-primitive/`String` state needs no annotation.

### State Ownership

- All application state lives in the ViewModel (`StateFlow` + `collectAsStateWithLifecycle()`). Never `remember` / `rememberSaveable` for application state.
- Only Compose-internal state (`LazyListState`, `ScrollState`, `PagerState`) is held with `remember*`.
- `derivedStateOf` only where Compose-internal state drives a derived value. If the derivation can happen in the ViewModel, it should.

### Side Effects

- Avoid when possible — prefer routing through the ViewModel via an Action.
- When truly necessary (lifecycle APIs with no ViewModel equivalent), extract into a dedicated composable.
- `LaunchedEffect` acceptable when genuinely needed; question ViewModel placement first.
- Do not use custom `CompositionLocal`s.

### Lazy Layouts

- Add `key` to lazy items when an obvious unique identifier exists. Don't force it otherwise.

### Animations

- Never animate in a way that recomposes every frame. Use `graphicsLayer`, offset lambdas, `Canvas`, or `animateFloatAsState` + `graphicsLayer`.
- Pass animated values as lambdas (deferred state reads) so the read happens in layout/draw phase, not composition.

### Modifier Extensions

- Plain `Modifier` extension functions or `Modifier.Node`-based factories. Never `@Composable` modifier extensions.

### Design System & Slot APIs

- Slot APIs (`@Composable` lambda parameters) for design system components with flexible content areas.
- Feature-level composables prefer typed parameters over slots.

### Previews

- Every Screen composable gets at least one meaningful `@Preview` with realistic state, wrapped in the app theme. Add it automatically for MVI Screens — never wait to be asked (see **android-presentation-mvi**).

### Accessibility

- Meaningful `contentDescription` (from string resources) on all interactive/informational elements; `null` on decorative ones.

### TextField

- Text input state lives in the ViewModel; every keystroke dispatches an Action. See **android-presentation-mvi** for the full pattern.

---

## Checklist: Writing a Composable

- [ ] No business logic, no data transformation in the composable
- [ ] State from ViewModel via `collectAsStateWithLifecycle()`
- [ ] `@Stable` only where unstable fields exist
- [ ] Lazy items keyed where a unique id is obvious
- [ ] Animations run below the recomposition layer
- [ ] Preview present with realistic data, wrapped in app theme
- [ ] `contentDescription` set (resource string or `null`)
