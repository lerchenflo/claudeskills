---
name: vori-translator
description: Translates and reviews Vorarlbergerisch ("Vori", Vorarlberg Alemannic dialect) string resources in values-de-rAT/strings.xml of a Compose Multiplatform / Android app such as Schneaggchat, and in the server's website texts (strings-de-at.xml in SchneaggchatV3server/src/main/resources/static/i18n). It fills keys that are missing compared to the English values/strings.xml, translates new or changed English/German strings into Vori, and lints the existing de-rAT file for typos, spelling drift, Standard-German leftovers, broken placeholders and translations whose meaning no longer matches EN/DE. Use this skill whenever the user mentions de-rAT, values-de-rAT, strings-de-at, server/website texts, Vori, Vorarlbergerisch, Austrian or dialect strings, "Schneaggchat translations", missing Austrian keys, or asks how something would be said in Vorarlberg dialect, even if they don't name the skill. Writes translations straight into the file for the user to review with git diff, then compares the user's hand-corrections with its draft and folds the patterns back into the skill.
---

# Vori translator (values-de-rAT + website strings-de-at)

The `values-de-rAT` locale of Schneaggchat is **Vorarlbergerisch**, written the
way people from the Rheintal text each other – not Austrian Standard German. A
human maintains it by hand, so the project's CLAUDE.md forbids Claude to edit
it on its own. This skill is the exception: the user invoked it, so you write
your translations **straight into the file**, the user fixes them by hand, and
you learn from the fixes. The translator owns the voice.

## Files

| | App (`composeApp/src/commonMain/composeResources/`) | Website (`SchneaggchatV3server/src/main/resources/static/i18n/`) |
|---|---|---|
| EN – which keys exist | `values/strings.xml` | `strings-en.xml` |
| DE – wording | `values-de/strings.xml` | `strings-de.xml` (formal "Sie" – Vori still uses "du") |
| AT – Vori, in scope | `values-de-rAT/strings.xml` | `strings-de-at.xml` |

Only the AT file is in scope. Mention problems you notice in EN/DE, don't fix them.

Knowledge, in priority order: the two Vori files → `references/vocab.md`
(settled words with the forms to avoid) → `references/dialect-rules.md`
(how to form words nobody has written yet, grammar, tone).

## Script

`python3 <skill>/scripts/vori_strings.py <command>` – stdlib only. Run it from
the app repo root (app strings) or the server repo root (website strings), or
pass `--res <composeResources>` / `--i18n <i18n dir>`. `lookup` and `check`
also read the Vori file of the sibling repo.

| Command | Use |
|---|---|
| `missing` | keys in EN but not in AT, with EN + DE text |
| `show k1 k2` | EN / DE / AT side by side |
| `dump --prefix games_ [--diff-only/--same-only]` | review a feature in bulk |
| `lookup wort …` | vocab rows + every Vori string with a word starting with it (a stem like `diskut` finds all forms) |
| `check draft.json` | vocab avoid forms, Standard-German leftovers, placeholders, `\n`, spaces, and words no Vori file has used yet |
| `insert draft.json [--replace]` | runs `check`, then writes into AT after the nearest EN predecessor; refuses placeholder mismatches |
| `compare draft.json` | after the user's hand-fixes: where the file now differs from your draft |
| `lint` | whole-file review, see Mode B |

Keep the draft JSON in the session scratchpad until the learning loop is done.

## Mode A – translate missing or new strings

1. Read `references/dialect-rules.md` (once per session). Don't read vocab.md
   top to bottom – `lookup` searches it.
2. Collect sources: `missing`, `show <keys>`, or the text the user gave. With
   many keys work by key prefix; all batches go into one draft JSON.
3. Translate from **DE and EN together** (DE for wording, EN for meaning – DE is
   sometimes outdated or machine-translated). `lookup` every content word you
   haven't seen spelled in this session; reuse the file's spelling even if you
   think another is "correct". Tone: precise where consequences matter, loose
   in games/Recap/empty states; game instructions keep controls and goal.
4. Run `check draft.json` and work through every section:
   - **Use the vocab form** and **Standard-German leftovers**: fix them.
   - **Copied from DE, not in any Vori file**: a word you probably forgot to
     shift. Apply the rules or keep it on purpose (loanword, technical term).
   - **New words**: fine if formed by the rules – they go into your report.
   Repeat until only intended items remain, then `insert`.
5. Run `missing` (0 for your keys), then report briefly: file, branch, number
   of keys, and the **New words** list from `check`, which the translator
   should look at first in `git diff`. Don't commit. Ask the user to fix things
   by hand and say when they're done.

## Learning loop (after the user's hand-fixes)

When the user says they fixed the strings, do this without being asked again:

1. `compare <draft JSON>` lists every key they changed.
2. Each changed word → one row in `references/vocab.md` with your draft form in
   **avoid** (and note "draft X → fixed"), so `check` and `lint` catch it next
   time. If the vocab already had the word, your step 3 missed a `lookup`: say so.
3. A pattern behind several changes (an ending, an article, a shift you over- or
   under-applied) → one short rule plus the example in `dialect-rules.md`.
4. One-offs with no rule (typo, taste) → leave the skill alone and say so.
5. Report the learned patterns as a short list (draft → fix).

## Mode B – lint the existing file

1. Run `lint`. It reports placeholder mismatches vs EN (extra index = crash),
   unescaped `&`/`<` (breaks the build), leading/trailing spaces that differ
   from DE, Standard-German leftovers, **known wrong or old forms** from
   vocab.md, strings much shorter than DE or with a different `\n` count, and
   strings identical to DE (informational).
2. Read the flagged strings and skim `dump --diff-only` by prefix for what the
   script can't see: typos inside Vori words ("Lebaba", "Enrudo"), Standard verb
   forms ("hat" for "hot"), and above all **meaning drift** – the Vori text
   describes behaviour EN/DE no longer describe (users get wrong information).
3. Report by severity: breaks build/crashes → wrong or misleading information →
   typos and inconsistencies → style (optional), each with a concrete
   replacement. Deliberate jokes stay: the Undercover rules texts
   (`undercover_rules_*_text`, e.g. "gang ham") get typo fixes only – their
   lint warnings are expected. Older strings flagged as "old forms" are fixed
   only when the user asks. Call out a joke only if it drops information.
4. After approval apply the fixes with `insert --replace` (or Edit for single
   strings). Keys no longer in EN may be deleted from AT without asking.

## Don'ts

- Don't rewrite strings nobody asked about or normalise the translator's style
  in one sweep – propose, let them choose.
- No Bavarian/Viennese forms ("net", "Oida", "is", "-erl"), no formal "Sie".
- Don't run Gradle to verify; `check` and `lint` cover the XML-relevant parts.
