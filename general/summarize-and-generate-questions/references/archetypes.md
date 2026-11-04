# Question archetypes, calibration and set mix

## Recall quiz vs. this workflow

A quick self-check ("quiz me on this chapter") can use plain "select all that
apply" recall questions – faster to write. Use the full archetype workflow
when the user asks for harder / more exam-like / applied questions, pastes
real exam questions and wants more like them, says recall felt too easy, or
prepares for an exam that tests understanding (lecturers who give
"Abgrenzungen" / "distinguish X from Y" tables or worked examples usually do).

## What the real exams look like (calibration)

> **Status (29.10.2026):** these numbers come from the SE course's
> **micro-quizzes**, which are over. That course now has real exams: read them
> and re-calibrate before the next SE set. Any other course: calibrate on its
> own exams/sample questions; use these numbers only as a fallback and say so.

45 real quiz questions (FH Vorarlberg „Projektbasierter Einstieg ins Software
Engineering“ plus an earlier run of the lecturer's HCI quizzes; list with keys
in `<course>/06_Claude/text/05_Quizes/ALLE_Quizfragen_Analyse.md`):

- **Format:** sheets of 5 questions, one per newest deck, each on the deck's
  **central message** (JTBD: the product is only one possible solution; HTML:
  structure and meaning; Product Vision: which block names the competitor).
  Little slide trivia.
- **Correct count:** 62 % one, 24 % two, 11 % three, 2 % all four (a persona
  dimensions list where every option was a real dimension).
- **Stems:** slash forms („Welche Aussage/n entspricht/en …“), superlatives in
  slash forms (2–3 correct), short direct questions („Was sind …?“, „Was
  bedeutet …?“), reverse definitions („Welches Prinzip beantwortet die Frage
  „Wie denke ich, dass es funktioniert?“?“), cause/effect („Was passiert mit
  der Reaktionszeit, wenn …?“), rationale („Warum betonen X, dass …?“). Names
  and years only as context („Nach George Olsen (2004) …“).
- **Options:** short, parallel, often one term; distractors come from
  neighbouring decks (the HTML question offers CSS and JavaScript duties).
- **Types:** ≈ 60 % recall, 40 % applied; ≈ 10 % read code or a formula (a CSS
  rule, one JavaScript line, a code handout, Fitts' law with renamed
  variables).

**Real exams or quizzes in the folder: re-calibrate.** Read them (or their
extract) first, tabulate correct-count mix, stem forms, option length and
archetypes, and follow them where they differ from these defaults. Say in the
reply what you calibrated on.

## Two families

**Recall** asks "what does the source say?" – fast to write, good for first
memorization. **Applied** asks "can you use it?" – predicts exam performance
because pattern-matching text fails. Every question maps to one archetype
(`y:'R2'` …). Vary the angle: never one pattern 20 times.

## Recall archetypes

All four options must be plausible things that *could* be on the slide; an
off-topic or absurd distractor tests nothing.

**R1. List membership.** 4 items; usually 1–3 belong to a taught list or
category (all four only as the Hard rules allow). Distractors are real terms
from an *adjacent* category of the same model or chapter, not made up.
> Which of the following is a subcharacteristic of [X] in [model]? → [term from
> a neighbouring category] ✗ · [term from X's list] ✔ · [another neighbouring
> category] ✗ · [neighbouring term from the chapter] ✗

**R2. Single-fact definition.** One correct definition; three each swap in one
specific wrong detail (another concept's definition, a plausible unsupported
claim, a too narrow/broad version).
*Reverse variant (common in real exams):* give the definition, guiding
question or quote, ask for the term – „Welches Prinzip beantwortet die Frage
„Wie denke ich, dass es funktioniert?“?“ → Visibility. ✗ / Conceptual/Mental
Model. ✔ / Feedback. ✗ / Constraints. ✗ (bare terms from the same list).

**R3. Sequence / order.** For a taught process, cycle or pyramid: the order,
or "what comes after step N". Distractors: real steps in the wrong order, or
one step swapped for one from another taught sequence.

**R4. Count / quantity.** "How many X" for a list with a taught count ("8
quality characteristics", "5 Norman principles"). Distractors: equally
plausible off-by-a-few numbers.

**R5. Term ↔ purpose.** Match a term to its purpose, phase/artefact or the
problem it solves („Wofür wird ein Storyboard eingesetzt?“, „Welches Artefakt
entsteht in Phase X?“). Distractors: the purpose/phase of another real term
from the document. Never pair terms with authors, years or slide numbers.
*Complete-mapping variant:* for a trio/quartet (Mistake / Slip / Lapse; Product
Owner / Scrum Master / Developers) each option maps *all* terms; only the fully
correct mapping counts. A fourth option can be a true meta statement („Alle
drei Begriffe werden unter dem Begriff Error zusammengefasst.“), making it 1-
or 2-correct. Stem: „Welche Option/en treffen gesamt korrekte Aussagen über …?“

**R6. Rationale and effect („warum“ / „was passiert, wenn“).** Correct = the
reasons/effects the source gives; distractors = plausible unstated reasons,
reversed effects, wrong growth shapes.
> Warum betonen Greenberg et al., dass Skizzen „von Hand, nicht mit einem
> Zeichenprogramm“ erstellt werden sollen? → zu genaue digitale Zeichnungen
> bremsen die Ideenfindung ✔ · Handskizzen fördern viele schnelle Ideen ✔ ·
> Skizzen sollen ausgedruckt werden ✗ · Software erzwingt visuelle Hierarchie ✗
>
> Was passiert laut Hick-Hyman-Gesetz mit der Reaktionszeit, wenn die Zahl
> gleich wahrscheinlicher Alternativen steigt? → sinkt linear ✗ · steigt
> logarithmisch ✔ · bleibt konstant ✗ · steigt exponentiell ✗

## Applied archetypes

Test the concept's *boundary* with new wording, examples or framing – the
harder, more exam-realistic half.

**A1. Near-duplicate discrimination.** 3–4 superficially similar phrasings
(same topic, structure, length); only one meets the definition, each wrong one
violates it in a different plausible way. Needs a definition with a clear
boundary ("task-centric, not tool-centric").
> Which formulation best satisfies [concept]? (task-centric user story) →
> "I want to enter a CD title into a search box and start the search." ✗ names
> the UI mechanism · "I want to click the search button after entering search
> terms." ✗ also UI · "I, as a hurried shopper, want to find a specific CD in
> the store." ✔ goal only · "I want to refresh the search results." ✗ a
> sub-action, not the goal

**A2. Novel application.** Apply a concept taught with the slide's example to
an example that **never appears in the source** – the highest-value archetype,
because recognizing text does not help. Needs a category/classification
concept (User Objects, stakeholder vs. user, mental vs. system model).
**Invent the new domain yourself**, distinct from every example in the source
(record store in the slides → shop, fitness app, library).
> Which is most likely a User Object in an online shop? → Warenkorb ✔
> user-facing noun · Product Repository ✗ data layer · Order Service ✗
> architecture · API-Endpunkt ✗ implementation detail

**A3. Statement truth-checking.** 3–4 short statements on one concept; the
correct one(s) exactly supported, each wrong one false in a *different* common
way. Needs a definition or a property list. Ways to falsify a true statement:
- drop a qualifier ("incomplete, possibly contradictory" → "always complete and
  consistent"),
- universalize what varies per person ("identical across all users"),
- narrow a multi-part definition to one part ("exclusively the structure"),
- swap in a related concept's property,
- invert cause/effect or a comparison (usability vs. UX, Gulf of Execution vs.
  Evaluation).

**A4. Contextual decision.** A small scenario or design decision; which of
several real, source-backed facts is most decisive for it. All options are
true – the test is relevance. Needs a checklist or attribute set (persona
attributes, task analysis questions, prototype dimensions).
> Which persona attribute matters most when deciding on a step-by-step
> tutorial? → Psychographics ✗ · Biographic Background ✗ · Specific
> Knowledge/Proficiency ✔ · Product's Relationship to the Persona ✗ (all real,
> only one decisive)

**A5. Definitional contrast.** For a pair the source contrasts (course
"Abgrenzungen" tables are a goldmine): which statement *most* distinguishes X
from Y – not any true fact about X.
> Storyboard vs. UI sketch collection → shows the screen sequence ✗ (true only
> for sequential storyboards, not the separator) · serves mainly visual design
> ✗ · represents how a design is used to reach a user goal within a scenario ✔
> · made earlier in the process ✗ (not the distinguishing property)

**A6. Scenario explanation („warum passiert das?“).** A concrete situation
with an observable effect; which statements *explain* it with taught
concepts. Correct options apply different contributing concepts (often 2–3);
wrong ones misapply, invert or absolutize („Nur Farbe allein garantiert
Sichtbarkeit.“). A4 asks which fact *decides* a choice; A6 which concepts
*explain* an outcome.
> Banking-App: Sicherheitswarnung fett über dem „Login“-Button, oben ein
> animiertes Werbebanner. Warum übersehen Benutzer die Warnung? → Aufmerksamkeit
> auf den Login-Button (Ziel) fokussiert ✔ · Bewegung im Banner zieht
> Aufmerksamkeit an ✔ · Warnung außerhalb des Locus of Attention ✔ · Nur Farbe
> garantiert Sichtbarkeit ✗

**C1. Read code or apply a formula** (counts as applied, `y:'C1'`). Snippet in
`code` (a CSS rule, one or two JavaScript lines, a tiny HTML block) or a
formula with renamed variables; ask what a part does, what the user sees, or
which statements are true. Distractors: swapped roles (selector vs. property,
event type vs. handler), claimed immediate execution, an existing property that
does something else, swapped numerator/denominator. Use it whenever the source
teaches code or formulas (real exams: ≈ 1 in 10).
> `.container {display: grid; grid-template-columns: 1fr 1fr; gap: 10px;}` –
> welche Eigenschaft macht beide Spalten gleich breit? → display: grid. ✗ ·
> gap: 10px. ✗ · grid-template-columns: 1fr 1fr. ✔ · container. ✗
>
> `button.addEventListener("click", handleSearch);` → "click" ist der Event
> Type ✔ · button ist die Event Source ✔ · handleSearch ist der Event Handler ✔
> · addEventListener führt handleSearch sofort aus ✗

## Material-to-archetype map

- Bulleted items under one category → R1; with an explicit boundary/qualifier
  also A1/A3
- Single named definitions → R2; terms with a purpose/phase/artefact → R5
- Numbered steps, cycles, pyramids → R3; lists with a stated count → R4
- Classification concepts with a worked example → A2
- Property/characteristic lists → A3
- Checklists, multi-attribute concepts (personas, task analysis, prototype
  types) → A4
- Contrast tables ("Abgrenzung", "Unterschied", "vs.", "don't confuse X with
  Y") → A5
- Recommendations with a reason ("so that …", "because …"), laws/models with a
  direction of effect → R6
- Concepts that explain observable behaviour (attention, errors, feedback,
  breakdowns, burndown shapes) → A6
- Code snippets, syntax anatomy, formulas → C1

## Building a mixed set

- **Default:** ≈ 55 % recall (R1–R6), 45 % applied (A1–A6, C1) – near the
  real 60/40 with extra practice on the harder half; ≈ 10 % C1 if the source
  teaches code or formulas.
- **Central messages first:** give every deck's core claim (title slide,
  learning objectives, summary/merksatz slide) at least two questions from
  different archetypes, then fill in details.
- "Harder" / "more like these examples": ≈ 70–80 % applied. "Just quiz me" /
  fast first pass: ≈ 70–80 % recall.
- Rotate archetypes within each family (20 questions ≈ 2 each of R1–R6 minus
  one, 1–2 each of A1–A6, plus 1–2 C1 with code/formulas).
- Use what the source supports; don't force A5 without contrasts or R3
  without sequences. Leaning toward the archetypes the material fits is fine.

## New documents

The archetypes describe the *shape* of a good question, not one course. For a
new document, re-run the workflow, build fresh worked examples and invented
domains from its concepts, and prefer its own contrast tables, worked
examples and checklists as raw material – they are usually what the lecturer
intends to test.
