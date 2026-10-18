---
name: vori-translator
description: Translates and reviews Vorarlbergerisch ("Vori", Vorarlberg Alemannic dialect) string resources in values-de-rAT/strings.xml of a Compose Multiplatform / Android app such as Schneaggchat, and in the server's website texts (strings-de-at.xml in SchneaggchatV3server/src/main/resources/static/i18n). It fills keys that are missing compared to the English values/strings.xml, translates new or changed English/German strings into Vori, and lints the existing de-rAT file for typos, spelling drift, Standard-German leftovers, broken placeholders and translations whose meaning no longer matches EN/DE. Use this skill whenever the user mentions de-rAT, values-de-rAT, strings-de-at, server/website texts, Vori, Vorarlbergerisch, Austrian or dialect strings, "Schneaggchat translations", missing Austrian keys, or asks how something would be said in Vorarlberg dialect, even if they don't name the skill. Writes translations straight into the file for the user to review with git diff, then compares the user's hand-corrections with its draft and folds the patterns back into the skill.
---

# Vori translator (values-de-rAT + server strings-de-at)

The `values-de-rAT` locale of Schneaggchat is not Austrian Standard German. It
is **Vorarlbergerisch**, written the way people from the Rheintal text each
other. A human maintains it by hand, which is why the project's CLAUDE.md
forbids Claude to edit it on its own. This skill is the exception: the user
invoked it, so you write your translations **straight into the file**. The
user reviews them with `git diff`, fixes what is off by hand, and you learn
from those fixes (see "Learning loop"). The translator owns the voice; you are
an assistant who saves them typing.

## Files

```
composeApp/src/commonMain/composeResources/
  values/strings.xml          EN  – source of truth for which keys exist
  values-de/strings.xml       DE  – Standard German, closest source for wording
  values-de-rAT/strings.xml   AT  – Vori, the file this skill works on
```

The server repo (`SchneaggchatV3server`, a sibling of the app repo) has the
same three-way split for the website (landing page, FAQ, privacy policy,
password reset …), in one flat folder:

```
SchneaggchatV3server/src/main/resources/static/i18n/
  strings-en.xml / strings-de.xml / strings-de-at.xml
```

"Server texts" or "website texts" means this file. Its DE text addresses the
reader with formal "Sie"; the Vori version still uses "du".

Only the de-rAT / de-at file is in scope. If you notice something wrong in EN/DE/IT
(the DE file, for example, contains a leftover "Übersetzt mit DeepL.com" line in
`undercover_rules_secret_word_text`), mention it in your report and leave it alone.

## Before translating anything

1. Read `references/dialect-rules.md`: sound shifts, grammar, verbs, tone.
2. Read `references/glossary.md`: established app terms.
3. The existing file beats both references. Before using a word, grep
   `values-de-rAT/strings.xml` for it. If the translator already spelled it some
   way, reuse that spelling. A consistent spelling matters more than whichever
   spelling you think is "correct".

## Helper script

`scripts/vori_strings.py` (Python stdlib) finds the files on its own when run
from the app repo root (app strings) or the server repo root (website strings).
To be explicit, pass `--res <composeResources dir>` or `--i18n <server i18n dir>`
before the command:

| Command | Use |
|---|---|
| `python3 <skill>/scripts/vori_strings.py missing` | keys in EN but not in AT, with EN + DE text |
| `… show key1 key2` | EN / DE / AT side by side |
| `… dump --prefix games_ --diff-only` | review a feature's strings in bulk (`--same-only` = AT identical to DE) |
| `… lint` | mechanical checks (see Lint mode) |
| `… compare draft.json` | after the user edited the file: list where it now differs from your draft |
| `… insert draft.json [--replace]` | write `{"key": "value"}` pairs into AT; new keys land after their nearest EN predecessor, `--replace` overwrites existing keys in place; refuses placeholder mismatches |

Put the JSON in the session scratchpad, not the repo. Keep it until the
learning loop is done, because `compare` needs it.

## Mode A – translate missing or new strings

Use this mode when the user says "translate the missing keys", "translate the
new rodeo strings", gives a list of keys, or pastes a German/English text.

1. Collect the source strings: run `missing`, `show <keys>`, or use the text the user gave.
   With many keys, work feature by feature (by key prefix); all batches go
   into the same draft JSON.
2. Translate from **DE and EN together**. DE gives the wording. EN is the
   reference for meaning, because DE is sometimes outdated or machine-translated.
3. Apply the tone rules. Precise for anything with consequences (deleting,
   account, privacy, permissions, errors). Loose and funny for games, Recap and
   empty states. Game instructions must still name the exact controls and the goal.
4. Write the draft JSON to the scratchpad and `insert` it right away. No
   approval table, no waiting. Then run `missing` (should be 0 for the keys you
   did) and check the XML still parses.
5. Report briefly: file, branch, how many keys, and a short list of the words
   you could not find in the file and had to form from the rules (e.g.
   "*Stalagmita*"). Those are what the translator should look at first in
   `git diff`. Don't commit. Tell the user to fix things by hand and say when
   they're done.

## Learning loop (after the user's hand-fixes)

When the user says they fixed the strings, their edits are the best training
data this skill gets. Do this without being asked again:

1. Run `compare <the draft JSON you inserted>`. It lists every key the user
   changed, with your draft and their version.
2. Look for patterns, not single words: an article or dative form you got wrong
   everywhere, an ending, a shift you over- or under-applied, a word you coined
   that the translator replaced.
3. If there is something to learn, update the skill:
   - `references/dialect-rules.md`: a rule plus the real example from the diff.
   - `references/glossary.md`: single words and fixed phrases.
   - `VARIANT_GROUPS` in `scripts/vori_strings.py`: new spelling pairs
     (preferred form first), so `lint` catches the old form next time.
   If every change was a one-off (a typo, a taste choice with no rule behind
   it), say so and leave the skill alone.
4. Copy the skill to the synced folder
   `/home/flo/Nextcloud/Schneaggchat/claude_skills/vori-translator/` and
   confirm both copies are identical (`diff -r`).
5. Report the learned patterns in a short list (draft → fix).

## Mode B – lint the existing file

Use this mode when the user asks to "check", "review" or "lint" de-rAT, or to
find typos or outdated Vori strings.

1. Run `lint`. It reports:
   - **Placeholder mismatch** vs EN. An extra or unknown index crashes at
     runtime. A missing one only loses information.
   - **Unescaped `&` / `<`**, which break the XML build.
   - **Leading/trailing space** that differs from DE. These strings are
     concatenated in code, so a stray space shows up in the UI.
   - **Standard-German leftovers** (nicht, ist, hat, deine …).
   - **Spelling variants**: the preferred form is the majority form in the file.
   - **Much shorter than DE** or **missing `\n`**: possibly summarised or written
     for an older version of the feature.
   - **Identical to DE**: informational. Loanwords and names are fine as they are.
2. Read the flagged strings yourself and also skim `dump --diff-only` by prefix
   for problems the script cannot see:
   - Typos inside Vori words, such as doubled syllables ("Lebaba"), swapped
     letters ("Enrudo") or wrong letters ("kümma", "Famingo").
   - **Meaning drift**: the Vori text describes behaviour that EN/DE no longer
     describe. Example: the AT text says "daily puzzle" while EN says "random
     puzzle, as many as you want". Or a delete dialog explains a different choice
     than the current buttons offer. This is the most valuable finding, because
     users get wrong information.
   - Standard verb forms that slipped through, such as "hat" instead of "hot".
3. Report the findings grouped by severity: **breaks build or crashes** →
   **wrong or misleading information** → **typos and inconsistencies** →
   **style (optional)**. Give a concrete replacement for each finding. Do not
   "fix" deliberate jokes or creative liberties. Known ones: the Undercover rules
   texts (`undercover_rules_*_text`, short on purpose, e.g. "gang ham") – fix
   only typos there; lint's \n / length / ham warnings on them are expected. If a joke drops information
   the user needs (controls, consequences), call that out and offer to fix it.
4. After approval, apply the fixes with `insert --replace` (or the Edit tool
   for single strings).

## Orphaned keys

When a key no longer exists in EN, the project rules allow deleting it from
de-rAT without asking (`lint` lists them).

## Don'ts

- Don't rewrite strings the user didn't ask about, and don't "normalise" the
  translator's style across the file in one sweep. Propose, then let them choose.
- Don't use Bavarian or Viennese forms ("net", "Oida", "is", "-erl").
- Don't use formal "Sie". Always use "du".
- Don't run Gradle to verify. `lint` checks the XML-relevant parts.
