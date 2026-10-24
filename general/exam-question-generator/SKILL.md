---
name: exam-question-generator
description: Generate applied, reasoning-style multiple-choice exam questions from a study document (lecture slides, summaries, textbook chapters). Use this whenever the user uploads or references study material and asks for practice questions, a quiz, self-test questions, or exam prep — especially when they want questions that go beyond simple recall (e.g. "make it harder", "more like real exam questions", "questions that make me actually think", "not just picking the bullet point off the slide"). Also use when the user asks to reverse-engineer, replicate, or match the style of example exam questions they paste in. Also covers summarizing new lecture decks into a study-summary PDF first, and building an interactive HTML practice test (clickable question grid on the left, auto-advance on answer, back and check buttons, random-question-order toggle, extended mode). Extracts course PDFs to plain text once so later runs read text, not PDFs. Calibrated on real exam quizzes: always multiple choice with 4 options, mostly exactly 1 correct (sometimes 2–3, very rarely all 4), slash-form stems like "Welche Aussage/n beschreibt/en …"; never asks who/when/source-citation questions like "Von wem stammt".
---

# Exam Question Generator

Turns study material into multiple-choice questions that test **application and
discrimination**, not just recall of bullet points. This is the difference between
"list the five things on the slide" and "given a new example, which of these is one
of the five things" — the second is much closer to what real exams ask, and much
harder to answer by pattern-matching the slide text.

## Hard rules (always apply)

- **Every question is multiple choice** with exactly 4 options (A–D) and
  **1–4 correct answers** (never 0). Mix, calibrated on real exam quizzes (see
  "What the real exams look like"): about **55 % with 1 correct, 30 % with 2,
  12–15 % with 3**; all 4 correct at most once per 30 questions and only when
  the source lists exactly those four items as one set. Scoring is
  all-or-nothing: a question counts only if exactly the correct set is ticked.
  No open/free-text, true/false or fill-in-the-blank questions — convert source
  examples into this format.
- **Stems use the exam's grammar.** Default: a slash form that hides the
  count — „Welche Aussage/n beschreibt/en …?“, „Welche/r Begriff/e …?“,
  „Welche Option/en treffen zu?“, „beschreib/en/t“. Superlatives („am besten“,
  „am ehesten“, „am deutlichsten“, „am unmittelbarsten“, „hauptsächlich“) are
  fine in a slash-form stem with any count (the real exams use them with 1–3
  correct) and in a singular stem with exactly one correct („Welche Aussage
  unterscheidet … am deutlichsten?“).
  A singular „Welche/r/s“ stem („Welcher Bestandteil …?“, „Welches Prinzip
  …?“, „Welche Aussage beschreibt …?“) only when exactly one option is correct;
  a plain plural „Welche“ stem („Welche Aussagen …?“, „Welche der folgenden
  sind …?“) only when at least two are correct — in the 45 real questions these
  two forms never contradicted the key (9/9 each). W-questions („Was …?“, „Wie
  …?“, „Warum …?“) are neutral: mostly one correct, but the real exams also had
  „Warum …?“ and „Was muss …?“ with 2 and „Was sind …?“ with 3 correct. Mix the
  forms roughly like the exams (≈ 35 % slash, 20 % singular, 20 % plural,
  25 % W-questions) so the grammar alone never gives the answer away. Never „Welche EINE“,
  „genau eine“, „die einzige“.
- **Options are short and parallel, like the exam's.** Often a single term
  with a full stop („Controller.“, „Visibility.“, „Increment.“), otherwise one
  line. All four options have similar length and the same grammatical shape;
  the correct option must not be the longest or most qualified one by habit
  (the build checks this). Don't over-correct either: if the correct option
  is almost never the longest (near 0 %), "the longest is always wrong"
  becomes the cue. Aim for about 25 % (chance level with four options); ties
  don't count. Put precision into the wording of all four options, not only
  into the right one.
- **Every correct option must be unambiguously backed by the source, every
  wrong option clearly wrong for a nameable reason.** With multi-answer, an
  "arguably true" distractor makes the question unanswerable — drop it.
- **No questions about in-class activities or exercises.** Slides often
  contain workshop instructions ("Activity: What did I hire?", "Mini-Aktivität",
  "Übung", "Activity 3", "in Teams von 4–5", "15 Minuten", "Produktkarten") —
  team size, timing, materials and steps of an exercise are not exam content.
  Never ask about them, and don't cite them as the source in explanations
  ("Activity 3: …"). If an activity demonstrates a concept, test the concept
  itself (e.g. classifying a job as functional/emotional/social), with no
  reference to the activity.
- **Spell out abbreviations in brackets, every time they appear** — in
  stems, options, explanations and summaries: `<ul>` (unordered list),
  `<ol>` (ordered list), `<li>` (list item), `<em>` (emphasis), `<a>`
  (anchor), DOM (Document Object Model), JTBD (Jobs To Be Done), DoD
  (Definition of Done), `px` (pixels), `fr` (fraction) … The expansion helps the
  learner recognize and remember the term. In quizzes expand in every
  question (each question stands alone). In summaries: HTML (HyperText Markup
  Language) tags/attributes/units every time outside code blocks; acronyms
  like JTBD/DOM/CSS at least at their first occurrence in each section, so the
  text stays readable. Never let the expansion give away
  the answer — if the question asks what an abbreviation means, leave that one
  unexpanded in the stem/options and expand it in the explanation.
- **Don't quiz the details of the slides' own examples.** Example cases on
  the slides (a sample product vision like "Rheticus Experience", a case
  study, a demo app) only illustrate a concept — never ask what that specific
  example's competitor, target group, wording or numbers were. Test the
  concept the example illustrates, ideally applied to a new, invented case
  (archetype A2). Exception: the example *is* the concept (e.g. the milkshake
  story as the canonical JTBD illustration) — then ask about the lesson it
  teaches, not its trivia.
- **No questions about people, authorship or citations.** Never ask "Von wem
  stammt …", "Wer hat … definiert/entwickelt", "Wer prägte den Begriff …",
  "In welchem Jahr …", "Auf welcher Folie …" or any other who/when/where-cited
  question. Names, years and sources may appear as context inside a question,
  but they must never be what is being tested, and options must never be a
  list of names or years. Test the concept itself instead.
- **Explanations never refer to options by letter or position.** Options are
  shuffled at runtime, so "B ist …", "C nennt …", "die erste Option" will point
  at the wrong answer. Name each option by a short quote of its own text
  instead (e.g. „Start-Button“ ist ein UI-Element). The same goes for
  position words: never „die letzten beiden“, „die ersten drei Einwände“,
  „die letzte Aussage“ — quote the options instead (the build rejects these).
  This also applies to plain-text sets, since users may reorder or print them.

## When plain recall questions are fine vs. when to use this skill

If the user just wants a quick self-check ("quiz me on this chapter"), simple
"select all that apply" recall questions are a reasonable default and faster to
produce. Reach for the workflow below when the user:
- explicitly asks for harder / more exam-like / more "applied" questions,
- pastes example questions from a real exam and asks for more like them,
- says recall questions felt too easy or that they want questions that "make me
  think" rather than "quote the slide back",
- is preparing for an exam known to test understanding over memorization (this is
  common — professors who write "Abgrenzungen" / "distinguish X from Y" tables or
  give worked examples are usually testing exactly this).

## What the real exams look like (calibration)

Calibrated on 45 real quiz questions of the course this skill was built for
(FH Vorarlberg „Projektbasierter Einstieg ins Software Engineering“ plus an
earlier run of the lecturer's HCI quizzes; full list with keys in
`<course>/06_Claude/text/05_Quizes/ALLE_Quizfragen_Analyse.md`):

- **Format:** sheets of 5 questions, one per newest slide deck, each about the
  deck's **central message** (JTBD: the product is only one possible solution;
  HTML: structure and meaning; Product Vision: which block names the
  competitor). Little slide trivia.
- **Correct count:** 62 % one, 24 % two, 11 % three, 2 % all four (a persona
  dimensions list where every option was a real dimension).
- **Stems:** slash forms („Welche Aussage/n entspricht/en …“), superlatives
  inside slash forms („… beschreibt/en … am besten?“ with 2–3 correct), short
  direct questions („Was sind …?“, „Was bedeutet …?“), reverse definitions
  („Welches Prinzip beantwortet die Frage „Wie denke ich, dass es
  funktioniert?“?“), cause/effect („Was passiert mit der Reaktionszeit, wenn
  …?“), rationale („Warum betonen X, dass …?“). Names and years appear only as
  context („Nach George Olsen (2004) …“).
- **Options:** short and parallel, often one term; distractors come from the
  neighbouring decks (the HTML question offers CSS and JavaScript duties as
  wrong options).
- **Types:** ≈ 60 % recall, 40 % applied; about 10 % read code or a formula
  (a CSS rule, one JavaScript line, a code handout, Fitts' law with renamed
  variables).

**When the course folder contains real exams or quizzes, re-calibrate:**
read them (or their text extract) first, tabulate correct-count mix, stem
forms, option length and archetypes, and follow them wherever they differ from
the defaults here. Say in the reply what you calibrated on.

## Two families of archetypes

A good practice set needs both families below. **Recall archetypes** ask "what
does the source say?" — they're faster to write, good for first-pass memorization,
and how most of a typical slide deck gets tested. **Applied archetypes** ask "can
you use what the source says?" — they're what turns a passable quiz into one that
actually predicts exam performance, because they can't be answered by
pattern-matching text.

Every question you generate should map to one archetype below. Don't repeat one
pattern 20 times — real exams vary the angle of attack, and so should you. See
"Building a mixed set" at the end for suggested ratios.

## Recall archetypes

These test whether a fact was learned, not whether it can be applied. All four
options should be plausible things that *could* have been on the slide — a
distractor that's obviously off-topic or absurd doesn't test anything.

### R1. List membership ("which of these belong")
Give 4 items; usually 1–3 belong to a taught list/category, the rest don't (all
four only in the rare case allowed by the Hard rules). Distractors should be real terms from an *adjacent* topic in the
source, not made up — that's what makes the wrong ones tempting.

> Which of the following is a subcharacteristic of [X] in [source model]?
> A) [wrong — belongs to a different, adjacent category in the same model]
> B) [correct — from X's own list]
> C) [wrong — belongs to yet another adjacent category]
> D) [wrong — a neighboring term from the same chapter]

### R2. Single-fact definition
Ask for the definition or meaning of a single taught term. One clearly correct
option; three each swap in a different specific wrong detail (wrong scope, a
neighboring term's definition, a plausible but unsupported claim).

> What is [term], according to the course material?
> A) [a different concept's definition]
> B) [a plausible-sounding but unsupported claim]
> C) [the correct definition]
> D) [an overly narrow or overly broad version of the definition]

**Reverse variant (common in the real exams):** give the definition, guiding
question or a quote and ask for the term — „Welches Prinzip beantwortet die
Frage „Wie denke ich, dass es funktioniert?“?“ → Visibility. ✗ /
Conceptual/Mental Model. ✔ / Feedback. ✗ / Constraints. ✗ Options are bare
terms from the same list.

### R3. Sequence / order recall
For any taught process, cycle, or pyramid with a fixed order, ask for that order
or for "what comes after step N." Distractors should be real steps in the wrong
order or with one step swapped for one from a different taught sequence.

### R4. Count / quantity recall
"How many X are there" or "which of these numbers is correct" for any taught
list with a specific count (e.g. "8 quality characteristics", "5 Norman
principles"). Distractors: off-by-a-few numbers that sound equally plausible.

### R5. Term ↔ purpose pairing
Match a term to its purpose, the phase/artefact it belongs to, or the problem it
solves (e.g. "Wofür wird ein Storyboard eingesetzt?", "Welches Artefakt
entsteht in Phase X?"). Distractors: the purpose/phase of a different real term
from the same document. Never pair terms with authors, years or slide numbers
(see Hard rules).

**Complete-mapping variant:** for a trio or quartet of related terms
(Mistake / Slip / Lapse; Product Owner / Scrum Master / Developers) each option
maps *all* terms at once, and only the fully correct mapping counts. A fourth
option can be a true meta statement about the set („Alle drei Begriffe werden
unter dem Begriff Error zusammengefasst.“), which makes the question 1- or
2-correct. Stem: „Welche Option/en treffen gesamt korrekte Aussagen über …?“

### R6. Rationale and effect ("warum" / "was passiert, wenn")
Ask *why* the source recommends something or *what happens* to one quantity
when another changes. Correct options = the reasons/effects the source gives;
distractors = plausible but unstated reasons, reversed effects, wrong growth
shapes.

> Warum betonen Greenberg et al., dass Skizzen „von Hand, nicht mit einem
> Zeichenprogramm“ erstellt werden sollen? → zu genaue digitale Zeichnungen
> bremsen die Ideenfindung ✔ · Handskizzen fördern viele schnelle Ideen ✔ ·
> Skizzen sollen ausgedruckt werden ✗ · Software erzwingt visuelle Hierarchie ✗
>
> Was passiert laut Hick-Hyman-Gesetz mit der Reaktionszeit, wenn die Zahl
> gleich wahrscheinlicher Alternativen steigt? → sinkt linear ✗ · steigt
> logarithmisch ✔ · bleibt konstant ✗ · steigt exponentiell ✗

## Applied archetypes

These test whether the concept's *boundary* was understood, using new wording,
new examples, or new framing the learner hasn't seen verbatim. This is the
harder, more exam-realistic half of a good set.

### A1. Near-duplicate discrimination
Give 3–4 phrasings that are superficially similar (same topic, same sentence
structure, similar length) but only one satisfies the concept's actual definition.
The wrong options should each violate the definition in a different, plausible way.

**Source material needed:** a definition with a clear boundary condition (e.g.
"task-centric, not tool-centric"; "abstract from UI, not implementation-specific").

**Template:**
> Which of the following [formulations/examples/descriptions] best satisfies
> [concept]?
> A) [violates the boundary one way]
> B) [violates it a different way]
> C) [satisfies the definition correctly]
> D) [violates it a third way, often by being too narrow/specific]

**Worked example (from a task-centric-vs-tool-centric user story concept):**
> A) "I want to enter a CD title into a search box and start the search." (names
> the UI mechanism — tool-centric)
> B) "I want to click the search button after entering search terms." (also
> names UI — tool-centric)
> C) "I, as a hurried shopper, want to find a specific CD in the store." (states
> only the goal — correct)
> D) "I want to refresh the search results." (a sub-action, not the actual goal)

### A2. Novel application
Take a concept taught with the *slide's own example* and force the learner to
apply it to an example that **never appears in the source material**. This is the
single highest-value thing you can do, because it's impossible to answer by
recognizing text — the learner has to actually understand the category boundary.

**Source material needed:** a category or classification concept (e.g. User
Objects, stakeholder vs. user, mental model vs. system model).

**Template:**
> Which of the following is most likely a(n) [category] in a [new, unseen
> context]?
> A) [correct — a plain, user-facing noun from the new domain]
> B) [wrong — an implementation/architecture term from the new domain]
> C) [wrong — a service/backend term from the new domain]
> D) [wrong — a technical protocol/interface term from the new domain]

**Worked example (User Objects concept, applied to a new domain — online shop —
that never appeared in the source):**
> A) Warenkorb (shopping cart) — correct: a user-facing noun that would appear on
> the UI
> B) Product Repository — wrong: backend/data-layer term
> C) Order Service — wrong: architecture/microservice term
> D) API-Endpunkt — wrong: implementation detail, never surfaces to the user

When writing this archetype: **invent the new domain yourself.** Pick something
adjacent to but distinct from every worked example already in the source document
(if the source uses a record store, use a shop, a fitness app, a library — anything
not already used). This is what makes the question un-Googleable and
un-skimmable.

### A3. Statement-truth-checking
List 3–4 short statements about one concept. Only one is fully and precisely
supported by the source; the rest are each wrong in a specific, common way. This
tests whether the learner knows the *exact scope* of a definition, not just its
gist.

**Source material needed:** a definition or a list of properties (these are
usually explicitly bulleted in slides — properties, characteristics, features).

**Common ways to make a false statement from a true one — use a different one for
each wrong option so they don't all fail for the same reason:**
- **Overgeneralize a qualifier away**: source says "mental models are
  *incomplete, possibly contradictory*" → false statement: "mental models are
  always complete and consistent."
- **Universalize something that varies per person**: source implies mental
  models are individual → false statement: "mental models are identical across
  all users."
- **Narrow a multi-part definition to only one part**: source says a model
  includes both *structure and behavior* → false statement: "mental models
  describe exclusively the structure of a system."
- **Swap in a related-but-different concept's property.**
- **Invert cause and effect, or invert a comparison** (e.g. swap "usability" and
  "UX", or swap "Gulf of Execution" and "Gulf of Evaluation" — see archetype 5).

**Template:**
> Which statement about [concept] is supported by the course material?
> A) [overgeneralized/absolute version — wrong]
> B) [universalized-across-people version — wrong]
> C) [narrowed-to-one-part version — wrong]
> D) [the actual, precisely scoped claim from the source — correct]

### A4. Contextual decision reasoning
Describe a small scenario or design decision, then ask which single piece of
information (out of several real, source-backed options) is most decisive for
that decision. All four options should be real facts/categories from the source
— the test is *relevance to the specific decision*, not whether the option itself
is true.

**Source material needed:** a checklist, a set of attributes/dimensions belonging
to one bigger concept (e.g. persona attributes, task analysis questions, prototype
dimensions).

**Template:**
> [Short decision scenario, e.g. "Which persona attribute matters most when
> deciding whether to include a step-by-step tutorial?"]
> A) [an attribute of the concept, but not the decisive one for this scenario]
> B) [another real attribute, not decisive here]
> C) [the attribute that actually drives this specific decision — correct]
> D) [another real but irrelevant-to-this-decision attribute]

**Worked example (persona attributes → tutorial decision):**
> A) Persona's Psychographics — real attribute, not decisive here
> B) Biographic Background — real attribute, not decisive here
> C) Specific Knowledge/Proficiency — correct: this is literally what "does this
> person need a tutorial" depends on
> D) Product's Relationship to the Persona — real attribute, not decisive here

### A5. Definitional contrast ("what distinguishes X from Y")
Take a pair of concepts the source explicitly or implicitly contrasts (course
"Abgrenzungen" tables are a goldmine for this) and ask what *most* distinguishes
them — not just any true fact about X, but the fact that actually separates it
from its near-neighbor Y.

**Source material needed:** a pair of related-but-distinct concepts (Storyboard vs.
UI sketch collection, Usability vs. UX, Gulf of Execution vs. Gulf of Evaluation,
User Scenario vs. Use Case).

**Template:**
> Which statement most clearly distinguishes [X] from [a superficially similar
> Y]?
> A) [true of X, but describes a secondary property, not the actual
> distinguishing one — plausible distractor]
> B) [describes something closer to Y or to a different concept entirely —
> wrong]
> C) [the actual defining contrast — correct]
> D) [true-sounding but unsupported or backwards claim]

**Worked example (Storyboard vs. plain UI sketches):**
> A) Storyboards show the sequence of screens — true, but this is a property of
> *sequential* storyboards specifically, not the thing that separates a
> storyboard from a sketch collection in general
> B) Storyboards serve mainly visual design — wrong, this undersells the point
> C) Storyboards represent how a design is used to reach a user goal within a
> scenario — correct: this is the actual definitional core
> D) Storyboards are typically made earlier in the design process — true-ish but
> not the distinguishing property being tested

### A6. Scenario explanation ("warum passiert das?")
Describe a concrete situation with an observable effect and ask which
statements *explain* it with the taught concepts. Correct options apply
different concepts that each contribute (often 2–3 correct); wrong options
misapply a concept, invert it, or claim an absolute („Nur Farbe allein
garantiert Sichtbarkeit.“).

> Eine Banking-App zeigt eine wichtige Sicherheitswarnung fett über dem
> „Login“-Button, oben läuft gleichzeitig ein animiertes Werbebanner. Welche
> Aussagen erklären am besten, warum Benutzer die Warnung übersehen? →
> Aufmerksamkeit ist auf den Login-Button (Ziel) fokussiert ✔ · Bewegung im
> Banner zieht Aufmerksamkeit an ✔ · Warnung liegt außerhalb des Locus of
> Attention ✔ · Nur Farbe garantiert Sichtbarkeit ✗

Differs from A4: A4 asks which fact *decides* a design choice; A6 asks which
concepts *explain* an observed outcome.

## Code and formula archetype

### C1. Read code or apply a formula
Put a short snippet into the question's `code` field (a CSS rule, one or two
JavaScript lines, a tiny HTML block) or give a formula with renamed variables,
then ask what a part does, what the user sees, or which statements about the
line are true. Distractors: confusing the roles of the parts (selector vs.
property, event type vs. handler), claiming immediate execution, picking a
property that exists but does something else, swapping numerator and
denominator. Use it whenever the source teaches code or formulas — the real
exams spend about one question in ten on it. Counts as applied (`y:'C1'`).

> Welche CSS-Eigenschaft in `.container {display: grid; grid-template-columns:
> 1fr 1fr; gap: 10px;}` ist hauptsächlich dafür verantwortlich, dass beide
> Spalten gleich breit sind? → display: grid. ✗ · gap: 10px. ✗ ·
> grid-template-columns: 1fr 1fr. ✔ · container. ✗
>
> Welche Aussage/n trifft/treffen auf `button.addEventListener("click",
> handleSearch);` zu? → "click" ist der Event Type ✔ · button ist die Event
> Source ✔ · handleSearch ist der Event Handler ✔ · addEventListener führt
> handleSearch sofort aus ✗

## Building a mixed set

Don't default to all-recall or all-applied. Unless the user specifies otherwise:

- **Default mix for a general practice set:** roughly 55 % recall (R1–R6) and
  45 % applied (A1–A6, C1), close to the real exams' 60/40 with a little extra
  practice on the harder half. If the source teaches code or formulas, about
  10 % of the set is C1.
- **Cover each deck's central message first.** The real quizzes ask about one
  question per deck, aimed at its core claim (title slide, learning objectives,
  summary/merksatz slide). Before writing detail questions, give every deck's
  core claim at least two questions from different archetypes; then fill in
  the details.
- **If the user asks for "harder" or "more like these example questions"**
  (i.e. they've pasted applied-style questions and want more of that), shift to
  roughly 70–80% applied.
- **If the user wants a fast first-pass / "just quiz me"**, roughly 70–80% recall
  is fine — they likely want breadth and speed over depth at this stage.
- **Within each family, rotate archetypes** rather than reusing one repeatedly.
  A 20-question set might look like: 2 of each R1–R6 (minus one), and 1–2 of
  each A1–A6 plus 1–2 C1 if the source has code or formulas.
- **Match archetypes to what the source actually supports.** Not every document
  has explicit contrast tables (A5) or numbered sequences (R3) — use what's
  there rather than forcing an archetype onto material that doesn't fit it. It's
  fine for the mix to lean toward whichever archetypes the source material
  naturally supports.
- **State the mix you used** in a short line when delivering the set (e.g. "10
  recall, 10 applied, covering topics X–Y") so the user knows what they're
  getting and can ask to shift the balance.

## Workflow

00. **Work from a plain-text extract, not from the PDFs.** Look for
   `<course>/06_Claude/text/` (one `.txt` per PDF with page markers, plus
   `INDEX.md`). If it is missing or older than the slides, run
   `python3 scripts/extract_texts.py <course-root> [--skip <private folder>]`
   (needs poppler's `pdftotext`; Node.js for practice tests). It only
   re-extracts changed files. Copy the script to `<course>/06_Claude/tools/` and
   add a short `README.md` there, so later sessions find it. Photos of exam or
   quiz sheets have no text layer: read them once and transcribe them verbatim
   (original language, marked answers) into a `.md` under `06_Claude/text/`.
   `INDEX.md` flags image-only pages; look at those slides visually
   (`pdftoppm -png -r 55 -f N -l N`) and describe important diagrams in the
   README.

0. **Ask how many questions** before generating anything, unless the user
   already gave a number. Use the AskUserQuestion tool with a few sensible
   options (e.g. 20 / 50 / 120, "Other" is added automatically) and, if the
   material spans several decks, ask in the same call whether to cover all
   decks or only the newest ones. Don't guess the count — set size drives the
   per-topic distribution and the time the user will spend.
   If the user also asked for a summary, do the summary step (see "Summarizing
   the material first") before writing questions — the questions are then
   written against both the slides and the summary.

1. **Read the whole source text first**, and any real exams/quizzes in the
   folder (calibrate on them, see "What the real exams look like"). Note each
   deck's central message. Don't generate questions paragraph-by-paragraph —
   skim for the material that supports each archetype:
   - Bulleted lists of items under one category → R1, and if the list has an
     explicit boundary/qualifier, also A1/A3
   - Single named definitions → R2; terms with a clear purpose/phase/artefact → R5
   - Numbered steps, cycles, pyramids → R3
   - Lists with an explicit count ("8 characteristics", "5 principles") → R4
   - Classification/category concepts with a worked example → A2
   - Bulleted lists of properties/characteristics → A3
   - Checklists or multi-attribute concepts (personas, task analysis, prototype
     types) → A4
   - Explicit contrast tables (often literally labeled "Abgrenzung",
     "Unterschied", "vs.", or a "don't confuse X with Y" note) → A5
   - Recommendations with a reason ("so that …", "because …") and laws or
     models with a direction of effect → R6
   - Concepts that explain observable behaviour (attention, errors, feedback,
     breakdowns, burndown shapes) → A6
   - Code snippets, syntax anatomy, formulas → C1
2. **For archetype A2 specifically**, actively invent a new domain/example not in
   the source. Do this deliberately — it's the single biggest lever for making a
   question un-skimmable.
3. **Write each wrong option with an intentional, nameable reason it's wrong** (a
   boundary violation, an overgeneralization, a related-but-wrong category, an
   irrelevant-but-true fact). If you can't articulate why an option is wrong in
   one clause, it's a weak distractor — replace it. Never include a "joke" or
   obviously-absurd option; every option should be something a half-prepared
   student would plausibly pick.
4. **Always 4-option multiple choice, mostly with exactly 1 correct** (see
   Hard rules for the mix and the stem grammar). If the source's own example
   questions use another format (open, true/false), rewrite them into this
   format and mention that in the reply. The archetype templates show one
   correct option — keep it that way for about half of the set; make one or two
   more options correct only where the source clearly supports it (e.g. A3:
   two precisely supported statements; A2: two items that both fit the
   category; R1 lists; A6 explanations).
   Then even out option length: if the correct option is the longest, shorten
   it or lengthen the distractors.
   Before delivering, scan the set for any who/when/source-citation question
   ("Von wem stammt …", "Wer …", "Welches Jahr …") and replace it with a
   question about the concept itself.
5. **Give every question a detailed explanation** (the user wants to learn
   from the answer box, not only check it). Three parts, separated by `<br>`
   in the HTML quiz:
   - **Lösung:** why the correct option(s) are right, citing the specific
     source fact (slide number, summary section, notes), quoted where possible;
   - **Die anderen:** *every* wrong option, named by a short quote of its text,
     with the nameable reason it is wrong (which neighbouring concept it
     really describes, what it inverts, that it is not in the source);
   - optional **Merke:** / **Logik:** – one-line takeaway, mnemonic or the
     reasoning behind an order/mapping.
   Typically 3–6 sentences. Don't label the parts „Richtig:“/„Falsch:“ – the
   quiz's result line already says „Richtig.“/„Falsch.“, and „Falsch. …
   Richtig: …“ reads confusingly.

   Example (2 correct):
   > `<b>Lösung:</b> Verifikation prüft gegen die Spezifikation – die ist
   > erfüllt, also ist die Software verifiziert. Validierung prüft die Eignung
   > für den Einsatzzweck (Folie 74) – die fehlt.<br><b>Die anderen:</b>
   > „validiert, weil die Tests bestanden sind“ verwechselt die Begriffe;
   > „Verifikation hätte den Fehler sicher gefunden“ – unmöglich, was nicht in
   > der Spezifikation steht, kann eine Prüfung gegen sie nicht vermissen.<br>
   > <b>Merke:</b> Korrekt nach Spezifikation kann trotzdem unbrauchbar sein.`
6. **Check every question before building**: re-read stem, options and key
   against the source. Replace an option that is only "arguably" right or
   wrong (e.g. it also partly fits the neighbouring definition) with one that
   is unambiguous, and say in the reply which questions you changed.
7. **If a fact needed to make a good question isn't actually in the source
   material**, say so rather than inventing exam-sounding content that isn't
   backed by the document — flag it as general knowledge, the same way you would
   in a normal answer.

## Summarizing the material first

When the user wants a summary alongside (or before) the questions:

- **Check for existing summaries in the folder first.** Read their text
  extract (`06_Claude/text/…`, see workflow step 00) and find out which decks
  they already cover. Only summarize what is not covered yet; don't
  re-summarize the same decks. Keep the summary's HTML source in
  `06_Claude/sources/` so it can be edited later, and re-run the extract
  script afterwards so the new PDF is in the text folder too.
- **Give summaries distinct names.** If an existing summary has a generic name
  (e.g. `Zusammenfassung.pdf`), rename it to say what it covers (e.g.
  `SE-Zusammenfassung-Teil1_LifeCycle-bis-Storyboard.pdf`) and name the new one
  in the same pattern (`…-Teil2_<first>-bis-<last topic>.pdf`). Mention the
  rename in the final reply.
- **Match the existing summary's language and style** (e.g. German
  explanations with the slides' English terms; boxed callouts such as
  DEFINITION / MERKSATZ / ERGÄNZUNG; a "topic → source file" table at the top;
  an "Abgrenzungen" table and self-check questions at the end).
- **Mark anything not on the slides** as an addition (ERGÄNZUNG) so the user
  knows what to double-check.
- Produce the PDF by writing HTML + print CSS and rendering it with a headless
  browser (`google-chrome-stable --headless --no-pdf-header-footer
  --print-to-pdf=out.pdf file.html`) or WeasyPrint if installed. Look at a page
  or two of the result (`pdftoppm -png -r 50`) before handing it over.
- Exclude folders the user says are irrelevant (e.g. project or personal
  notes folders).

## Output format

**Ask whether the user wants plain text or the interactive HTML quiz** if it
isn't clear. Plain text: numbered questions, options A–D, answer key at the end.

### Interactive HTML quiz (default for sets of ~30+ questions)

One self-contained `.html` file (no external dependencies, works offline by
double-click), saved next to the source material with a distinct name such as
`<Course>-Probetest-<N>Fragen.html`. Required behaviour:

- **Left sidebar = question overview in a calendar-like grid.** One small
  numbered tile per question (grid of ~6–10 columns, grouped or labelled by
  topic). Tiles are clickable and open that question. Tile states are visually
  distinct: unanswered, answered, current; after checking: correct (green) /
  wrong (red). Show a progress counter (answered / total). On narrow screens
  the sidebar collapses above the question or behind a toggle.
- **Normal flow = tick and confirm.** Options are checkboxes (square markers);
  a hint under the stem says "Mehrfachauswahl: eine oder mehrere Antworten
  sind richtig".
  "Antwort bestätigen" (or Enter) records the ticked set and the next question
  appears automatically (~250 ms). Keyboard: 1–4 / A–D toggle, Enter confirm,
  ←/→ navigate.
- **"Instant check" toggle in the sidebar (default on).** On: confirming an
  answer immediately marks right/wrong (missed correct options dashed green), shows the explanation, colours the
  tile and updates a running score ("x / y richtig"); the answer is locked and
  there is no auto-advance, the user continues with Next / → / Enter. Off: the
  auto-advance flow above, solutions only via the Check button. The mode is
  saved with the progress; questions already revealed stay revealed after
  switching modes.
- **Back button** goes to the previous question (answers stay editable until
  checked). A Skip/Next button is fine in addition.
- **Check button ("Prüfen"/"Check")** reveals the results: marks the correct
  option green and a wrong chosen option red on every question, shows the
  short explanation, colours the sidebar tiles, and shows the score (overall and
  per topic). Allow checking with unanswered questions (they count as wrong,
  tiles marked as unanswered). Provide a "Restart" that clears answers.
- **Shuffle option order** once per attempt at runtime so the correct answer's
  position is not a pattern.
- **"Zufällige Reihenfolge" / "Random order" toggle in the sidebar (default
  off)** for the question order. Off: questions in topic order, grid grouped by
  topic. On: questions are shuffled (Fisher–Yates) into a random order; the
  grid, numbering, Back/Next and keyboard navigation all follow that order (grid
  shown as one flat block, tile tooltip shows the topic). Store the order as
  an array of question indices (`seq`) in the saved state; answers, reveals and
  results are keyed by question, not by display position, so toggling never
  loses progress.
  Switching the toggle on draws a fresh order; switching it off restores topic
  order; the current question stays selected. "Restart" re-shuffles if the
  toggle is on. The toggle and the order are persisted with the progress.
- **"Erweiterter Modus" toggle in the sidebar (default off), shown only when the
  bank has extended questions.** Extended questions (`x: 1`) test the same
  concepts as the core set with new examples, new invented domains and other
  angles (mostly applied archetypes, especially A2). Off: only core questions
  exist in grid, numbering, progress and score. On: they join their topic group
  after that topic's core questions (marked with a dot on the tile and an
  "erweitert" pill), and the score adds core/extended rows. Answers stay keyed
  by question, so toggling never loses progress. Offer this mode whenever the
  user wants "everything covered", "more practice" or "the same with other
  examples"; never put a concept only into the extended set — every extended
  question has a core counterpart in the same topic.
- Persist answers in `localStorage` inside `try/catch` so a reload doesn't lose
  progress; the page must work if storage is unavailable.
- Light and dark mode via `prefers-color-scheme`; readable on phone width.

**Build it from the bundled files, don't rewrite the page from scratch:**

- `assets/quiz-template.html` — finished page implementing everything above.
  Copy it to the scratchpad and adapt only the `<title>`, the sidebar
  `<h1>`/subtitle and the `localStorage` `KEY` (new key per quiz, and bump the
  version suffix whenever the question bank changes so stale saves are dropped).
- Question bank = a `questions.js` file:
  ```js
  // c = indices of ALL correct options (1–4). The quiz shuffles options at runtime,
  // so explanations must name options by their text, never by letter (A–D).
  const QUESTIONS = [
  {id:1,t:'Topic',y:'A2',q:'Welche Aussage/n trifft/treffen zu? (HTML allowed)',o:['correct','wrong','correct','wrong'],c:[0,2],e:'Explanation'},
  {id:2,t:'Topic',y:'C1',q:'Welche CSS-Eigenschaft … ist hauptsächlich …?',code:'.box { display: grid; }',o:['…','…','…','…'],c:[1],e:'…'},
  ];
  ```
  `t` topic, `y` archetype R1–R6/A1–A6/C1, `o` exactly 4 options, `c` sorted array of
  correct indices, `e` explanation (HTML; Lösung / Die anderen / Merke, see workflow step 5), `id` unique, optional `code` (shown as a
  code block under the stem), optional `x:1` = extended-mode question. The
  correct-count mix (≈55/30/15) applies to the core set on its own.
- Build + validate in one step:
  `node scripts/build_quiz.js questions.js quiz-template.html out.html`.
  It refuses to build (exit 1, lists problems) on: ≠4 options, `c` not 1–4
  valid indices, a core set (≥ 20) with under 45 % single-answer questions or
  over 25 % three/four-correct, all-four-correct more than once per 30, the
  correct option being the longest in over 40 % of single-answer questions
  (length cue), „Welche EINE“/„genau eine“ stems, superlatives („am besten“ …)
  with several correct options outside a slash-form stem, a „Welcher/Welches …“
  stem with more than one correct option, duplicate ids/questions/options, **any A–D letter reference
  in an explanation** (text inside „…“ quotes and "z. B." are ignored),
  who/when/source questions, and extended questions in a topic without core
  questions. Fix every reported item — never weaken the check
  to make it pass. On success it prints count (core/extended), topic
  distribution, correct-count mix, recall/applied/code mix and the length-cue
  rate; report those to the user. The in-class-activity check also matches words that merely contain
  "aktivität"/"activity" (e.g. „Attraktivität“, an anti-pattern named
  "Activity without goal") — rephrase the stem/explanation; option text is
  not checked.
- No `google-chrome-stable` (e.g. on macOS)? Use a cached Playwright
  Chromium, e.g.
  `~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell`;
  it takes the same `--headless --dump-dom/--screenshot/--print-to-pdf` flags.
- Then load the built page in headless Chrome
  (`google-chrome-stable --headless --dump-dom` with a small test script that
  writes PASS/FAIL into a `data-log` attribute) and take one screenshot
  (`--screenshot`) to check it renders before handing it over.

## Scaling to new documents

This skill is document-agnostic — the five archetypes are about the *shape* of a
good exam question, not about this particular course's content. When a new
document comes in:
- Re-run the workflow above from scratch on the new material.
- Reuse archetypes 1–5, but build fresh worked examples and fresh invented
  domains (archetype 2) from the new document's actual concepts.
- If the new document has its own contrast tables / worked examples / checklists,
  prefer those as the raw material — they're usually exactly what the instructor
  intended to be tested.