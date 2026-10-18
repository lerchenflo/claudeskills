# Modifier Extensions & Design System — Examples

## Modifier Extensions

Prefer plain `Modifier` extension functions or `Modifier.Node`-based factories. Do not make modifier extensions `@Composable`:

```kotlin
// Good — plain extension
fun Modifier.shimmerEffect(): Modifier = composed {
    // shimmer implementation
}

// Better — Modifier factory (no composition needed)
fun Modifier.roundedBackground(color: Color, radius: Dp) =
    background(color, RoundedCornerShape(radius))
```

## Design System & Slot APIs

The design system lives in `:core:design-system` (multi-module) or `sharedUi/` (single-module KMP) and contains reusable Compose components, colors, theme, and typography.

Use slot APIs (passing `@Composable` lambdas) primarily for design system components that need flexible content areas:

```kotlin
// Slot API — design system component
@Composable
fun AppCard(
    modifier: Modifier = Modifier,
    header: @Composable () -> Unit,
    content: @Composable () -> Unit
) {
    Card(modifier = modifier) {
        header()
        content()
    }
}
```

Feature-level composables should prefer typed parameters over slots for clarity:

```kotlin
// Feature composable — typed parameters, no slots
@Composable
fun NoteItem(
    note: NoteUi,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) { ... }
```
