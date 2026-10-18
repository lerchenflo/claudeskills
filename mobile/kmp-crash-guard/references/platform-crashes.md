# Platform crashes: expect/actual, Android (permissions, API levels), iOS (iPhone + iPad)

Crashes that live on **one platform only**, so they survive testing on the other one. Always say
which platform a finding hits.

## Contents
1. expect/actual divergence
2. Android: runtime permissions
3. Android: API-level gated calls (minSdk vs. used API)
4. Android: intents, files, services, components
5. iOS: general (Kotlin/Native + UIKit interop)
6. iOS: iPad-specific
7. Manifest / Info.plist / build-config checks

---

## 1. expect/actual divergence

Go through the `expect` declarations and read **every** actual side by side. Common code trusts
the expect contract, so each actual has to fail in the same way (the same null/throw behaviour).

- **An actual still set to `TODO()`, `error()` or `throw NotImplementedError`** on one platform →
  `NotImplementedError` only there (often iOS, because the dev only tests on Android).
  `actual fun share(...) {}` as an empty stub doesn't crash, but report it as a silent no-op.
- **Divergent null or throw behaviour:**
  - Android `Uri.parse(s)` never returns null, while iOS `NSURL.URLWithString(s)` **returns null
    for strings with spaces, umlauts or other invalid characters** → `!!` or a non-null return
    type crashes only on iOS. Percent-encode first, or return nullable from the expect.
  - Android `SimpleDateFormat.parse` throws `ParseException`, while iOS
    `NSDateFormatter.dateFromString` returns null → common code catches one and crashes on the
    other.
  - `String.format(...)` exists only on JVM/Android. A hand-rolled iOS actual may use
    `NSString.stringWithFormat`, where `%s` with a Kotlin String is **undefined behaviour or a
    crash** (it needs `%@`). On Android, `%d` with a Double → `IllegalFormatConversionException`.
  - File APIs: Android `File.readText` throws `FileNotFoundException`, while iOS
    `NSString.stringWithContentsOfFile` returns null.
  - Exceptions from ObjC/Swift APIs surface as `NSException` on the iOS side and **can't be caught
    by Kotlin try/catch**. They terminate the app (e.g. `NSInvalidArgumentException` from
    inserting nil into NSDictionary or NSArray, or from `objectAtIndex` out of range).
- **Context holders.** A pattern like `lateinit var appContext` or an `object AndroidContext`
  set in `MainActivity.onCreate`, and an actual that reads it:
  - The process can start **without the Activity**: a push notification
    (`FirebaseMessagingService`), a `BroadcastReceiver` (alarm, boot), `WorkManager`, a widget, a
    `ContentProvider`, a quick-settings tile. The actual then reads an uninitialized holder →
    `UninitializedPropertyAccessException`. **Fix:** initialize in `Application.onCreate` (or
    Koin `androidContext` there), not in the Activity.
  - A holder for the **current Activity** (for dialogs, permissions, share, the biometric prompt):
    it's null or stale after rotation, when the app is backgrounded, or when a process restores
    straight into a sub-screen. Showing a dialog on a finished Activity →
    `WindowManager.BadTokenException` / `IllegalStateException: Activity has been destroyed`.
    Hold it weakly, update it on each lifecycle event, and null-check it before use.
- **iOS actuals that touch UIKit off the main thread** (`UIApplication.sharedApplication`,
  presenting a VC, `UIPasteboard`, a haptics generator): calling them from `Dispatchers.Default`
  or `IO` → a Main Thread Checker violation, random crashes, or UI that never shows. Wrap them
  with `withContext(Dispatchers.Main)`.
- **Kotlin/Native pointer interop:** `memScoped`/`alloc` results used after the scope ends,
  `.pointed!!` / `value!!` on an out-parameter the API left null, an `NSError` out-param ignored
  while the result is force-unwrapped. `CPointer` null means failure, so check it.
- **An actual that throws a platform-specific exception type** (`android.os.RemoteException`,
  `java.io.IOException`) that common code can't name → common code catches something narrower
  and misses it. The expect contract should state "returns Result/null", or catch `Exception`.
- **Suspend actuals and Swift callers:** if Swift calls a Kotlin `suspend fun` (or any function)
  that throws something other than `CancellationException` and the function has no
  `@Throws(Exception::class)`, the app **terminates** (Kotlin/Native turns it into a fatal
  error). Every Kotlin API that Swift calls needs `@Throws` or has to never throw.
- **Missing `actual` for one iOS target** (`iosX64`/`iosArm64`/`iosSimulatorArm64`) is a
  compile/link error, not runtime, so you can skip it. But `actual` implementations under
  `iosMain` that use APIs newer than the deployment target crash on older iOS (see §5).

## 2. Android: runtime permissions

For each permission in `AndroidManifest.xml` and each API that needs one: **is it checked right
before use, on every path, including after the user revokes it in Settings?** Runtime permission
state can change while the app is backgrounded (and the process is killed on revoke).

| Permission / API | Crash when missing | API-level notes |
|---|---|---|
| Location (`FusedLocationProviderClient`, `LocationManager.requestLocationUpdates`, `getLastKnownLocation`) | `SecurityException` | API 31+: FINE must be requested **together with** COARSE, and the user can grant only COARSE. Background location (API 29+) is a separate permission, requested after foreground |
| `CAMERA` | `SecurityException` | **If CAMERA is declared in the manifest, even `ACTION_IMAGE_CAPTURE` via an Intent throws without it.** Remove the declaration if only the intent is used, or request it |
| `POST_NOTIFICATIONS` | no crash, notifications are silently dropped on API 33+ | runtime on 33+. Requesting it on < 33 is a no-op. Report as "silent" |
| `SCHEDULE_EXACT_ALARM` / `USE_EXACT_ALARM` (`setExact*`, `setAlarmClock`) | `SecurityException` | API 31+. Check `alarmManager.canScheduleExactAlarms()` (only exists on 31+, so gate with SDK_INT). On API 34+ it's **denied by default** for new installs |
| Bluetooth scan/connect | `SecurityException` | API 31+: `BLUETOOTH_SCAN`/`BLUETOOTH_CONNECT` at runtime. Legacy `BLUETOOTH` + location below 31 |
| Storage | `SecurityException` / `FileNotFoundException (EACCES)` | API 33+: `READ_EXTERNAL_STORAGE` is **always denied** → use `READ_MEDIA_IMAGES/VIDEO` or the Photo Picker. API 29+ scoped storage: writing to arbitrary external paths fails. API 34: partial photo access (`READ_MEDIA_VISUAL_USER_SELECTED`) |
| `READ_CONTACTS`, `READ_CALENDAR`, `RECORD_AUDIO`, `READ_PHONE_STATE` | `SecurityException` | runtime on 23+ |
| `VIBRATE` (normal permission, manifest only) | `SecurityException` | missing from the manifest |
| Foreground service types | `SecurityException` / `MissingForegroundServiceTypeException` | API 34+: `android:foregroundServiceType` **and** `FOREGROUND_SERVICE_<TYPE>` permissions are required; location/camera/mic types also need the runtime permission granted **before** `startForeground` |
| Full-screen intent, `USE_BIOMETRIC`, `NFC` | varies | check the manifest |

Also check:
- The permission launcher (`rememberLauncherForActivityResult`) is launched from a callback or
  effect, **never during composition**. Launching before registration →
  `IllegalStateException: Launcher has not been initialized`.
- The result callback handles **denied** and **permanently denied** (the dialog no longer
  shows) without assuming "granted". Code like `onResult = { startLocation() }` that ignores the
  boolean → `SecurityException`.
- The check happens right **before each use**, not once at app start. The user can revoke the
  permission in Settings while the app is in the background.
- Permissions requested from an expect/actual on iOS: see §6 for the Info.plist usage strings.

## 3. Android: API-level gated calls

Read `minSdk` (in `build.gradle.kts` / `libs.versions.toml`). Any framework API newer than
minSdk called without `if (Build.VERSION.SDK_INT >= X)` or `@RequiresApi` →
`NoSuchMethodError`/`NoClassDefFoundError` on older devices. Lint `NewApi` catches most of these,
so check whether lint is suppressed (`@SuppressLint("NewApi")`, `lint-baseline.xml`,
`abortOnError false`).

Frequent offenders:
- **`MutableList.removeFirst()`/`removeLast()`** compiled against compileSdk 35+ resolves to
  the Java 21 `List` method → **`NoSuchMethodError` on API < 35** (very common, and this includes
  commonMain code compiled for Android and Nav3 `backStack.removeLast()`). Use
  `removeAt(0)`/`removeAt(lastIndex)` or `removeLastOrNull()`.
- `java.time.*` (LocalDate, Instant, DateTimeFormatter) below API 26 without core library
  desugaring → `NoClassDefFoundError`. kotlinx-datetime is fine.
- `NotificationChannel` (26+), `canScheduleExactAlarms` (31+), `getParcelableExtra(key, Class)`
  (33+, the old version is deprecated), `PackageManager.PackageInfoFlags` (33+),
  `registerReceiver(..., flags)` (33+ overload), `Context.getSystemService(Class)` (23+),
  `WindowInsets` APIs, `BiometricManager.Authenticators` combinations
  (DEVICE_CREDENTIAL + BIOMETRIC_STRONG is unsupported on API 28–29 → `IllegalArgumentException`),
  `Settings.ACTION_APP_NOTIFICATION_SETTINGS` (26+), `ACTION_REQUEST_SCHEDULE_EXACT_ALARM` (31+).
- Behaviour changes that crash when you **target** a new SDK (check `targetSdk`):
  - targetSdk 31+: `PendingIntent` without `FLAG_IMMUTABLE`/`FLAG_MUTABLE` →
    `IllegalArgumentException`. Starting a foreground service from the background →
    `ForegroundServiceStartNotAllowedException`. `android:exported` is required on components
    with intent filters (an install failure, not a runtime crash).
  - targetSdk 34+: `registerReceiver` for non-system broadcasts without
    `RECEIVER_EXPORTED`/`RECEIVER_NOT_EXPORTED` → `SecurityException`. A mutable `PendingIntent`
    with an implicit Intent → `IllegalArgumentException`. FGS types (see §2).
  - targetSdk 35+: edge-to-edge is enforced (layout, not a crash).
  - WorkManager expedited work on API < 31 without `getForegroundInfo()` →
    `IllegalStateException`.

## 4. Android: intents, files, services, components

- `startActivity(intent)` for an implicit Intent (open URL, mail, maps, dialer, store, a
  settings page) with **no app to handle it** → `ActivityNotFoundException`. This happens on
  emulators, work profiles, kiosk devices, tablets without a dialer, and devices without the
  Play Store. Compose `LocalUriHandler.openUri` throws `IllegalArgumentException`
  wrapping it. Wrap in try/catch. Also, on API 30+ `resolveActivity()` returns null without a
  `<queries>` manifest entry, so "check first" logic silently disables the feature.
- `startActivity` from a non-Activity context (application context, service) without
  `FLAG_ACTIVITY_NEW_TASK` → `AndroidRuntimeException`.
- Sharing a file with `Uri.fromFile` / `file://` → `FileUriExposedException` (API 24+). Use
  `FileProvider`. FileProvider paths missing in `file_paths.xml` → `IllegalArgumentException:
  Failed to find configured root`. The authority string must match the manifest exactly.
- Forgetting `FLAG_GRANT_READ_URI_PERMISSION` doesn't crash in the app itself, but the receiving
  app fails.
- A `startForegroundService()` without `startForeground()` within ~5–10 s →
  `ForegroundServiceDidNotStartInTimeException` / ANR crash. `startForeground` with a
  notification whose channel doesn't exist → `RemoteServiceException: Bad notification`.
- Showing a dialog, toast, or `Snackbar` host after `onDestroy` → `BadTokenException`.
- Huge Intent extras or Bundles → `TransactionTooLargeException`.
- `Toast.makeText` from a background thread without a Looper → `RuntimeException: Can't toast on
  a thread that has not called Looper.prepare()` (older APIs).
- Clipboard read in the background on API 29+ returns null → NPE if force-unwrapped.

## 5. iOS: general

- **Info.plist usage strings:** accessing camera, photos, location, contacts, calendar,
  microphone, Bluetooth, Face ID, motion or local network **without the matching
  `NS…UsageDescription` key crashes immediately** (a TCC privacy violation SIGABRT), on iPhone
  and iPad alike. Keys to check: `NSCameraUsageDescription`, `NSPhotoLibraryUsageDescription`,
  `NSPhotoLibraryAddUsageDescription` (saving only), `NSLocationWhenInUseUsageDescription`
  (+ `NSLocationAlwaysAndWhenInUseUsageDescription` for background), `NSContactsUsageDescription`,
  `NSCalendarsUsageDescription` (iOS 17: `NSCalendarsFullAccessUsageDescription` /
  `WriteOnly`), `NSMicrophoneUsageDescription`, `NSFaceIDUsageDescription`,
  `NSBluetoothAlwaysUsageDescription`. Map every permission-using actual or library (a
  camera/image picker, maps, a QR scanner, moko-permissions, calf, peekaboo) to its key.
- Unhandled Kotlin exceptions crossing into Swift, or `@Throws` missing (see §1).
- APIs newer than the deployment target (`IPHONEOS_DEPLOYMENT_TARGET` in the pbxproj) called
  without an `#available` / `NSProcessInfo.isOperatingSystemAtLeastVersion` check → a crash on
  older iOS.
- `UIApplication.sharedApplication.keyWindow` (deprecated) is **null with scene-based apps or
  multiple windows**. `windows.first()` can be empty. `rootViewController!!` crashes. Find the
  presenting VC through the active `UIWindowScene`, or pass it from `LocalUIViewController` in
  Compose.
- Presenting a VC while another is already presented: nothing is shown and a warning is logged,
  with no crash. Presenting the **same** VC instance twice → `NSInvalidArgumentException`. Walk
  to `presentedViewController`.
- Kotlin/Native stack is smaller than the JVM's: deep recursion (tree walking, recursive
  parsing) → stack overflow on iOS only.
- The main-thread watchdog: blocking Main for more than ~10 s at launch (sync DB migration,
  `runBlocking` network) → the app is killed (0x8badf00d).
- Memory: large images decoded at full resolution → jetsam kill (no crash log in Kotlin). Seen
  more on older iPads with big screens.
- `NSUserDefaults`/Keychain returning null on first launch or after a reinstall (the Keychain
  survives a reinstall while UserDefaults doesn't, so they get out of sync).

## 6. iOS: iPad-specific

An app that works on iPhone can crash on iPad. Check that the app actually ships to iPad:
`TARGETED_DEVICE_FAMILY` in `iosApp.xcodeproj/project.pbxproj` (`1` = iPhone only, `1,2` =
iPhone + iPad). iPhone-only apps still run on iPad in compatibility mode, where the list below
mostly doesn't apply, apart from permission keys and memory.

- **Share sheet / `UIActivityViewController` on iPad → crash** unless you set
  `popoverPresentationController.sourceView` (+ `sourceRect`) or `barButtonItem`:
  `NSGenericException: UIPopoverPresentationController ... should have a non-nil sourceView or
  barButtonItem set before the presentation occurs.` **This is the most common KMP iPad crash:**
  a `share()` actual copied from an iPhone tutorial. Fix: after creating the controller,
  ```kotlin
  controller.popoverPresentationController?.apply {
      sourceView = presenter.view
      sourceRect = CGRectMake(CGRectGetMidX(presenter.view.bounds), CGRectGetMidY(presenter.view.bounds), 0.0, 0.0)
      permittedArrowDirections = 0uL
  }
  ```
- **`UIAlertController` with `UIAlertControllerStyleActionSheet`** → the same popover crash on
  iPad. Set the sourceView/sourceRect, or use `.alert` style on iPad.
- `UIDocumentPickerViewController`, `UIDocumentInteractionController`,
  `UIPrintInteractionController`, and `UIImagePickerController` with `.photoLibrary` on older iOS:
  these present as popovers on iPad and need an anchor too.
- **Orientation:** if Info.plist `UISupportedInterfaceOrientations~ipad` lists all four
  orientations but code (`supportedInterfaceOrientations` override, `ComposeUIViewController`
  config, a lock helper) returns a set with **no overlap** with the plist →
  `UIApplicationInvalidInterfaceOrientation` crash. On iPad, multitasking (Split View / Slide Over
  / Stage Manager) requires all four orientations **or** `UIRequiresFullScreen = YES`; otherwise
  App Store validation fails.
- **Window size changes at runtime** (Split View, Slide Over, Stage Manager resizing, external
  display): widths shrink to ~320 pt or grow to 1366 pt. Layout math that assumed phone widths
  hits §7/§8 of the common catalog: `coerceIn(min, available)` with available < min, negative
  padding from `(screenWidth - fixedWidth) / 2`, `GridCells.Fixed(width / itemWidth)` with 0
  columns → `IllegalArgumentException`. Also a `LazyVerticalGrid` with
  `GridCells.Adaptive(minSize)` larger than the width is fine, but `Fixed(0)` crashes.
- **Multiple scenes/windows** (if `UIApplicationSupportsMultipleScenes` is set): code assuming a
  single `keyWindow`/rootViewController, or singletons holding one VC. Two windows of the same
  app then share state.
- **Hardware differences:** no telephony, so `tel:`/`sms:` URLs fail. `canOpenURL` returns false
  and `openURL` does nothing, with no crash, but `!!` on the result of a "which app handles this"
  lookup does. Some iPads lack a rear flash, GPS (Wi-Fi models, so location is coarse and can
  time out), or cellular. Code that assumes `AVCaptureDevice.defaultDeviceWithMediaType(...)` is
  non-null, or that a specific camera position exists, → a null crash.
- Hardware keyboard and pointer: `onKeyEvent`/focus code paths only run on iPad with a keyboard.
  Check them for the usual null and index issues.
- Stage Manager / external display: `UIScreen.mainScreen` bounds don't equal the window bounds,
  so code that sizes by screen instead of window gives wrong layouts (and negative sizes, see
  above).

## 7. Manifest / Info.plist / build-config checks

Read these files once per audit. They decide whether whole classes of findings apply.

| File | Look for |
|---|---|
| `androidApp/src/main/AndroidManifest.xml` (+ `composeApp/.../androidMain/AndroidManifest.xml`) | `uses-permission` list vs. runtime checks, `<queries>`, FileProvider, `foregroundServiceType`, `exported` |
| `build.gradle.kts` / `libs.versions.toml` | `minSdk`, `targetSdk`, `compileSdk`, `isCoreLibraryDesugaringEnabled`, lint `abortOnError`/baseline |
| `iosApp/iosApp/Info.plist` | `NS…UsageDescription` keys vs. used features, `UISupportedInterfaceOrientations(~ipad)`, `UIRequiresFullScreen`, `UIApplicationSceneManifest`/`UIApplicationSupportsMultipleScenes` |
| `iosApp/iosApp.xcodeproj/project.pbxproj` | `TARGETED_DEVICE_FAMILY` (iPad shipped?), `IPHONEOS_DEPLOYMENT_TARGET` |
| Swift files in `iosApp/` | calls into Kotlin APIs that can throw (`@Throws` present?), share/alert presenting code |
