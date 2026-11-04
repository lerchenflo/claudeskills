# Learning page, question formats and widgets

## Question format catalog (pick per course)

All formats run on the learning page (`assets/lernseite-template.html`); the
standalone quiz is MC only. When a course starts a mixed set, build a format
sample (one question each, real course content), let the user pick, and
record the chosen formats and the favourite in the course `CLAUDE.md`.
Examples from Strukturierte Programmierung (C, German), where the user liked
all formats and the desk-check table most.

| # | Format | Fields | Use it for | Example |
|---|---|---|---|---|
| 1 | MC, several correct | `o`, `c:[…]` | statement checks (A3), slash stem | „Welche Aussage/n über Zeichenketten in C trifft/treffen zu?“ |
| 2 | MC, one correct | `o`, `c:[i]` | discrimination (A1/A2), singular stem | „Welche Zeile ist gültiger C-Code und kein Pseudocode?“ – options differ only in `and`/`mod`/`:=` vs `&&`/`%`/`=` |
| 3 | Code + MC | `code`, `o`, `c` | read a program, find bug and fix (C1) | `while (i <= LEN)` writes past the array end → „Der letzte Durchlauf schreibt nach `values[5]`.“ ✔ |
| 4 | Number input | `kind:'num'` | value of an expression, output of code | `int a = 7 / 2 * 2;` → 6 |
| 5 | Text input | `kind:'text'`, `strict:true` for code | one line of code, a short exact term | „Schreibe die Präprozessor-Zeile …“ → `#define LEN 24` |
| 6 | Set input | `kind:'set'` | result of a procedure as a set | sieve up to 30 → `{2, 3, 5, …, 29}` |
| 7 | Fill-in table | `kind:'grid'`, cells `'?'` | desk check (Schreibtischtest), Euclid tables | GGT(45, 12): x/y after pass 1–3 |
| 8 | Tap-to-cycle table | `kind:'grid'`, `toggle:[…]` | classify 4–8 items into 2–4 categories | step → Präprozessor / Compiler / Linker / Prozessor |
| 9 | Chips | `kind:'chips'`, `chips:[…]` | pick all fitting items from more than 4 | preprocessor lines of a program; values that count as true in `if (…)` |
| 10 | Bit row | `kind:'bits'` | base conversion to binary | 37 → `00100101` |
| 11 | Truth table | `tt:{vars, col}` + MC columns | logic expressions | `a && !b` → „f w f f“ |
| 12 | Venn / mod clock | `kind:'venn'`, `kind:'clock'` | set expressions, modular arithmetic | (Diskrete Mathematik) |
| 13 | Writing task | `<div class="tq">` in the summary | write pseudocode or C; hidden solution, self-checked | „Schreibe eine Funktion, die das Maximum eines Feldes (Arrays) liefert.“ |
| 14 | Mock exam | own topic „Probeprüfung N“ | exam-like mix, input and widget questions only | 3 × ~10 questions |
| 15 | Kprim table | `kind:'grid'`, one row per statement, `toggle:['zutreffend','nicht zutreffend']` | K-Prim/ilias style: 4 statements judged, 0–4 true | IEEE: „E = 1…1, F ≠ 0 → Unendlich“ → nicht zutreffend (Computersysteme) |
| 16 | Step-by-step cloze | `kind:'grid'`, head `['Schritt','Ergebnis']`, one `'?'` row per step, alternatives with `\|` | calculations asked step by step (ilias Cloze): conversions, IEEE 754, two's complement | −11,5 → 1011,1 · 1,0111·2³ · 3 · 10000010 · 1 · C1380000 |
| 17 | Ordering | `kind:'grid'`, rows = shuffled steps, one `'?'` per row, `a` = positions | fixed sequences (R3): protocols, cycles | USB enumeration: erkennen → Kommunikation → Descriptors → Adresse → konfigurieren |
| 18 | Error hunt | MC single; stem shows a worked solution with one wrong step, options quote the steps | procedure understanding (A1); explanation gives the fixed value and the consequential error | IEEE 6,25: „129 = 1000 0010“ is the first error (→ 40C8 0000) |
| 19 | Check row | `kind:'grid'`, one row mixing verdicts (`'richtig\|r'`) and numbers/characters | decoding with several outputs (Hamming: parity bits, error position, character) | 0100 1100 0011 → P2, P4 falsch → Stelle 6 → „C“ |

Rules learned with these formats:

- **Error hunt:** later steps follow from the planted error (consequential
  error), so only one step is the *first* wrong one.
- **Kprim table vs. MC Kprim:** the table allows „all false“ and matches ilias;
  MC with checkboxes needs 1–4 correct. Offer both in the format sample.
- **Explain the procedure in the stem** when asking for an algorithm's result
  (sieve, desk check, conversion): numbered steps first, then the question.
  The user rejected a sieve question that assumed the method.
- **Code questions show the full program** in `code` (includes, `main`,
  `return 0;`); compile and run every program before using it.
- **Chip labels and given grid cells are HTML** (`innerHTML`): escape `<`/`>`
  (`&lt;stdio.h&gt;`); `a` repeats the chip labels exactly.
- **Text answers ignore `,` and `;`** (for truth-table strings) – set
  `strict:true` whenever the answer is code.
- **Toggle tables:** each row belongs to exactly one category; avoid rows two
  stages touch (a line using `LEN` is preprocessed *and* compiled – ask about
  the step, not the line).
- Test every format in the browser: renders, correct answer accepted, a
  typical wrong answer rejected (see Test).

## Learning page (summary + connected quiz)

Built only when the user chooses it (workflow step 0). One self-contained
HTML file: left tabs „📖 Zusammenfassung“ / „✎ Probetest“; the summary is the
default view and readable on its own. Made for Diskrete Mathematik
(`Claude/sources/`, `DM_Lernseite.html`); the bundled files are the generic
version.

- **Sources:** the summary's print HTML stays the single source (it also
  renders the PDF). Number h2/h3 headings („2.3 Mengenoperationen“); extra
  headings get `id="s-…"` to link to. Exercises:
  `<div class="aufg"><div class="q">full task text</div><div class="a">solution</div></div>`;
  theory questions:
  `<div class="tq"><div class="tq-q">…</div><div class="tq-a">…</div></div>`.
  Every exercise shows its **full task text** (no sheet needed).
- **Questions file** (`const QUESTIONS = [...]`), mixed format:
  ```js
  {id:1,t:'Logik',y:'A3',q:'Welche Formel/n ist/sind eine Tautologie?',o:['p ∨ ¬p','p ∧ ¬p','(p ∧ q) ⇒ p','p ⇒ q'],c:[0,2],e:'…',ref:'1.5'},
  {id:2,t:'Mengenlehre',kind:'num',q:'Wie viele Elemente hat ℘({1, 2, 3, 22, 42})?',a:['32'],show:'32 (= 2⁵)',e:'|℘(M)| = 2^|M|',ref:'2.8'},
  {id:3,t:'Zahlen',kind:'text',q:'650₈ ins Hexadezimalsystem?',unit:'₁₆',a:['1a8','0x1a8'],show:'1A8₁₆',e:'…',ref:'3.17'},
  {id:4,t:'Mengenlehre',kind:'set',q:'A ∪ D?',a:['{1, 2, 3, 5, 42}'],show:'{1, 2, 3, 5, 42}',e:'…',ref:'2.3'},
  ```
  `num` compares numerically; `text` after normalising (case, spaces,
  subscripts like ₁₆, unicode minus, ·/×; `,` and `;` ignored unless
  `strict:true` – `#define N 5;` must not count as `#define N 5`); `set`
  ignores order and duplicates and accepts nested sets and tuples
  (`{∅, {1}}`, `{(a, 1), (b, 2)}`). `a` lists every accepted spelling, `show`
  is the displayed solution (required for widgets). `ref` = section number:
  before answering „📖 Erst im Skript nachlesen“ jumps there; the solution box
  gets „📖 Im Skript nachlesen“ (primary button when wrong); „← zurück zum
  Probetest“ returns. Optional `code`, `unit`, `demo:true`; `x:1` = extended
  mode only (dashed tiles, „erweitert“ pill). Mock exams work well as their
  own topic („Probeprüfung N“, input/widgets only).
- **Widgets** (in `assets/lernseite-template.html`, tested in Chromium and
  iPhone WebKit; the answer is kept as a string, so saving and „Prüfen“ work
  as usual):

  | field / kind | shows | answer `a` |
  |---|---|---|
  | `tt:{vars:'pq', col:'p ∨ q'}` (MC or input) | truth table with a „?“ column; MC options written „w w w f“ become candidate columns | as usual |
  | `kind:'grid'`, `grid:{head:[…], rows:[[…,'?',…]], toggle?:['w','f']}` | fill-in table (helper columns, Euclid, ℤ/nℤ tables); `toggle` = tap to cycle | one entry per `?`, row by row; `'∅\|{}'` = alternatives |
  | `kind:'venn'`, `venn:{names:['A','B','C']}` | tap regions to shade a set expression (2 or 3 sets) | region codes: `'110'` = in 1st and 2nd, not 3rd; `'000'` = outside |
  | `venn:{sets:{A:[…],B:[…]}, U:[…]}` (any question) | Venn diagram with elements in their regions | – |
  | `kind:'chips'`, `chips:[labels]` | tap all fitting chips (more than 4 options: elements of ℘(M), number sets, divisors …) | labels of the correct chips |
  | `kind:'clock'`, `clock:{n:12, from?:9}` | tap a number on a mod-n dial | `['2']` |
  | `kind:'bits'`, `bits:8` | bit row with place values 2⁷ … 2⁰, tap to flip | `['00010111']` |

  `build_quiz.js` checks region codes, chip labels, blank counts and bit
  lengths; letters A–D used as names in stem, code or Venn data count as
  variables, not option references.
- **Many variants (extended mode, mock exams): generate them with a Python
  script that computes every answer** (truth-table columns, Venn codes,
  conversions, mod, ggT, inverses) and writes a marked block
  (`// <<GEN-START>>` … `// <<GEN-END>>`) into the questions file – no typed
  answers; re-run instead of hand-editing. `scripts/answer_check.py` has the
  helpers (`column`/`equiv`/`tautology`/`true_rows` for logic,
  `venn_codes`/`fmt_set`/`powerset` for sets, `inverse`/`to_base` for numbers,
  `write_block` for the GEN block; CLI: `answer_check.py tt "p ∧ q" pq`). Full
  example: the course's `Claude/tools/quiz_variants.py` (Diskrete Mathematik).
  Generated explanations also say why each wrong option or chip is wrong.
- **Build:** `node scripts/build_quiz.js --link questions.js assets/quiz-template.html /tmp/check.html`
  (validation only), then
  `python3 scripts/build_lernseite.py --summary <summary.html> --questions questions.js --template assets/lernseite-template.html --out <Kurs>_Lernseite.html --title "<Kurs>" --sub "<Semester>" --key <kurs>-lernseite-v1`.
  It scopes the summary CSS under `.doc`, adds heading ids, writes the TOC
  statically, wraps solutions in `<details>` with a note field, and warns on
  duplicate ids or refs without a section. Rebuild after every summary change.
- **View controls (both templates):** „Textgröße rechts“ (A− / 100 % / A+,
  ⌘/Ctrl + Plus/Minus/0, trackpad pinch) zooms **only the right content** via
  CSS `zoom` on `.zoomable`; the sidebar keeps its size. Sidebar width is
  draggable (fixed `.resizer`, CSS variable `--sidew`, 220 px … 60 % of the
  window, arrow keys, double click = 340 px). Zoom and width saved per page in
  `localStorage`. (Users asked: browser zoom enlarges the sidebar too.)
- **Collapsed Claude additions:** `build_lernseite.py` turns every
  `<div class="alarm added">` into `<details class="alarm added claude">`
  (label → `<summary>`); switch `#claudeAll` opens/closes all, state saved.
- **Must hold (tested):** one file, no external requests (works when sent
  alone); works **without JavaScript** (Finder spacebar, phone Files app):
  static TOC, native `<details>` solutions, JS-only controls hidden,
  `<noscript>` note that the quiz needs a real browser; phone layout with top
  bar and „☰ Inhalt“ drawer; state in `localStorage` (try/catch). Strict CSP
  works: `default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:`.
- **Test** with Playwright (WebKit desktop + iPhone, Chromium, JS off): reveal,
  TOC jump, drawer, input answer, wrong marking, ref jump + back, content zoom
  (sidebar unchanged), sidebar resize, Claude switch. Without Playwright: copy
  the page, append a test script that writes PASS/FAIL into a `data-log`
  attribute, run `chrome-headless-shell --headless --virtual-time-budget=3000 --dump-dom`
  (cached in `~/Library/Caches/ms-playwright/chromium_headless_shell-*/`); for
  the no-JS view strip the `<script>` tags and take a `--screenshot`. Use the
  Playwright version that matches the cached browsers: `npx playwright
  install` from another version **deletes** the other versions' browsers
  (incl. the headless shell used for PDFs).
- **Mixed set without a summary:** use the learning page, or port the input
  functions (`isInput`, `norm`, `checkInput`, input branch of `renderCard`)
  from `assets/lernseite-template.html` into the quiz template.
