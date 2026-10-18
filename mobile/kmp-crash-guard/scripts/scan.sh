#!/usr/bin/env bash
# kmp-crash-guard candidate scanner.
# Prints grep hits grouped by crash category. Hits are CANDIDATES, not findings -
# every one still has to be traced (see references/crash-catalog.md).
#
# Usage: bash scan.sh [path ...]      (default: current directory)
#        MAX=200 bash scan.sh src     (raise per-category line cap, default 60)

set -u
MAX="${MAX:-60}"
PATHS=("$@")
[ ${#PATHS[@]} -eq 0 ] && PATHS=(.)

if command -v rg >/dev/null 2>&1; then
  search() {
    rg -n -P --no-heading --color=never -t kotlin \
      -g '!**/build/**' -g '!**/generated/**' -g '!**/*Test/**' -g '!**/test/**' \
      -g '!**/*UnitTest/**' -g '!**/*.gradle.kts' \
      "$1" "${PATHS[@]}" 2>/dev/null
  }
  files_with() {
    rg -l -P --color=never -t kotlin \
      -g '!**/build/**' -g '!**/generated/**' -g '!**/*Test/**' -g '!**/test/**' \
      -g '!**/*UnitTest/**' "$1" "${PATHS[@]}" 2>/dev/null
  }
else
  search() {
    grep -rnP --include='*.kt' --exclude-dir=build --exclude-dir=generated \
      --exclude-dir='*Test' --exclude-dir=test --exclude-dir='*UnitTest' \
      "$1" "${PATHS[@]}" 2>/dev/null
  }
  files_with() {
    grep -rlP --include='*.kt' --exclude-dir=build --exclude-dir=generated \
      --exclude-dir='*Test' --exclude-dir=test --exclude-dir='*UnitTest' \
      "$1" "${PATHS[@]}" 2>/dev/null
  }
fi

# strip leading whitespace in the code part, drop comment-only lines, cap output
tidy() {
  sed -E 's/^([^:]+:[0-9]+:)[[:space:]]+/\1 /' \
    | grep -vP '^[^:]+:[0-9]+:\s*(//|\*|/\*)' \
    | grep -vP '^[^:]+:[0-9]+:\s*import\s'
}

section() {
  local title="$1" pattern="$2"
  local out count
  out="$(search "$pattern" | tidy)"
  count=$(printf '%s' "$out" | grep -c . || true)
  printf '\n=== %s  (%s hits) ===\n' "$title" "$count"
  [ "$count" -eq 0 ] && return
  printf '%s\n' "$out" | head -n "$MAX"
  [ "$count" -gt "$MAX" ] && printf '... %s more (MAX=%s to see all)\n' "$((count - MAX))" "$count"
}

echo "kmp-crash-guard scan: ${PATHS[*]}"
echo "Candidates only - trace each one before reporting."

section "1 LAZY KEYS (duplicate / unsaveable key)" \
  '(\bkey\s*=\s*\{|\bitem\s*\(\s*key|\bstickyHeader\s*\(|\bitemsIndexed\s*\(|Pager\s*\()'

section "2a NON-NULL ASSERTION !!" '!!'
section "2b UNSAFE CAST (as X)" '(?<![\w?])\bas\s+[A-Z]\w*(?!\?)'
section "2c LATEINIT" '\blateinit\s+var\b'

section "3 EMPTY COLLECTION / MISSING KEY" \
  '\.(first|last|single|reduce|reduceIndexed|random|maxOf|minOf|maxBy|minBy|maxWith|minWith|elementAt|getValue|removeFirst|removeLast|component1)\s*(\(|\{)|\.(max|min)\(\)'

section "4 INDEX / RANGE (out of bounds)" \
  '(\[(0|1|2|i|j|\w*[iI]ndex\w*|[^\]]*size\s*-\s*1|[^\]]*lastIndex)\]|\bsplit\([^)]*\)\s*\[|\.get\(\d+\)|\bsubstring\(|\bsubList\(|\bremoveAt\(|\bchunked\(\s*[a-z]|\bwindowed\(\s*[a-z])'

section "5 PARSING / CONVERSION of external input" \
  '(\.to(Int|Long|Double|Float|Short|Byte|BigDecimal|BigInteger)\(\)|\.parse\(|\bdecodeFrom(String|JsonElement)\b|\.valueOf\(|\benumValueOf\b|\.entries\[|\bRegex\(|\.toRegex\(|\bparseColor\(|\.round(ToInt|ToLong)\(\)|\bLocalDate(Time)?\(\s*[a-z]|\bMonth\(\s*[a-z]|\bfromEpochMilliseconds\b)'

section "6 ARITHMETIC (division by zero -> ArithmeticException / NaN)" \
  '\s[/%]\s*\(?\w*(size|count|Count|total|Total|sum|Sum|days|Days|hours|Hours|minutes|Minutes|len|Length|width|Width|height|Height|max|Max|divisor|n)\b(?!\s*\.\s*to(Float|Double))'

section "7 RANGE ARGS (coerceIn min>max, bad step)" \
  '(\bcoerceIn\s*\(|\bcoerceAtLeast\s*\(|\bcoerceAtMost\s*\(|\bstep\s+[a-z]|\bIntRange\s*\(|\bsteps\s*=\s*[a-z(])'

section "8 COMPOSE LAYOUT ARGS that throw (weight<=0, negative padding/size, maxLines<1, scrollToItem(-1), gradient<2 colors)" \
  '(\.weight\(\s*(?![\d.]+f?\s*[,)])|\b(padding|size|width|height|offset)\([^)]*\s-\s*\w|maxLines\s*=\s*(?!\d|Int\.MAX)|\b(animateS|s)crollTo(Item|Page)\(|Gradient\(|\baddStyle\(|\bSpanStyle\b.*\bstart\b)'

section "9 SAVED STATE (rememberSaveable / SavedStateHandle types, size)" \
  '(\brememberSaveable\b|\bSavedStateHandle\b|\brememberNavBackStack\b|\bsaveable\b)'

section "10 COROUTINES & ERROR HANDLING (uncaught, swallowed cancellation, iOS-blind catch)" \
  '(\bGlobalScope\b|\brunBlocking\b|\brunCatching\b|catch\s*\(\s*\w+\s*:\s*(Throwable|Exception|IOException|SocketTimeoutException|UnknownHostException)\s*\)|\.stateIn\(|\.shareIn\(|\bChannel\s*[<(]|\.first\(\)\s*$|\bwithTimeout\s*\()'

section "11 NETWORK / SERIALIZATION config & body decoding" \
  '(\.body<|\.body\(\)|\bexpectSuccess\b|\bignoreUnknownKeys\b|\bcoerceInputValues\b|\bexplicitNulls\b|\bJson\s*\{|\bHttpClient\s*\()'

section "12 ROOM / DATABASE" \
  '(\bOnConflictStrategy\b|\bfallbackToDestructive|\ballowMainThreadQueries\b|\baddMigrations\b|@Database\s*\(|\bversion\s*=\s*\d)'

section "13 PLATFORM (intents, removeLast on API<35, back stack, iOS interop, DI)" \
  '(\bstartActivity\s*\(|\bopenUri\s*\(|\bIntent\s*\(|\bgetSystemService\b|\bget(Parcelable|Serializable|String|Int)Extra\b|\.removeLast\(\)|\.removeFirst\(\)|\bpopBackStack\b|backStack\.(remove|removeLast|removeAt|clear)|\bNSException\b|@Throws|\bcheckSelfPermission\b|\bgetString\(\s*R\.)'

section "14 EXPLICIT THROWS (reachable from UI?)" \
  '(\bTODO\(|\berror\(\s*"|\brequire(NotNull)?\s*\(|\bcheck(NotNull)?\s*\(|\bthrow\s+\w)'

# Things grep can't see line-by-line: nested scroll containers
echo
echo "=== 15 NESTED SCROLL (files with verticalScroll/horizontalScroll AND a Lazy list - check nesting) ==="
comm -12 \
  <(files_with '\b(vertical|horizontal)Scroll\s*\(' | sort) \
  <(files_with '\bLazy(Column|Row|VerticalGrid|HorizontalGrid|VerticalStaggeredGrid)\b' | sort) \
  | head -n "$MAX"

# DAO single-row queries returning a non-null type
echo
echo "=== 16 ROOM single-row query with non-null return (row missing -> crash) ==="
for f in $(files_with '@Dao\b'); do
  grep -nP 'fun\s+\w+\s*\([^)]*\)\s*:\s*(?!List|Flow|Int\b|Long\b|Boolean\b|Unit\b|Map\b|Set\b)[A-Z]\w*(<[^>]*>)?\s*$' "$f" \
    | sed "s|^|$f:|"
done | head -n "$MAX"

# ---------- platform: expect/actual ----------
echo
echo "=== 17 EXPECT/ACTUAL - actuals that stub, throw or force-unwrap (compare each actual side by side) ==="
for f in $(files_with '\bactual\s+(fun|class|val|var|object|typealias)\b'); do
  grep -nP '(\bTODO\(|\berror\(|\bthrow\s|NotImplemented|!!|\bas\s+[A-Z]\w*(?!\?)|lateinit)' "$f" | sed "s|^|$f:|"
done | tidy | head -n "$MAX"
echo "--- files declaring expect ---"
files_with '\bexpect\s+(fun|class|val|var|object)\b' | head -n "$MAX"

section "18 ANDROID PERMISSIONS / API-LEVEL / TARGET-SDK behaviour" \
  '(Manifest\.permission\.|\bcheckSelfPermission\b|\brequestPermissions?\b|RequestPermission\b|\bSDK_INT\b|@RequiresApi|@SuppressLint\(\s*"NewApi"|\bPendingIntent\.get|\bregisterReceiver\s*\(|\bsetExact\w*\(|\bsetAlarmClock\(|\bcanScheduleExactAlarms\b|\bstartForeground(Service)?\s*\(|\bFileProvider\b|\bUri\.fromFile\b|\bjava\.time\.|\bNotificationChannel\b|\bVibrator\b|\bBiometricManager\b|\bFusedLocation|\bLocationManager\b)'

section "19 iOS / iPad (popover anchors, key window, NSURL nil, UIKit threading, device caps)" \
  '(\bUIActivityViewController\b|\bUIAlertController\b|ActionSheet|\bpopoverPresentationController\b|\bUIDocument(Picker|Interaction)|\bUIImagePickerController\b|\bkeyWindow\b|\brootViewController\b|\bpresentViewController\b|\bNSURL(\.URLWithString|\(string|\.fileURLWithPath)|\bUIApplication\.sharedApplication\b|\bUIScreen\.mainScreen\b|\bAVCaptureDevice\b|\bUIDevice\.currentDevice\b|\bsupportedInterfaceOrientations\b|\bNSSearchPathForDirectoriesInDomains\b|\bmemScoped\b|\.pointed\b|\bNSError\b)'

# ---------- config files ----------
echo
echo "=== 20 CONFIG (read these files fully - see platform-crashes.md section 7) ==="
for root in "${PATHS[@]}"; do
  find "$root" -path '*/build' -prune -o \( -name AndroidManifest.xml -o -name Info.plist -o -name project.pbxproj -o -name libs.versions.toml \) -print 2>/dev/null
done | sort -u | head -n "$MAX"
for root in "${PATHS[@]}"; do
  grep -rhoP --include='*.kts' --include='*.toml' --exclude-dir=build '\b(minSdk|targetSdk|compileSdk|android-(min|target|compile)Sdk)\b\s*[=:]?\s*"?[\w.()"]+' "$root" 2>/dev/null
  grep -rhoP --include=project.pbxproj '(TARGETED_DEVICE_FAMILY|IPHONEOS_DEPLOYMENT_TARGET) = [^;]+' "$root" 2>/dev/null
  grep -rhoP --include=Info.plist '<key>(NS\w+UsageDescription|UIRequiresFullScreen|UISupportedInterfaceOrientations[~\w]*|UIApplicationSupportsMultipleScenes)</key>' "$root" 2>/dev/null
done | sort | uniq -c | head -n "$MAX"

echo
echo "Done. Next: triage with references/crash-catalog.md, then run the edge-case sweep by reading code."
