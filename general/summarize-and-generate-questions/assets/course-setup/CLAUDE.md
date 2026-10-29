# __COURSE__ (__SCHOOL__, __SEMESTER__, __LECTURER__)

**New session? Read `__WORK__/SESSION_LOG.md` first** (what was done, key facts, next steps). Update it at the end of every session.

Exam preparation folder. Keep this file updated whenever the user states a new preference or a fact about the exam.

## User preferences

- **Never assume anything.** A fact counts as settled only when two or more independent sources agree (script, the user's notes, classmates' notes, solutions). One unclear source, disagreeing sources or no source: do not guess or fill in – mark it, add it to `__WORK__/OPEN_QUESTIONS.md` and ask the user. Ask for more sources (classmates' notes) where only one exists. Questions are only written on settled content.
- Accuracy has top priority: the user learns from the transcriptions and summaries, so they must be error-free. Transcribe handwriting exactly as written. If something looks wrong, do not silently correct it: keep the original, add a `[CHECK: …]` note and ask the user.
- Do not interpret unclear content (illegible handwriting, ambiguous scope, unclear exercise solutions). Ask the user instead (interview form, AskUserQuestion) and mark open points as `[UNCLEAR: …]` until they are answered.
- Spots the notes mark as exam-relevant (e.g. „Prüfungsrelevant“, „Prüfungsfrage“, "exam question") will be asked for sure: own section in the summary (★), always covered by exam questions. Content marked as not exam-relevant is left out.
- Open points go into `__WORK__/OPEN_QUESTIONS.md` (numbered, with source page). Every manual change by the user (before/after), every assumption and every Claude addition goes into `__WORK__/TO_VERIFY.md`. Never close these for good: when new material arrives (another script, classmates' notes), compare against both lists and update them.
- Notes from other sources (classmates' photos, scans) count as the user's own notes.
- Summary: loud alarm boxes only where something is missing, added by Claude, exam-relevant or solved wrongly in class – never on clear content. Generous spacing, bullet lists instead of long one-liners. Exercises always show the full task text plus the solution.
- New info: update transcription, `OPEN_QUESTIONS.md`, `TO_VERIFY.md` and the summary source right away; rebuild the PDF only when the user asks.
- Work order: 1) extract all text (incl. handwriting) and write the summary, 2) the user reviews it, 3) only then generate exam questions.
- Material language: __LANG__ (summaries and transcriptions in this language).

## Exam facts (from the user)

- Scope: __SCOPE__
- Not on the exam: __NOT_IN_SCOPE__
- Format: __FORMAT__
- Allowed aids: __AIDS__

## Sources

| File | What it is |
|---|---|
| __FILE__ | __WHAT__ (pages per chapter) |

Reference only (look things up, do not summarize): __REFERENCE_ONLY__
Never use as a source: __IGNORE__

## Claude working files (`__WORK__/`)

- `__WORK__/text/` – plain-text extracts of every PDF (`===== Seite N =====` page markers) plus transcriptions of handwriting (`*_transcription.md`). Read these instead of the PDFs.
- `__WORK__/INDEX.md` – index of the extracts; pages without text are flagged (image-only, check visually).
- `__WORK__/tools/extract_texts.py` – re-run `python3 __WORK__/tools/extract_texts.py . --out __WORK__` after new files arrive (only changed files are re-extracted).
- `__WORK__/sources/` – HTML sources of the summary (and later the quiz questions).
- `__WORK__/backup/` – copies made before Claude changes a user file.
