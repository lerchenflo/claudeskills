# Variant B: store images rendered from Compose previews

Variant A (SKILL.md) captures a running emulator and composites with ImageMagick. Variant B renders
the store images in Compose itself, on the JVM, as screenshot tests. No emulator, no navigation, no
pixel-cropping callouts: after a UI change one Gradle task re-renders the whole set at every size.

Use B when the app is Compose (Android or Compose Multiplatform), every screen has a stateless
`<Screen>Screen(state, onAction)` composable, and the set will be refreshed often. Use A when the
screens need live data, real images from a backend, or the app is not Compose.

## Trade-offs to tell the user up front

- The images show **sample state**, not real app data. Each shot needs a rich "store" state (full
  lists, realistic names, no empty sections) - write it once next to the test.
- Pictures (avatars, product photos) must be test resources with a licence that allows store use
  (CC0 / own photos), loaded through a fake image loader or passed as painters.
- Status bar and device frame are drawn in Compose (pinned 9:41, full battery), not captured.
- Gestures (pinch zoom, an open bottom sheet mid-drag) have to be expressed as state.

## Setup (Roborazzi)

Roborazzi renders composables with Robolectric's native graphics and supports Compose Multiplatform
modules through their Android host tests. Check its README for the current version and plugin id
before adding it - do not guess versions.

```kotlin
// module build.gradle.kts (the module that can see all screens, e.g. the app shell)
plugins { id("io.github.takahirom.roborazzi") }
dependencies {
    testImplementation("io.github.takahirom.roborazzi:roborazzi")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose")
    testImplementation("org.robolectric:robolectric")
}
```

Put the store tests in their own test class/package (`storeshots`) so normal test runs can skip them,
and write the output to `storeassets/` like variant A.

## The StoreImage composable

One composable owns the whole canvas; the screen and the callout are slots:

```kotlin
@Composable
fun StoreImage(
    caption: String,
    callout: (@Composable () -> Unit)? = null,
    calloutOffsetY: Dp = 0.dp,          // where the callout floats, relative to the device
    screen: @Composable () -> Unit,
) {
    Box(Modifier.fillMaxSize().background(brandBrush())) {   // brandBrush: theme/icon colours
        Text(caption, /* display font, onPrimary, centred, top band */)
        DeviceFrame(Modifier.align(Alignment.BottomCenter)) {  // rounded bezel + 9:41 status bar
            screen()
        }
        callout?.let { Box(Modifier.align(Alignment.Center).offset(y = calloutOffsetY).scale(1.3f).shadow(24.dp, RoundedCornerShape(24.dp))) { it() } }
    }
}
```

The callout is the **real component** (`TaskCard(task)`, `MedicationSection(meds)`) rendered at a
larger scale, not a crop - so edges are always clean and it stays in sync with the UI.

## One test per image, one size per qualifier

```kotlin
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class StoreShots {
    @Test @Config(qualifiers = "w360dp-h800dp-xxhdpi")           // 1080x2400 Play phone
    fun heute() = captureRoboImage("../storeassets/play/phone/de/01-heute.png") {
        AppTheme { StoreImage("Der ganze Stall.\nAuf einen Blick.", callout = { TaskCard(sampleTask) }) {
            TodayScreen(state = storeTodayState, onAction = {})
        } }
    }
}
```

Pick qualifiers so `dp * density` hits an exact accepted size from `store-sizes.md` (e.g. 1206x2622
= `w402dp-h874dp` at 3x). Verify every output with `magick identify` - a 1px drift is a rejection.
Render a size per test (or parameterise the test over the size list).

## Workflow differences from variant A

- Steps 3-4 (device prep, capture) become: write the store states, ask the user to approve each
  rendered screen - same one-at-a-time rule as step 7.
- Re-render: `./gradlew <module>:recordRoborazzi<Variant>` (or the record property the Roborazzi
  README names for KMP host tests), then review the contact sheet as in step 8.
- Captions live in the test as plain strings; changing one is a one-line diff.
