# Vorarlbergerisch ("Vori") – rules as used in Schneaggchat

Vorarlberg Alemannic (Unterland/Rheintal), **not** Viennese or Bavarian: never
"ned wahr", "Oida", "geh bitte", "-erl", "is" for "ist", "net". There is no
standard spelling. The Vori files are the authority, then `references/vocab.md`
(both searched by `vori_strings.py lookup`), then these rules for words nobody
has written yet. Single words and their wrong drafts live in vocab.md, not here.

## 1. Sound shifts (stressed syllables of native words)

| Standard German | Vori | Examples |
|---|---|---|
| unstressed final **-en** (infinitive, plural, -ungen) | **-a** | löschen→löscha, Gruppen→Gruppa, Einstellungen→Einstellunga |
| prefix **ge-** | **g-**, dropped before t/p/k/b/d/g | gelesen→gleasa, gemacht→gmacht, getestet→testet, geteilt→teilt |
| stressed **e / ä** | **ea** | lesen→leasa, Feld→Feald, schnell→schneall – also in participles and conjugated forms: gseaha, geassa, mealdat |
| long **u / ie** | **ua / ia** | gut→guat, versuchen→versuacha, Liebe→Liabe, sieht→siaht |
| **ei** from old *î* | **i** / **ü** | Zeit→Zit, mein→min, schreiben→schrieba, weiter→witta, ein- prefix→i- (ilogga, igia, ilada) |
| **ei** from old *ei* | **oa / ua** | zwei→zwoa, heißt→hoast, weiß→woaß, kein→kua, einfach→uafach |
| **au** from old *û* | **u** | aus→us, auf→uf, raus→usse, rauf→uffe, runter→abe |
| **au** from old *ou* | **ou / o** | laufen→loufa, kaufen→koufa, schauen→schoua, Baum→Bom |
| **eu / äu** | **ü** | heute→hüt, Leute→Lüt, deutsch→dütsch (but freuen keeps eu: "I freu mi") |
| long **a** | **o** | Nachricht→Nochricht, Sprache→Sproch, Jahr→Joar, Frage→Frog, schlafen→schlofa |
| **an-** before a consonant | **a-** | anzeigen→azoaga, anrufen→arufa, anfangen→afanga |
| **-er** at word end | often **-a** | oder→oda, lieber→liaba, schneller→schnealla |
| 2nd person **-st** | **-sch** | bist→bisch, hast→hosch, kannst→kannsch |
| **-ig** | stays | richtig, gültig |

**Don't over-apply.** Forms you *construct* are the most common mistake – when a
word isn't in the files, prefer the plainer spelling. Known traps: bei stays bei
(only "beim" → bem); a final -n that isn't an -en ending stays (Seilbahn); the
dative plural keeps -n (mit Freunden); the noun prefix Zu- stays (Zugangsdata);
Berg, Bauch, Montag don't shift; long technical compounds keep Standard spelling
and only shift the ending (Benachrichtigunga, Datenschutzerklärung). Don't coin
compressed adverbs ("S letzte mol aktualisiert", not "Zletscht").

**But do shift inside long or formal words** (privacy policy): ussahalb,
gealtend, gnennt, ihola.

## 2. Function words

The common ones, all with their wrong forms in vocab.md: isch (ischas = ist es),
ned, nix, nümma (nicht mehr), kua/kuan, no, nomml, scho, o (auch), denn (dann),
do (hier), döt (dort), eapas, mol, vo, z (too), zruck, witta, hüt/gest/morn,
villicht, zemma, nocha, sit, glich, ins, bei/bem, mitam/ufam/usam (one word).

* **um … zu** + infinitive → **zum** + infinitive: "zum löscha", "zum Starta tippa".
* **mehr**: "mehr" after kua/no ("kua Nochrichta mehr"); "meh" for "more of" in
  game texts ("meh Punkte", "8 oda meh Zeicha").
* **a / an**: article "a"; **an** before a vowel and for masculine nouns, also
  nominative ("an Account", "isch an Stua").

### Adjective endings

After an article or possessive, **-e becomes -a** for masculine, neuter and
plural: "sin gspeicherta Fortschritt", "die fallanda Stüa", "vo da graua Felsa".
A participle ending in -a takes it on top: "d igladana User".
**Feminine singular keeps -e**: "a uafache Liste", "in die richtige Reihafolg".
**No article before a plural noun keeps -e**: "Tägliche Rätsel".
Neuter after "a" takes **-s**: "a fremds Token", "a klenns Bild".

## 3. Verbs

| | sein | haben | werden | können | wollen | müssen |
|---|---|---|---|---|---|---|
| ich | bin | hob (hobi) | – | – | – | – |
| du | bisch | hosch | – | kannsch | willsch | musch |
| er/sie/es | isch | hot | wird | kann | will | muss |
| wir/ihr/sie | sind | hond | werrand | künnand | wennd | – |
| participle | – | ket | worra / werra | künna | – | – |

"–" = not used in the files yet: form it from Vorarlberg Alemannic, list it as a
new word, prefer rephrasing around it when unsure. Infinitive of haben: **ho**.

* Infinitive **-a**; 3rd person plural and plural imperative **-and**
  (wähland, kriagand; "Ladand nur echte Spiele uffe" when a dialog speaks to
  several players). 3rd person singular after a d/t stem **-at** (mealdat,
  wartat), otherwise -t (liast).
* du-imperative = bare stem: "Druck", "Tipp", "Wähl", "Gib … i". Buttons and
  settings: bare infinitive ("Account löscha").
* Stems ending in -sch insert e: "wenn du din Account löschesch".
* Participles of nehmen end in **-no** (überno, agno); kommen after a modal or
  with a prefix → **ko** (mitko, usse ko); gehen before another infinitive →
  **ga** ("gang i ga schlofa"), at the end of a clause → **go**.
* Subjunctive: hätt, würd, wär; könntest → künntasch.
* Contractions: hob i → hobi, kenn i → kenni, müssen wir → müssama, gehen wir →
  gomma, haben wir → homma, wollen wir → wemma.
* Avoid double infinitives ("froga wella"): drop the modal.
* Passive "konnte nicht geladen werden" → "hot ned glada werra künna".

## 4. Pronouns and articles

| Standard | Vori |
|---|---|
| ich / mich / mir | i / mi / mir; unstressed dative → **ma** ("Kannsch ma … schicka?") |
| du / dich / dir | du / di / dir; unstressed "da" ("Bisch da sicher?") |
| er / ihn / ihm | er / ean / eam |
| wir / uns / unser | mir / üs / üsre |
| sie (pl) / ihnen | se / eana |
| mein, dein | min, din (fem/pl mine, dine · dat dinam, dina · before neuter: mi Handy) |
| der / die / das | da / d or die / s or des (neuter nouns: s Mitglied) |
| dem / den | am, deam / da, dean – den is **da**, never "an" (= einen) |
| dieser / diese / dieses | da / **dia** ("über dia Sitta") / des |
| einem / einer (dative) | **nam** / **na**, **nar** before a vowel ("vo nam andra Spieler", "bei na Aufsichtsbehörde") – "am" is only *dem* |
| diesen (dat pl), all diesen | deana, **allna** ("vo allna Spieler") |
| in die / in der | ind / in da |

Always informal **du**, never "Sie" (also not where the DE source uses it).

## 5. What stays Standard German / English

* Loanwords and app terms: App, Chat, Account, E-Mail (always hyphenated), Event,
  Admin, Server, Feature, Bug, Highscores, Recap, Challenge, Link, Logs, Theme,
  Markdown, Emojis, Tour, Status, Profilbild, Passwort, Freund(e), Gruppe.
* Brand/feature names: Schneaggchat, Schneaggmap, Schneagg/Schneagga, Wordle,
  Yahtzee, Tetris, Undercover, Mr. White. Programming terms (Anweisung,
  Syntaxfehler, Semikolon).
* In-game names (vehicles, items, power-ups) are localised freely
  (Milchlaster → Milchlastwaga, Free Candy Bus → Ghettobus): propose a Vori name
  and flag it as a suggestion.
* Identical to DE is often correct (Chats, Status, Event) – not untranslated by default.

## 6. Tone and register

* Casual, short, spoken; shorter than DE is normal ("Account wird glada ...").
* Humour in fun places (games, Recap, empty states, rodeo): "Abhaua" for
  "Gruppe verlassen", light teasing of the player. Never insult real groups.
* Precise where consequences matter (deleting, account, password, e-mail,
  privacy, permissions, errors, irreversible actions): keep every fact from
  EN/DE – what is deleted, for whom, whether it can be undone.
* Game instructions: keep the controls and the goal, drop vivid detail that is
  neither (rodeo: "wenn se di erwischand, isch s End vom Ritt"). No gore.

## 7. Mechanical rules

* Keep every placeholder of EN with its index (`%1$s`, `%2$d`); order may change.
* Keep XML escapes (`&amp;`, `&#127874;`), `\n` paragraph breaks where EN has
  them, and leading/trailing spaces where DE has them (strings are concatenated).
* Plain apostrophes and quotes (`Los goht's`); arrows and emoji stay in place.
