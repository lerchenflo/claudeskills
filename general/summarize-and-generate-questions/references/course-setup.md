# Course setup and summaries

## Course setup (new folder: index, interview, summary)

Use in a folder of course files without a course `CLAUDE.md`, or when the
user asks to summarize all files / set up the course. Reproduces the
Diskrete-Mathematik setup. Templates: `assets/course-setup/` (CLAUDE.md,
SESSION_LOG.md, OPEN_QUESTIONS.md, TO_VERIFY.md) and
`assets/summary-template.html`.

**Most important rule: never assume.** A fact is settled only when two or more
independent sources agree (script and the user's notes, or two classmates'
notes). One unclear source, disagreeing sources or no source: don't guess,
interpret or fill in. Mark it (`[UNCLEAR]`/`[CHECK]`/`[GAP]`), add it to
`OPEN_QUESTIONS.md` and ask the user (AskUserQuestion); ask for more sources
(classmates' notes, photos) where a spot has only one. Anything Claude adds
anyway (a solved gap, an interpretation) is an assumption: mark it
`.alarm.added`, log it in `TO_VERIFY.md` and ask.

1. **Inventory.** List every file (`find . -type f`, skip `.DS_Store`, hidden
   and system folders). Group: lecture script/slides, exercise sheets, own
   solutions, handwritten notes (`.xopp`, scans, photos), formula sheets, old
   exams/quizzes (folders like `Old Test`, `Altklausuren`, `Probeklausur`),
   textbooks, classmates' material, other. `<work>` = `Claude/` unless
   `06_Claude/` or `Claude/` already exists.
2. **Extract all text once:** copy `scripts/extract_texts.py` to
   `<work>/tools/`, run it (`--out <work>`).
   - `.xopp` (Xournal++): export with notes
     (`xournalpp --create-pdf=<work>/text/<name>_annotiert.pdf <file>.xopp`;
     macOS: `/Applications/Xournal++.app/Contents/MacOS/xournalpp`), render
     pages with handwriting (`pdftoppm -png -r 100`), read them and write
     `<work>/text/<name>_transcription.md`: printed text plus every note,
     exactly as written. Markers: `✍` handwriting, `⌨` typed text box,
     `==…==` highlighted, `[CHECK: …]` probably wrong, `[UNCLEAR: …]`
     unreadable, `[GAP]` gap in the script without notes, `[ADDITION]` Claude
     addition. Never correct silently. Note page offsets between `.xopp` and
     PDF (inserted pages).
   - Photos and scans without text layer: transcribe the same way. Screenshots
     of e-learning pages inside PDFs (GoodNotes/iOS exports of classmates):
     extract the embedded images (`pdfimages -png -p file.pdf dir/i`) and OCR
     them with `scripts/ocr.swift` (`swift ocr.swift dir/*.png > out.ocr.md`;
     macOS Vision, German + English, two-column aware) – far cheaper than
     viewing each image. Look at diagrams and handwriting yourself; 200 dpi
     renders work for handwriting, OCR of handwriting is rough.
   - `.pptx`/`.docx`: `soffice --headless --convert-to pdf` if LibreOffice is
     installed, else `scripts/extract_office.py ROOT --out <work>` (reads the
     zip XML: slide text, speaker notes, image names, docx tables). Speaker
     notes can sit on the wrong slides after re-ordering – never trust the
     mapping blindly; flag notes that contradict the slide.
   - Same document as PDF and .docx (e.g. a submitted worksheet): diff the
     text, keep one as the source (user request), note it in the sources
     table.
   - Big textbooks: extract too, for lookups only.
   - **Cross-check sources:** where several notes or solutions cover the same
     material (user, classmates, lecturer), compare spot by spot in
     `<work>/text/sources_comparison.md`: agree (confirmed), disagree (conflict
     – ask), only once (single source – unclear spots go to the user). Mark
     confirmed spots in `OPEN_QUESTIONS.md` / `TO_VERIFY.md`, never close them
     for good.
3. **Interview the user** (one AskUserQuestion call, up to 4 questions, skip
   what the material answers):
   - What is **not** on the exam? Chapters/files found (multiSelect), plus
     „everything is relevant“ and „not known yet – keep everything“; a page or
     paragraph limit goes in „Other“.
   - Exam format (written with sub-questions / MC / mixed / unknown) and
     allowed aids (formula sheet in the folder?).
   - Which old tests come from the same lecture and lecturer
     (`references/old-tests.md`).
   - Files that are reference only (textbook) or must not be used
     (AI-generated, other course, outdated version).
   - Material language if not obvious.
   - Summary output: HTML learning page (left TOC, content zoom, collapsible
     Claude additions), PDF, or both.
   Ask follow-ups on unclear note spots the same way, in batches.
4. **Write the files.** Course `CLAUDE.md` from the template (preferences, exam
   facts, a sources table with every file, page ranges per chapter, `<work>`
   file list), `<work>/SESSION_LOG.md`, `<work>/OPEN_QUESTIONS.md` (every
   `[UNCLEAR]`/`[CHECK]`/`[GAP]`, numbered, with page), `<work>/TO_VERIFY.md`
   (every assumption and Claude addition). A folder that already uses German
   names (`OFFENE_FRAGEN.md`, `NACHPRUEFEN.md`, `[UNKLAR]` …) keeps them. Before
   changing any user file, copy it to `<work>/backup/`.
5. **Summarize everything in scope** into
   `<work>/sources/<Course>_Summary.html` (see below): one numbered chapter per
   main topic; „Still missing“ overview at the top; ★ exam-relevant spots as
   `.alarm.exam` plus their own section; every gap/`[UNKLAR]` as
   `.alarm.missing` with its #number; every Claude addition as
   `.alarm.added`; exercises with full task text and a fully explained
   solution (every step, how and why), slips of the lecturer's material as
   `.alarm.slip` (mistakes in the user's or classmates' own notes never go
   into the summary – ask about them in the interview instead); per topic a box listing what the allowed formula sheet
   covers; a symbol table for math courses; clean SVG drawings where the notes
   have sketches. Output as chosen: learning page (`references/learning-page.md`;
   empty question bank until the review) and/or
   `<Course>_Summary_Draft.pdf` in the course folder (named in the material's
   language, e.g. `<Kurs>_Zusammenfassung_Entwurf.pdf`); look at a few pages,
   re-run `extract_texts.py`.
6. **Correctness check** (SKILL.md, top priority).
7. **Stop for review:** report what was indexed, transcribed and summarized;
   ask the open questions with AskUserQuestion. Exam questions only after the
   user reviewed the summary (then SKILL.md workflow step 0).

## Summarizing the material

- **Check existing summaries first:** read their text extract, find which
  decks they cover, summarize only the rest. Keep the HTML source in
  `<work>/sources/` and re-run the extract script afterwards.
- **Distinct names:** rename a generic existing summary (`Zusammenfassung.pdf`
  → `SE-Zusammenfassung-Teil1_LifeCycle-bis-Storyboard.pdf`) and name the new
  one in the same pattern (`…-Teil2_<first>-bis-<last topic>.pdf`); mention
  the rename in the reply.
- **Match the existing summary's language and style** (German explanations
  with the slides' English terms; DEFINITION / MERKSATZ / ERGÄNZUNG boxes; a
  "topic → source file" table at the top; an "Abgrenzungen" table and
  self-check questions at the end).
- **Mark anything not on the slides** as an addition (ERGÄNZUNG).
- **Start from `assets/summary-template.html`** (print CSS, box types,
  exercise and theory-question markup; replace `__TITLE__`/`__SUB__`). Keep its
  CSS flat (no `@media`): `build_lernseite.py` scopes every rule under `.doc`.
- **Alarm boxes must stand out** – the user wants missing and important
  content loud, not pale tints. Solid-header boxes (thick border, saturated
  header bar, white text, tinted body): `.alarm.missing` (red – missing or
  unclear, still needs input; also the „Still missing“ overview),
  `.alarm.added` (orange – Claude added, interpreted or assumed),
  `.alarm.exam` (magenta – ★ Prüfungsrelevant), `.alarm.slip` (brown –
  slide or class solution of the lecturer is wrong; never for the user's own
  or classmates' notes). Inline:
  `<span class="flag missing">FEHLT</span>`, important terms
  `<mark class="hl">` (solid yellow, bold). Alarms only where they apply,
  never on clear content. Normal content uses the calm
  `.box.def/.merk/.fs/.info` boxes.
- **Claude's own additions and solutions go into `.alarm.added`** (solutions
  to sheets without a class solution, old-exam solution sketches,
  general-knowledge notes). On the learning page these are **collapsed**
  (orange header visible, body on click); the sidebar switch „Ergänzungen von
  Claude zeigen“ opens all. `.alarm.missing` / `.alarm.slip` (CHECK,
  conflicts, slips) stay **big and visible** until reviewed – never collapse
  them.
- **Ask PDF or HTML.** HTML only: build the learning page from the summary
  source right away (empty `const QUESTIONS = [];` hides the quiz tab) and
  skip the PDF. PDF: write HTML + print CSS and render it headless
  (`google-chrome-stable --headless --no-pdf-header-footer --print-to-pdf=out.pdf file.html`,
  or WeasyPrint); look at a page or two (`pdftoppm -png -r 50`) before
  handing it over. No Chrome (macOS): use the cached Playwright Chromium
  (`references/quiz-page.md`).
- Exclude folders the user calls irrelevant (project or personal notes).
