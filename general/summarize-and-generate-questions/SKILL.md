---
name: summarize-and-generate-questions
description: Set up a course folder for exam prep and generate applied, reasoning-style exam questions (multiple choice and typed-answer) from study material (lecture slides, scripts, summaries, textbook chapters). Use whenever the user uploads or references study material and asks for practice questions, a quiz, self-test questions or exam prep — especially questions beyond simple recall ("make it harder", "more like real exam questions", "questions that make me actually think", "not just picking the bullet point off the slide"), or to reverse-engineer and match the style of pasted example exam questions. Course setup: when called in a new folder of course files (or asked to "summarize all files", "set up this course", "prepare this folder"), it extracts the text of every file (PDF, Xournal++ notes, photos, Office files), interviews the user about what is NOT on the exam, writes a course CLAUDE.md that indexes every file plus open-question and change-log files, and summarizes everything into a study summary with loud alarm boxes for missing content. Also summarizes new lecture decks into a study-summary PDF, and builds an interactive HTML practice test (question grid, instant check, random order, extended mode) or a learning page (summary + connected quiz in one offline HTML file, solutions behind „Lösung zeigen“). Asks per course: multiple choice only, or mixed with typed-answer questions. Never asks who/when/source-citation questions.
---

# Summarize and generate questions

Two jobs: **set up and summarize a course folder** and **generate exam
questions** from it. In a folder without a course `CLAUDE.md`, start with the
course setup.

Questions test **application and discrimination**, not recall of bullet
points: "given a new example, which of these is one of the five things" is
what real exams ask; "list the five things" can be answered by matching
slide text.

**Language:** this skill is in English. Summaries, transcriptions and
questions use the material's language. Chat (replies, progress lines,
AskUserQuestion) stays in the user's reply language from the global
CLAUDE.md, even when the files are German. German quotes here (stems like
„Welche Aussage/n …“, labels like „Lösung zeigen“) come from the German
calibration course and templates; for another language, translate the labels
and follow that language's exam grammar.

## Reference files (read when the step needs them)

| File | Read when |
|---|---|
| `references/archetypes.md` | before writing questions: exam calibration, archetypes R1–R6 / A1–A6 / C1, material-to-archetype map, set mix |
| `references/old-tests.md` | the course has old tests, exams, mock exams or LMS quizzes |
| `references/course-setup.md` | new course folder, or the user wants a summary |
| `references/quiz-page.md` | standalone interactive HTML quiz, `build_quiz.js` checks |
| `references/learning-page.md` | learning page, input questions, widgets, format catalog, browser tests |

Bundled: `scripts/` (`extract_texts.py`, `extract_office.py`, `ocr.swift`,
`build_quiz.js`, `build_lernseite.py`, `answer_check.py`), `assets/`
(`quiz-template.html`, `lernseite-template.html`, `summary-template.html`,
`course-setup/` file templates).

## Hard rules (always apply)

- **Correctness has top priority** – above speed, length and design. The user
  learns from these files: every statement in a summary, solution or question
  must be correct in content and in context. Run "Correctness check" before
  handing anything over; when in doubt, ask (never assume).
- **Ask the format for every new quiz:** „Multiple Choice only“ or
  „gemischt“ (MC + input questions). MC-only came from the first course (SE);
  it is not a global rule. For a mixed set, first build a **format sample**
  (one question per format from the catalog in `references/learning-page.md`,
  real course content, on the learning page) and let the user pick formats.
  In a mixed set, simple calculations and short exact answers (a number, a
  base conversion, a set) are **input questions** (`kind:'num'|'text'|'set'`),
  never MC with guessable options; concepts, definitions and "which
  statements are true" stay MC. **Prefer answer widgets** (truth table,
  fill-in grid, Venn shading, chips, mod clock, bit row) wherever the content
  is visual – the user wants „really cool questions“. Open free-text / essay
  answers are never auto-checked: they become theory questions with a hidden
  solution in the summary.
- **MC questions:** exactly 4 options (A–D), 1–4 correct (never 0), scored
  all-or-nothing. The correct-count mix is course-specific: calibrate it on
  the course's real exams (`references/archetypes.md`). Without real exams use
  the SE default (≈ 55 % one correct, 30 % two, 12–15 % three, all four at
  most once per 30) and say so. The build enforces a mix only with `--mix`.
- **Stems use the exam's grammar.** Default: a slash form that hides the
  count – „Welche Aussage/n beschreibt/en …?“, „Welche/r Begriff/e …?“,
  „Welche Option/en treffen zu?“, „beschreib/en/t“.
  - Superlatives („am besten“, „am ehesten“, „am deutlichsten“, „am
    unmittelbarsten“, „hauptsächlich“) fit a slash stem with any count (real
    exams: 1–3 correct) and a singular stem with exactly one correct.
  - Singular „Welche/r/s“ stem („Welcher Bestandteil …?“, „Welche Aussage
    beschreibt …?“) only with exactly one correct; plain plural „Welche“ stem
    („Welche Aussagen …?“, „Welche der folgenden sind …?“) only with at least
    two (in 45 real questions both held 9/9).
  - W-questions („Was …?“, „Wie …?“, „Warum …?“) are neutral: mostly one
    correct, but real exams had „Warum …?“ / „Was muss …?“ with 2 and „Was
    sind …?“ with 3.
  - Mix ≈ 35 % slash, 20 % singular, 20 % plural, 25 % W-questions, so the
    grammar never gives the answer away. Never „Welche EINE“, „genau eine“,
    „die einzige“.
- **Options are short and parallel**, like the exam's: often one term with a
  full stop („Controller.“, „Visibility.“), else one line. Similar length,
  same grammatical shape; the correct option is not the longest or most
  qualified by habit (the build checks this). Put precision into all four
  options, not only the right one.
- **The user has no calculator.** Pick numbers that work by hand on paper
  (small operands, powers of 2, clean results). If big numbers are unavoidable,
  the solution shows the hand method step by step.
- **Every part of a multi-part task keeps its task.** When parts (1a, 1b, …)
  sit on separate pages behind a „Continue“ button, repeat the initial task text
  and all givens on each page, so no part appears without context.
- **Never assume:** a question may only test settled content (two or more
  sources agree, or the user confirmed it). Open or single-source spots get
  no question until the user answers.
- **Every correct option is unambiguously backed by the source; every wrong
  option is clearly wrong for a nameable reason.** In multi-answer questions
  an "arguably true" distractor makes the question unanswerable – drop it.
- **The explanation says why each wrong answer is wrong – always.** `e`
  gives the source fact behind the correct option(s) and then one short
  clause per wrong option, naming it by a quote of its text („„0“ ist das
  neutrale Element der Addition“). The same holds for every wrong chip
  (`kind:'chips'`; chips that fail for the same reason may share one clause)
  and every false row of a Kprim table. No wrong option is left unexplained.
  The user asked for this (04.11.2026) after an explanation skipped why
  „n (in ℤ/nℤ)“ was wrong. `build_quiz.js` warns when a wrong option or chip
  is not quoted in `e`; fix every warning or confirm it is a false hit.
- **No questions about in-class activities or exercises** („Activity: What
  did I hire?“, „Mini-Aktivität“, „Übung“, „in Teams von 4–5“, „15 Minuten“,
  „Produktkarten“): team size, timing, materials and steps are not exam
  content, and explanations never cite them as the source. If an activity
  demonstrates a concept, test the concept itself without mentioning the
  activity.
- **Spell out abbreviations in brackets every time they appear** – stems,
  options, explanations, summaries: `<ul>` (unordered list), `<li>` (list
  item), DOM (Document Object Model), JTBD (Jobs To Be Done), DoD (Definition
  of Done), `px` (pixels), `fr` (fraction) … Quizzes: in every question (each
  stands alone). Summaries: HTML tags/attributes/units every time outside code
  blocks; acronyms like JTBD/DOM/CSS at least at their first occurrence per
  section. Standards and compressed jargon too: never a bare
  „IEEE-754-Format“, „2er-Kompl.“, „VZ“, „1er“ – write „Gleitkommazahl nach
  IEEE 754 (Standard für Gleitkommazahlen)“, „Zweierkomplement (negative Zahl
  = alle Bits invertieren, dann +1)“, „Vorzeichen“. Never let an expansion
  give the answer away: if the question asks what an abbreviation means,
  leave it unexpanded in stem/options and expand it in the explanation;
  toggle/matching labels get the full term without the giveaway bracket.
  (User request, Computersysteme, 30.10.2026.)
- **Don't quiz details of the slides' own examples** (a sample product vision
  like "Rheticus Experience", a case study, a demo app): never ask that
  example's competitor, target group, wording or numbers. Test the concept it
  illustrates, ideally on a new invented case (A2). Exception: the example
  *is* the concept (the milkshake story for JTBD) – ask about its lesson, not
  its trivia.
- **No questions about people, authorship or citations:** never „Von wem
  stammt …“, „Wer hat … definiert/entwickelt“, „Wer prägte …“, „In welchem
  Jahr …“, „Auf welcher Folie …“. Names, years and sources may appear as
  context but are never what is tested, and options are never lists of names
  or years.
- **Code in a question goes in `code`, one statement per line.** IJVM programs,
  microinstruction sequences, source code: never a one-liner with „·“ or commas
  between the statements in the stem. The page shows `code` as a `<pre>` block;
  labels keep their own column (`L1: BIPUSH 0`). (User request, 11.11.2026.)
- **Tap-to-cycle tables are shuffled.** The learning page shows the rows of every
  toggle grid with one blank per row (Kprim tables, matching) in a random order per
  run, so the answers never follow the order of the toggle labels (1 tap, 2 taps,
  3 taps …). Still write rows so that the source order is not the toggle order;
  set `grid.fixed: true` only where the row order carries meaning (a sequence,
  a truth table). (User request, 11.11.2026.)
- **Every question has a scratch pad.** The learning page puts a „Notizblock“
  (text and drawing board, saved per question) under each card for hand
  calculations; keep it when changing the template. (User request, 11.11.2026.)
- **Worked examples in the summary need an answer block:** `.aufg` = `.q` + `.a`.
  The build turns `.a` into the hidden solution; a box without one used to stop
  the page script (now guarded, still write `.a`).
- **Explanations never refer to options by letter or position** – options are
  shuffled at runtime. No „B ist …“, „die erste Option“, „die letzten
  beiden“, „die letzte Aussage“; quote the option text instead (the build
  rejects these). Applies to plain-text sets too (users reorder or print them).

## Workflow

00. **Work from a plain-text extract, not the PDFs.** `<work>` = the course's
    Claude folder: an existing `06_Claude/` or `Claude/`; if neither exists,
    ask which name to use. Look for `<work>/text/` (one `.txt` per PDF with
    page markers, plus `INDEX.md`). Missing or older than the slides: run
    `python3 scripts/extract_texts.py <course-root> [--skip <private folder>]`
    (needs poppler's `pdftotext`; Node.js for practice tests; re-extracts only
    changed files). Copy the script to `<work>/tools/` with a short
    `README.md`. Photos of exam or quiz sheets have no text layer: transcribe
    them verbatim once (original language, marked answers) into a `.md` in
    `<work>/text/`. `INDEX.md` flags image-only pages: view them
    (`pdftoppm -png -r 55 -f N -l N`) and describe important diagrams in the
    README.
0. **Ask count, format and page type** in one AskUserQuestion call (skip what
   the user already said): count (e.g. 20 / 50 / 120 – never guess, it drives
   the topic split and the user's time); „Multiple Choice only“ vs
   „gemischt“; standalone quiz page or **learning page** (summary + connected
   quiz) – always ask. If the material spans several decks, ask in the same
   call: all decks or only the newest. If the user also wants a summary, write
   it first (`references/course-setup.md`); the questions then follow slides
   and summary.
1. **Read the whole source text first**, plus any real exams/quizzes: old
   tests from the same lecture set topic weights, task types and phrasing
   (`references/old-tests.md`) and calibrate the MC style
   (`references/archetypes.md`). Note each deck's central message. Skim for
   material that fits each archetype (map in `references/archetypes.md`);
   don't generate paragraph by paragraph.
2. **For A2, invent a new domain** that is not in the source – the biggest
   lever against skimmable questions.
3. **Give each wrong option an intentional, nameable reason** (boundary
   violation, overgeneralization, related-but-wrong category,
   irrelevant-but-true fact). If you can't state it in one clause, replace the
   distractor. No joke or absurd options – each must tempt a half-prepared
   student.
4. **MC: 4 options, about half the set with exactly 1 correct** (input
   questions skip this). Add a second or third correct option only where the
   source clearly supports it (A3: two precise statements; A2: two items that
   fit; R1 lists; A6 explanations). If the source's own example questions use
   another format (open, true/false), rewrite them into this format and say
   so. Even out length: if the correct option is the longest, shorten it or
   lengthen the distractors. Scan for who/when/source questions and replace
   them.
5. **Write the explanation**: one or two sentences citing the source fact for
   the correct option(s), then why each wrong option is wrong (Hard rules).
   Compact – a check for the user, not a re-teaching of the topic.
6. **A fact needed for a good question is not in the source?** Say so and
   flag it as general knowledge; never invent exam-sounding content.
7. **Build, validate, test** (`references/quiz-page.md` or
   `references/learning-page.md`). Report the build stats and a short mix
   line (e.g. "10 recall, 10 applied, topics X–Y") so the user can ask to
   shift the balance.

## Correctness check (top priority)

Run on every summary, transcription, solution and question set before
handing it over. Nothing is done until it passes.

1. **Every statement has a source** – a page of the material
   (`<span class="src">S. 12</span>` in the summary). General knowledge only as
   a marked addition (`.alarm.added`, logged in `TO_VERIFY.md`).
2. **Correct in context, not just in general.** Use the lecture's own
   definitions, notation and conventions (does ℕ include 0? truth-table row
   order? symbol for "exactly one"?), even where a textbook differs. Lecture
   differs from the standard: keep the lecture's version and add a note.
   Lecture looks wrong: keep it, mark `[CHECK]`, ask. Keep every condition and
   qualifier ("only for finite sets", "if gcd = 1", "in ℤ/nℤ"); never
   generalize beyond the source's scope or move content where it does not
   hold.
3. **Compute, don't trust.** Recalculate every worked example, solution,
   table, conversion and formula with Python – including the user's and
   classmates' solutions. A wrong class solution is shown as a slip
   (`.alarm.slip`), never fixed silently.
4. **Drawings match the content:** shaded Venn regions, axis labels, table
   values, arrows.
5. **Sources agree.** Cross-check with every source in the folder (script,
   notes, classmates, solutions). Conflicts and single unclear sources go to
   the user.
6. **Separate review pass:** re-read the finished output section by section
   against the text extracts, claim by claim, as if someone else wrote it. Fix,
   then check the fixes the same way.
7. **Report honestly:** what was verified and how (recomputed, cross-checked
   with N sources), and what is still unverified or open.

## Output format

Unclear which output the user wants: ask. **Plain text:** numbered
questions, options A–D, answer key at the end. **Interactive HTML quiz**
(default for ~30+ questions): `references/quiz-page.md`. **Learning page**
(summary + quiz in one file, needed for input questions and widgets):
`references/learning-page.md`.
