# Interactive HTML quiz (standalone, MC only)

Default for sets of ~30+ questions. One self-contained `.html` (no external
dependencies, works offline by double-click), saved next to the material with
a distinct name like `<Course>-Probetest-<N>Fragen.html`. Input questions and
widgets need the learning page (`references/learning-page.md`).

## Required behaviour (all implemented in `assets/quiz-template.html`)

- **Sidebar = calendar-like question grid:** one numbered tile per question
  (~6–10 columns, grouped by topic), clickable. Distinct tile states:
  unanswered, answered, current; after checking correct (green) / wrong
  (red). Progress counter (answered / total). Narrow screens: sidebar above
  the question or behind a toggle.
- **Tick and confirm:** options are checkboxes (square markers); hint under the
  stem „Mehrfachauswahl: eine oder mehrere Antworten sind richtig“.
  „Antwort bestätigen“ (or Enter) records the set; the next question appears
  after ~250 ms. Keys: 1–4 / A–D toggle, Enter confirm, ←/→ navigate.
- **„Instant check“ toggle (default on):** confirming marks right/wrong
  immediately (missed correct options dashed green), shows the explanation,
  colours the tile, updates „x / y richtig“; answer locked, no auto-advance
  (Next / → / Enter). Off: auto-advance, solutions only via Check. Mode is
  saved; revealed questions stay revealed after switching.
- **Back button** to the previous question (answers editable until checked);
  Skip/Next is fine too.
- **Check („Prüfen“):** marks correct options green and wrong chosen ones red
  on every question, shows explanations, colours tiles, shows the score
  (overall and per topic). Unanswered questions count as wrong (tiles marked
  unanswered). „Restart“ clears answers.
- **Option order shuffled** once per attempt.
- **„Zufällige Reihenfolge“ toggle (default off):** off = topic order, grid
  grouped by topic; on = Fisher–Yates shuffle, grid as one flat block (tile
  tooltip shows the topic), numbering, Back/Next and keys follow it. Order is
  stored as question indices (`seq`); answers, reveals and results are keyed
  by question, so toggling never loses progress. On draws a fresh order, off
  restores topic order, the current question stays selected; „Restart“
  re-shuffles when on. Toggle and order are persisted.
- **„Erweiterter Modus“ toggle (default off), only when the bank has `x: 1`
  questions.** Extended questions test the same concepts as the core set with
  new examples, invented domains and other angles (mostly applied, especially
  A2). Off: only core questions in grid, numbering, progress, score. On: they
  follow their topic's core questions (dot on the tile, „erweitert“ pill),
  score adds core/extended rows; progress is kept. Offer it when the user
  wants "everything covered", "more practice" or "other examples". Never put a
  concept only into the extended set – every extended question has a core
  counterpart in its topic.
- Progress in `localStorage` inside `try/catch`; the page works without
  storage. Light/dark via `prefers-color-scheme`; readable at phone width.

## Build from the bundled files

- Copy `assets/quiz-template.html` to the scratchpad; change only `<title>`,
  sidebar `<h1>`/subtitle and the `localStorage` `KEY` (new key per quiz; bump
  its version suffix whenever the bank changes so stale saves are dropped).
- Question bank `questions.js`:
  ```js
  // c = indices of ALL correct options (1–4). Options are shuffled at runtime,
  // so explanations name options by their text, never by letter (A–D).
  const QUESTIONS = [
  {id:1,t:'Topic',y:'A2',q:'Welche Aussage/n trifft/treffen zu? (HTML allowed)',o:['correct','wrong','correct','wrong'],c:[0,2],e:'Why the correct ones hold; „wrong“ fails because …'},
  {id:2,t:'Topic',y:'C1',q:'Welche CSS-Eigenschaft … ist hauptsächlich …?',code:'.box { display: grid; }',o:['…','…','…','…'],c:[1],e:'…'},
  ];
  ```
  `t` topic, `y` archetype (R1–R6/A1–A6/C1), `o` exactly 4 options, `c` sorted
  correct indices, `e` explanation (covers every wrong option), `id` unique,
  optional `code` (code block under the stem), optional `x:1` (extended). The
  correct-count mix applies to the core set alone.
- **Build + validate:** `node scripts/build_quiz.js questions.js quiz-template.html out.html`.
  Flags: `--mix` enforces the correct-count mix (only for courses whose real
  exams show it), `--link` requires `ref` on every question (learning page).
  Input questions (`kind`) skip the MC rules; they need `a`, `e` and (with
  `--link`) `ref`.
- **It refuses to build** (exit 1, lists problems) on: ≠ 4 options; `c` not 1–4
  valid indices; with `--mix`, a core set (≥ 20) with under 45 % single-answer
  or over 25 % three/four-correct, or all-four-correct more than once per 30;
  the correct option longest in over 40 % of single-answer questions (length
  cue); „Welche EINE“/„genau eine“ stems; superlatives with several correct
  outside a slash stem; „Welcher/Welches …“ with several correct; duplicate
  ids/questions/options; **any A–D letter or position reference in an
  explanation** (text in „…“ and "z. B." ignored); who/when/source questions;
  extended questions in a topic without core questions. Fix every item –
  never weaken the check. The activity check also hits words that merely
  contain „aktivität“/„activity“/„übung“ („Attraktivität“, an anti-pattern
  "Activity without goal", „Übungsblatt“): rephrase stem/explanation, or cite
  the summary section („siehe 2.11“); option text is not checked.
- **It warns** (still builds) when a wrong option or wrong chip is not quoted
  in the explanation (heuristic: full text, or its words). Fix each warning or
  confirm it is a false hit.
- On success it prints count (core/extended), topic split, correct-count mix,
  recall/applied/code mix and length-cue rate – report them.
- **Render check:** load the built page headless (`google-chrome-stable
  --headless --dump-dom` with a small test script that writes PASS/FAIL into a
  `data-log` attribute) and take one `--screenshot`. No Chrome (macOS): the
  cached Playwright Chromium
  `~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell`
  takes the same `--headless --dump-dom/--screenshot/--print-to-pdf` flags.
