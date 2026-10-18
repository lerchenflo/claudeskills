---
name: mobile-ux-conventions
description: Mobile UX and UI conventions sourced from official guidelines (Material Design 3, Apple Human Interface Guidelines, WCAG 2.2, plus Nielsen Norman Group / Baymard where the platforms are silent) - dialog and popup button order (confirming action on the trailing/right side, nearest the thumb), destructive actions, undo vs. confirmation, choosing between dialog / bottom sheet / snackbar / banner, touch target sizes and reachability, form validation, loading / empty / offline states, color (roles, contrast, dark mode), typography and Dynamic Type / font scaling, spacing and layout, lists and gestures, motion, and bottom navigation. Use this skill whenever building, reviewing or changing any mobile UI that has a dialog, popup, alert, confirmation, action sheet, bottom sheet, snackbar, toast, button row, delete action, form, list screen, loading/empty state, color choice, theme, layout, animation or tab bar - even if the user only says "add a delete button", "show a popup", "make a form" or "build the screen" and never mentions UX. Applies to Compose, SwiftUI, Flutter, React Native and any other mobile UI stack.
---

# Mobile UX conventions

Every rule below comes from an official guideline; the source tag after each rule says where. Android and iOS agree on most of them. Where they differ, both are listed so the app can follow the platform it runs on, or pick one consistently for a cross-platform UI.

Apply the rules while writing UI, not as an afterthought. When reviewing existing UI, report each violation with the rule it breaks, its source, and the concrete fix.

If a project documents its own convention that contradicts a rule here, the project convention wins - consistency inside one app matters more than matching a general guideline.

**Source tags**
- **M3** - Material Design 3, m3.material.io (and developer.android.com design pages)
- **HIG** - Apple Human Interface Guidelines, developer.apple.com/design/human-interface-guidelines
- **WCAG** - W3C WCAG 2.2, w3.org/TR/WCAG22 (criterion number and level given)
- **NN/g** - Nielsen Norman Group, nngroup.com
- **Baymard** - Baymard Institute, baymard.com

## 1. Dialogs and alerts

**Button order: confirming action on the trailing (right) side, dismissive action to its left.** Users finish reading on the right, and on a phone held in the right hand the right side is nearest the thumb. M3: buttons sit at the trailing edge, confirming action closest to the edge - "Don't place dismissive actions to the right of confirming actions". HIG: default button on the trailing side, Cancel on the leading side. Keep the order identical in every dialog; flipping it causes mis-taps from muscle memory. *(M3 dialogs, HIG alerts)*

**Stacked buttons: confirming action on top, Cancel at the bottom.** Use stacking when labels don't fit side by side. *(M3 dialogs, HIG alerts)*

**Number of actions.** M3: at most two actions; a dialog with a single action must be a plain acknowledgement. HIG alerts allow up to three buttons. For more choices use an action sheet / bottom sheet (HIG action sheets: at most 4 buttons including Cancel; destructive choice at the top, Cancel at the bottom). *(M3 dialogs, HIG alerts, HIG action sheets)*

**Label buttons with what happens.** Avoid "OK" unless the alert is purely informational, avoid "Yes" / "No"; use the action verb ("Delete", "Send"). Title the dismiss button "Cancel". *(HIG alerts)*

**Specific title and body.** No generic titles like "Error" or "Warning"; keep titles to two lines or fewer; add body text only if it adds information the title doesn't. *(HIG alerts)*

**Use dialogs only for critical, blocking decisions.** Don't show alerts at app launch, and don't use an alert just to inform - use a snackbar, banner or inline text instead. *(M3 dialogs, HIG alerts)*

**Don't stack modals.** Only full-screen dialogs may have another dialog on top. *(M3 dialogs)*

## 2. Destructive actions

**Prefer undo over confirmation.** "Avoid displaying alerts for common, undoable actions, even when they're destructive." Perform the action and offer "Undo" in a snackbar. Confirmation dialogs shown for routine actions get clicked through automatically and stop protecting anyone. *(HIG alerts, M3 snackbar, NN/g confirmation-dialog)*

**Confirm only irreversible, consequential actions** - permanent deletion, sending to other people, payment.

**A destructive button is never the primary/default button**, "even if that action is the most likely choice". *(HIG buttons)*

**Don't make Cancel the default either.** When you want people to actually read an alert about possible data loss, make no button the default. *(HIG alerts)*

**Destructive styling (red) marks an action the person did not deliberately choose.** If the user tapped "Delete" themselves, the confirming "Delete" in the alert does not need the destructive style. *(HIG alerts)*

**Keep consequential options away from frequent ones** - don't place "Delete" right next to "Save". *(NN/g proximity-consequential-options)*

## 3. Choosing the component

| Situation | Component | Source |
|---|---|---|
| Brief feedback on a user action, at most one action (e.g. "Undo") | Snackbar | M3 snackbar |
| Critical information or a decision that blocks the user | Dialog / alert | M3 dialogs, M3 snackbar |
| A set of choices related to an action the user started | Action sheet / bottom sheet | HIG action sheets |
| A problem the user should know about while still using the app (e.g. offline) | Non-intrusive label / banner with cached data | HIG alerts |

Never put critical information in a snackbar - it disappears. *(M3 snackbar)*

## 4. Touch targets and reachability

**Android: touch targets at least 48 x 48 dp, separated by at least 8 dp.** *(M3 structure, Google accessibility help 7101858)*

**iOS: default control size 44 x 44 pt, minimum 28 x 28 pt.** Leave about 12 pt around bezeled elements and about 24 pt around non-bezeled ones. *(HIG accessibility)*

**Keep essential interactions in reachable screen areas** - primary actions toward the bottom half, where the thumb reaches. *(Android layout basics)*

**Every gesture needs a single-tap alternative.** Swipe, drag-to-reorder and pinch must also be possible with simple taps. *(WCAG 2.5.1 A, 2.5.7 AA; NN/g contextual-swipe)*

**Every icon-only control needs an accessible name** describing the action. *(WCAG 4.1.2 A)*

## 5. Forms

**Validate when the user leaves a field (on blur), and remove the error the moment the input becomes valid.** *(Baymard inline-form-validation)*

**Show the error in place of the field's supporting text, say how to fix it, and add an error icon** - the icon is strongly recommended so color is not the only signal. *(M3 text fields, WCAG 3.3.1 A, 3.3.3 AA)*

**Show the matching keyboard** (email, number, phone, URL). *(HIG text fields)*

**Use visible labels, not placeholder-only fields.** Placeholders disappear while typing and hurt recall and accessibility. *(NN/g form-design-placeholders, HIG text fields)*

**Mark required fields explicitly** (e.g. asterisk); Baymard recommends marking both required and optional fields. Don't only mark the optional ones. *(NN/g required-fields, Baymard required-optional-form-fields)*

**Don't make users re-enter information they already gave in the same flow** - prefill or offer to select it. *(WCAG 3.3.7 A)*

**Login must not depend on memory or puzzles:** allow paste and password managers. *(WCAG 3.3.8 AA)*

## 6. Loading, empty and offline states

**Response-time limits:** under 0.1 s feels instant and needs no indicator; 0.1-1 s normally needs no special feedback; 2-10 s use a spinner or progress; longer use a percent-done indicator. *(NN/g response-times)*

**Skeleton screens for full-page loads under ~10 s** where the layout is known; spinners for small, local waits. *(NN/g skeleton-screens)*

**Show something as soon as possible** instead of a blank screen. *(HIG loading)*

**Empty sections explain why they are empty.** *(HIG tab bars)*

**Offline / errors:** show cached or placeholder data plus a non-intrusive label that describes the problem, rather than an alert. *(HIG alerts)*

## 7. Color

**Use semantic color roles, never hard-coded values.** M3 color roles (primary, surface, error, ...); HIG: "Avoid using hard-coded color values or colors that don't adapt." Dark mode, contrast modes and rebranding then happen in one place. *(M3 color roles, HIG dark mode)*

**Pair every container color with its "on" color** for text and icons on top of it (onPrimary on primary, onSurface on surface). *(M3 color roles)*

**Keep accent color scarce.** A 60-30-10 split (60 % dominant neutral, 30 % secondary, 10 % accent reserved for the primary call to action) is a useful guide. *(NN/g color-enhance-design)*

**One prominent (filled) button per screen.** M3: "Each screen should contain a single prominent button". HIG: keep prominent buttons to one or two per view. *(M3 buttons, HIG buttons)*

**One color, one meaning.** Don't use the same color to mean different things; M3 reserves the error role for urgency. Remember that color meanings vary by culture. *(HIG color, M3 color roles)*

**Contrast minimums:** text at least 4.5:1; large text (at least 18 pt, or 14 pt bold) at least 3:1; icons, field borders and other meaningful non-text UI at least 3:1. Disabled controls are exempt. Check contrast in both light and dark appearance; aim for 7:1 for small text in custom colors. *(WCAG 1.4.3 AA, 1.4.11 AA; HIG accessibility)*

**Never convey information by color alone** - add text, an icon or a shape. *(WCAG 1.4.1 A, HIG accessibility)*

**Support increased-contrast settings** (iOS Increase Contrast). *(HIG accessibility)*

**Dark theme:** use dark grey surfaces rather than pure black (M3 baseline #121212 historically; M3 now uses tone-based surface roles). Elevated surfaces are lighter than the base background. Use less saturated, lighter accent tones (around tone 200) on dark backgrounds. *(M3 dark-theme blog, M3 color roles, HIG dark mode)*

**Follow the system appearance;** avoid an app-specific light/dark setting. *(HIG dark mode)*

**Disabled state:** content at 38 % opacity, filled container at 10 %. *(M3 Compose FilledButtonTokens)*

## 8. Typography

**Use the platform type scale** - M3's 15 type styles, iOS built-in text styles - instead of ad-hoc sizes. *(M3 typography, HIG typography)*

**Body sizes:** M3 body 16 / 14 / 12 sp (large / medium / small). iOS default body 17 pt, minimum 11 pt. *(M3 typography, HIG typography)*

**Avoid light weights** (Ultralight, Thin, Light) for UI text. *(HIG typography)*

**Hierarchy through weight, size and color** together. *(HIG typography)*

**Line length about 40-60 characters** (up to ~120 on large screens); body line height about 1.5x. *(M3 applying type)*

**Text must scale to 200 %.** Support Dynamic Type / Android font scaling (Android 14 scales nonlinearly up to 200 %). At large sizes stack horizontally adjacent views vertically, let rows grow, and minimize truncation. Never use sp for padding or fixed heights. *(WCAG 1.4.4 AA, HIG accessibility, HIG layout, Android 14 features)*

**Content must survive increased text spacing:** line height 1.5x, paragraph spacing 2x, letter spacing 0.12x. *(WCAG 1.4.12 AA)*

**Capitalization differs per platform.** M3: sentence case everywhere, no title case. HIG: alert buttons use title-style capitalization; generally pick a style per element type and apply it consistently. *(M3 content style guide, HIG alerts, HIG writing)*

## 9. Spacing and layout

**8 dp grid for components, 4 dp for type and icons.** *(M3 grids and spacing)*

**Margins:** 16 dp on compact windows (<600 dp), 24 dp on medium (600-839 dp). Window size classes: compact <600, medium 600-839, expanded 840-1199, large 1200-1599, extra-large 1600+ dp. *(M3 applying layout, Android window size classes)*

**Align elements to make them easier to scan.** *(HIG layout)*

**Don't hide inputs behind the keyboard** - move them up while it is shown. *(Android layout basics)*

**Adapt to size classes** instead of stretching phone layouts across tablets, foldables and landscape. Use readable-width content on wide screens. *(HIG layout, Android window size classes)*

**Don't lock orientation** unless essential to the function. *(WCAG 1.3.4 AA)*

**Android edge-to-edge** is enforced when targeting SDK 35; predictive back animations are on by default when targeting SDK 36 - draw behind system bars and handle insets. *(Android 15/16 behavior changes)*

## 10. Lists

**Row anatomy:** leading icon / avatar / media, label, supporting text, trailing text / icon / control. *(M3 lists)*

**Swipe actions are a secondary shortcut only** - they are hard to discover; provide the same action another way. *(NN/g contextual-swipe, WCAG 2.5.1)*

## 11. Motion

**Add motion purposefully** - to show where things come from and go - never for its own sake. *(HIG motion)*

**Durations from the M3 tokens:** short 50-200 ms (small elements), medium 250-400 ms (most transitions), long 450-600 ms (large expressive transitions, usually emphasized easing), extra-long 700-1000 ms. Standard easing cubic-bezier(0.2, 0, 0, 1). *(M3 easing and duration tokens)*

**Let people interrupt motion;** don't make them wait for an animation to finish. *(HIG motion)*

**Respect reduce-motion settings:** replace x/y/z movement and zooms with fades. *(HIG accessibility, Android "Remove animations")*

## 12. Bottom navigation / tab bars

**3-5 destinations, each with icon and label.** Avoid overflow "More" tabs. *(M3 navigation bar, HIG tab bars)*

**Tabs are for navigation, never for actions.** *(HIG tab bars)*

**Keep the bar visible** except under modal views. *(HIG tab bars)*

**Never disable or hide tabs**, even when their content is unavailable - explain inside instead. *(HIG tab bars)*

**Each tab preserves its own navigation state / back stack.** *(HIG tab bars, Android multiple back stacks)*

**Reselecting the active tab scrolls to top.** *(M3 navigation bar)*

**Active destination uses a filled icon, inactive ones outlined.** *(M3 navigation bar)*

**Badges only for critical information.** *(HIG tab bars)*

## Review checklist

1. Dialogs: confirming action trailing / on top, Cancel leading / bottom, verb labels, specific title, action count within limits, only for critical decisions?
2. Destructive: undo instead of confirm where possible, destructive never default, no default when data loss, away from frequent actions?
3. Right component (snackbar / dialog / sheet / inline label)?
4. Targets 48 dp / 44 pt, 8 dp apart, gestures have tap alternatives, icon buttons named?
5. Forms: validate on blur, error text + icon below the field, matching keyboard, visible labels, required fields marked?
6. Loading per response-time limits, empty states explained, offline shows cached data + label?
7. Color roles + on-colors, one prominent button, contrast 4.5:1 / 3:1 in both themes, not color alone?
8. Type scale, no light weights, 200 % font scale works, capitalization per platform?
9. 8 / 4 dp grid, 16 / 24 dp margins, keyboard doesn't hide inputs, adapts to size classes, orientation not locked?
10. List rows follow anatomy, swipe has an alternative?
11. Motion within token durations, interruptible, reduce-motion respected?
12. Tab bar 3-5 labeled tabs, navigation only, never hidden or disabled, state preserved per tab?
