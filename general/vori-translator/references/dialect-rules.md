# Vorarlbergerisch ("Vori") – rules as used in Schneaggchat

Derived from the ~935 hand-translated strings in `values-de-rAT/strings.xml`.
This is Vorarlberg Alemannic (Unterland/Rheintal flavour), **not** Viennese or
Bavarian Austrian – never use "ned wahr", "Oida", "geh bitte", "-erl" diminutives,
"is" for "ist" or similar east-Austrian forms.

There is no standard spelling. The file is the authority: if a word already
appears in values-de-rAT, copy that spelling (grep first). These rules are for
words the file has not used yet.

## Contents
1. Sound shifts (how to respell a German word)
2. Grammar and function words
3. Verbs
4. Pronouns and articles
5. What stays Standard German / English
6. Tone and register
7. Mechanical rules (XML, placeholders)

---

## 1. Sound shifts

| Standard German | Vori | Examples from the file |
|---|---|---|
| unstressed final **-en** (infinitive, plural, -ungen) | **-a** | suchen→suacha, löschen→löscha, Einstellungen→Einstellunga, Gruppen→Gruppa, Optionen→Optiona, Minuten→Minuta |
| prefix **ge-** | **g-** (dropped before t/p/k/b/d/g) | gelesen→gleasa, geladen→glada, gemacht→gmacht, geschickt→gschickt · getestet→testet, geplant→plant, geteilt→teilt |
| stressed short/long **e / ä** | **ea** | lesen→leasa, sehen→seaha, Feld→Feald, Geld→Geald, melden→mealda, schnell→schneall, Weg→Weag, essen→eassa, rechnen→reachna |
| **u / ie** (long, old diphthong) | **ua / ia** | suchen→suacha, gut→guat, versuchen→versuacha, tun→tua, kriegen→kriaga, Liebe→Liabe, sieht→siaht, hinzu→dazua |
| **ei** from old long *î* | **i** (closed) / **ü** | Zeit→Zit, Eintrag→**Itrag** (everywhere, also "Neuer Itrag", "Itrag löscha"), mein/dein→min/din, ein- (prefix)→i- (einloggen→ilogga, eingeben→igia, einladen→ilada), schreiben→schrieba, bleiben→blieba, weiter→witta, Seite→Sitta, reiten→ritta, seit→sit, wischen→wüscha |
| **ei** from old *ei* | **oa / ua** | zwei→zwoa, heißt→hoast, weiß→woaß, teilen→toala (also teila), ein (number)→uan/ua, kein→kua/kuan, einfach→**uafach** (not "afach"/"einfach": draft "Gnüß afach da Ritt!" → fixed "Gnüß uafach da Ritt!"; adjective: "a uafache Liste"), fünf→**füf** (translator chose füf over fünf, 2026-10-04) |
| **au** from old *û* | **u** | aus→us, auf→uf, Haus→Hus, raus→usse, rauf→uffe, runter→abe |
| **au** from old *ou* | **ou / o** | laufen→loufa/lofa (glofa), kaufen→koufa (verkoft), schauen→schoua, Baum→Bom |
| **eu / äu** | **ü** | heute→hüt, Leute→Lüt, deutsch→dütsch, Kreuz→Krütz |
| long **a** | **o** | Nachricht→Nochricht, Sprache→Sproch, Jahr→Joar, Frage→Frog, Umfrage→Umfrog, Anfrage→Afrog, Straße→Stroß, schlafen→schlofa, lassen→lo/losa |
| **an-** prefix before consonant | **a-** | anzeigen→azoaga, anrufen→arufa, annehmen→ania, anfangen→afanga, anschauen→aschoua |
| **-er** at word end (Spieler etc.) | often **-a** | Spieler→Spiela (both used), oder→oda, über→überm/drüba, schneller→schnealla |
| **-st** 2nd person singular | **-sch** | bist→bisch, hast→hosch, kannst→kannsch, musst→musch, willst→willsch, magst→magsch |
| **-ig** | stays | richtig, gültig |

**Don't over-apply the shifts.** Several Standard forms are what the
translator actually writes: **bei** (not bi; only the
contraction **"bem"** = beim/bei dem: draft "dia bim langa Drucka" → kept "dia bem langa Drucka"), **höher/höhera** (not höchera), **Gewinner**
(also "Gwinner"). Rounded or reduced forms you *construct* are the most
common mistake, so when a word isn't in the file, prefer the plainer spelling.
Don't drop a final -n that isn't an -en ending: Seilbahn stays Seilbahn (not
"Seilbah"). Exceptions the translator chose on purpose (don't "fix" them):
rodeo "Heißluftballo", and the rocket button "Raketa" next to the vehicle
name "Rakete". The noun prefix **Zu-** stays: Zugang → Zugangsdata (not
"Zuagangsdata"). Don't coin compressed adverbs: "zuletzt aktualisiert" is
"S letzte mol aktualisiert", not "Zletscht".

**But do apply the shifts inside long or formal words too.** The translator
shifted these in the privacy policy, where the draft had left them Standard:
außerhalb → **ussahalb**, geltend → **gealtend**, genannt → **gnennt**
("die oba gnennta Dienstleister"), einholen → **ihola** (single l).

The shifts apply to stressed syllables of native words. Long compounds and
technical words often keep Standard spelling (Verifizierung, Benachrichtigung
→ Benachrichtigunga, only the ending shifts).

## 2. Grammar and function words

| Standard | Vori | Note |
|---|---|---|
| ist | isch | "ischas" / "ischs" = ist es / ist das ("dussa **ischas** iskalt", "Trotzdem **ischs** uana vo …") – don't write "isch es" |
| nicht | ned | never "net" / "nit" |
| nichts | nix | |
| kein / keine | **kuan** (masc. acc) / **kua** (fem, neut, plural) | kuan Status, kuan Ort · kua Beschreibung, kua Events |
| ein / eine (article) | **a**; **an** before vowels and for masculine nouns (nom. too) | a Event, a Frog · an Account, an Moment, "isch **an** Stua" (draft "a Stua" → fixed) |
| ein (number "one") | uan (masc) / ua (fem) | mindestens ua Zahl, uan Klennbuchstab |
| noch | no | |
| nochmal / erneut / wieder | nomml | "Nomml versuacha" |
| schon | scho | |
| auch | o (also "ou") | |
| dann | denn | |
| hier | do | |
| etwas | eapas / was | |
| jetzt | jetzt (casual: jz) | |
| mal | mol | "jedes mol", "amol" |
| nach (prep) | noch (nocham = nach dem) | "1 Tag nocham Event" |
| von | vo (vom, vo da) | "von" occurs but "vo" preferred |
| zu (too) | z | "z lang", "z viele" |
| um … zu + inf | **zum** + inf | "zum löscha", "zum Starta tippa" |
| dass es | dassas | |
| zurück | zruck | zrucksetza |
| weiter | witta | wittamacha |
| heute / gestern / morgen | hüt / gest / morn | |
| Woche / Stunde / Tage | Wocha / Stund / Täg | |
| Januar | Jänner | |
| ja / nein / ok | jo (button "yes" = **mol**) / na / passt | |
| hallo (greeting) | **Grüße** / **Zeawas** | never "Hoi" (Swiss/other): draft "Hoi %1$s!" → fixed to "Grüße %1$s!" |
| hinzufügen | **dazuatua** (preferred; hinzufüga still in older strings – don't sweep them) | draft "a eigene Reaktion hinzufüga" → fixed "… dazuatua" |
| herunterladen / hochladen | abalada / uffelada | |
| zeigen | zoaga (azoaga) | |
| geben / gibt es | gia / git, gits | "Es git scho an Account" |
| kommen | kumma (kummsch, kut); participle **ko** | "bevor da Film usse **ko** isch", "d Sunna isch **ussa ko**" (not "kumma isch") |
| gehen / geht | go / goht | "Los goht's", "Gomma" = gehen wir. Before another infinitive ("gehen + verb") the particle is **ga**: "denn gang i ga schlofa", "zemm ga wandra go" (not "go schlofa") |
| gehen at the end of a clause | **go** | "würd i öfter in d Berg **go**" (draft "ga" → fixed; **ga** only right before another infinitive) |
| haben wir | **homma** | "Doba uf da Hütta **homma** Käsknöpfle … geassa" (draft "hond mir") |
| wohin / woher | **wo ane** / woher | "**Wo ane** gosch du hüt zobad no?" (draft "Wohi"); woher stays (draft "wohär" → fixed) |
| dürfen / euch | **darf** / **euch** | "Darf i mi zu euch hocka?" (drafts "Dörf", "eu") |
| gegen (time) | **gegs** | "gegs Mittag" |
| nachher | **nocha** | "Nocha gomma no an Kaffee trinka" (draft "Nochher") |
| seit einer | sit **na** | "sit na Stund" (draft "sit ra" – the existing rule *einer → na* applies) |
| sogar | sogär | |
| wollen wir … ? | **Wemma** … ? | "Wemma am Wochenende zemm ga wandra go?" (draft "Wennd mir … zemma go wandra" → fixed) |
| zusammen | zemma; **zemm** before "ga + verb" | "zemm ga wandra go" |
| weil / wie | **weil** / **wie** (no shift) for the question word ("Wie goht's da?"); comparison "gleich wie" → **glich wia** (confirmed) | drafts "wil", "wia" → fixed |
| drin / darin | **dinna** | chat draft "isch jetzt o drin" → fixed "… dinna" |
| mehr | **mehr** after kua/no ("kua Nochrichta mehr", "No mehr Daten"); **meh** for "more of" in game texts ("meh Punkte") | draft "kua Nochrichta meh" → fixed "… mehr" |
| ins | **ins**, never "is" | "Wer zersch ins Ziel kut", "ins Vori-File" (chat draft "is Vori-File" → fixed) |
| halten | heba | "Ruhig heba" |
| springen / hüpfen | jucka (springa also used) | |
| wischen | wüscha | |
| drücken | drucka | |
| schauen / anschauen | luaga / schoua / aluaga | |
| aufmachen / öffnen | uftua / öffna | |
| Spieler | Spieler / Spiela | |

### Adjective endings

After an article or possessive, the adjective ending **-e becomes -a**:
"sin gspeicherta Fortschritt", "zu volla Reiha", "die fallanda Stüa",
"vo da graua Felsa". The bare ending "-e" ("gspeicherte") reads as Standard German.
A participle that already ends in -a takes the ending on top: iglada →
"d **igladana** User" (not "d iglada User").

**Exception: feminine singular keeps -e**, after "a" and after "die" alike:
"a **uafache** Liste", "in die **richtige** Reihafolg" (C-Challenge draft
"in die richtiga Reihafolg" → fixed). The -a ending is for masculine, neuter
and plural ("s schlüßenda Anführungszeicha", "die fallanda Stüa").

**Without an article the plural keeps -e**: "nur **klenne** Sprüng" (rodeo draft
"nur klenna Sprüng" → fixed). The -a only comes after an article or possessive.

## 3. Verbs

Infinitive ends in **-a** (macha, löscha, starta). Present tense:

| | sein | haben | werden | können | wollen | müssen |
|---|---|---|---|---|---|---|
| ich | bin | hob (hobi) | – | – | – | – |
| du | bisch | hosch | – | kannsch | willsch | musch |
| er/sie/es | isch | hot | wird | **kann** (prefer over ka) | will | muss |
| wir/ihr/sie | sind | hond | werrand | künnand | wennd | – |
| Partizip | – | ket | worra / werra | künna | – | – |

"–" = not yet used in the file. Fill these from your own knowledge of
Vorarlberg Alemannic, mark them as new in the review table, and prefer
rephrasing around them when unsure.

* Infinitive of haben is **ho**: "s Mindestalter erreicht ho".
* kommen after a modal / with separable prefix → **ko**: "dass er ned **mitko kann**" (draft "mitkumma ka" → fixed).
* The e→ea shift also hits participles: gegessen → **geassa** (not "gessa").
* Subjunctive: hätt, würd, wär (all kept); könntest → **künntasch** (draft "künntisch").
* **Don't over-shift these** (all corrected back by the translator): Berg (not
  "Bearg"), Bauch (not "Buch"), Montag (not "Mäntig"), neblig → **neablig**
  (this one does shift), gewandert → **gwandert** (not "gwandrat"),
  Ausgabe → **Usgab** (only aus→us; not "Usgob").
* Programming terms stay Standard German: Anweisung (not "Awisung"), Syntaxfehler,
  Semikolon, Compiler, Array-Index (C-Challenge draft "Awisung" → fixed).
* -er at word end → -a also in adverbs/nouns: lieber → **liaba** (also in "lieber nehmen": chat draft "lieber" → fixed), Bruder → **Brüadar**.
* Participles of nehmen / halten / passen: übernommen → **überno** (not "übernumma"), festgehalten → **festghebt** (heba = halten; not "festghalta"), aufgepasst → **ufpasst** (single u, like uf; not "uufpasst").
* The e→ea shift also hits conjugated forms, and the 3rd person singular ending after a d/t stem is **-at**: meldet → **mealdat** (chat drafts "meldet", "mealdet" → fixed). Same for other verbs: wartat, arbeitat, redat (confirmed by the translator).
* Preis/Preise stays **Preise** (not "Priese"; chat draft fixed).
* Neuter noun after "a" takes adjective **-s**: "a **fremds** Push-Token" (Token is neuter; chat draft "an fremda Push-Token" → fixed).
* was (interrogative) → **was**, never "wa" ("Mit was willsch witta macha?"; chat draft "Mit wa" → fixed).
* dafür stays **dafür** (not "doför"; chat draft fixed).
* läuft → **louft** (like loufa), steht → **stoht** (like goht); chat drafts "laft", "staht" → fixed.
* zusagen → **zuasäga**, zugesagt → **zuasägt** (chat draft "zuasaga" → fixed).
  Plain sagen → **säga**, imperative **säg** ("säg vorus, was …"; draft "sag" → fixed).
* gleich (same) / dasselbe → **glich / gliche / glicha**, as everywhere in the app
  file: "für alle s glich", "mit da glicha Farb", "s gliche igia" (C-Challenge
  draft "s gliech" → fixed). The earlier chat-exercise form "vom gliecha Stall"
  is the exception, not the rule – write **glich** in app texts.
* Neuter indefinite article: the file mostly writes **a** ("a Event", "a neus
  C-Rätsel"), but the translator used Alemannic **as** in "was **as** Programm
  usgit" (draft "a Programm"). Either is fine; don't sweep.
* Neuter nouns take **s**, also Mitglied: "**s** neue Mitglied" (chat draft "da neue Mitglied" → fixed).
* liest → **liast** (infinitive stays leasa; chat draft "läsat" → fixed). The -at ending is only for d/t stems.
* angehen → **ago** (like go = gehen; chat draft "aganga" → fixed).
* "auf dem"/"mit dem" are always written together: **ufam**, **mitam** (chat drafts "Uf am", "mit am" slipped through more than once).
* davon → **davo** (vo = von; chat draft "dävo" → fixed).
* angenommen → **agno** (like überno; chat draft "agnumma" → fixed). Participles of nehmen end in **-no**, never "-numma".
* hängen (an etwas) → **hängand** (plural), keeps the umlaut (chat draft "hangand" → fixed).
* nehmen in compounds → **-nia** (like ania = annehmen): herausnehmen → **ussania** (chat draft "usseneh" → fixed).
* "als nächstes" → **als nägschtes** (glossary has nägschtes; chat draft "nägschts" → fixed).
* klein → **klenn** ("a klenns Bild", cf. Klennbuchstab), never "klua/kluas" (chat draft fixed).
* sollte → **sött** ("Die App sött … zoaga"), not "söt".
* hinzugefügt (participle, "I hob … dazuato") → **dazuato**; the infinitive and button stay **dazuatua** ("Bild dazuatua"), du-form **dazuatuasch** (all confirmed 2026-10-10; chat draft "hob … dazuatua" → fixed).
* bleibt → **bliebt** (like blieba; not "blibt").
* Chat drafts still slipped on rules already listed, several times: "Bi"/"bi" → **Bei/bei** (bei stays, never bi), "isch es" → **ischas**. Check sections 1–2 before every reply.
* klingen → **klinga / klingt**, never Swiss "tönt" (chat draft "so tönt" → fixed "so klingt").
* anders: adverb → **andersch**; "etwas anderes" (adjective, neuter) → "eapas ganz **andres**" (chat draft "ganz andersch" → fixed).
* Adjective after article keeps the -e/-a pattern: "in **großa** Kanna";
  nominalised colour after "die" stays -e: "die **rote** oder die blau".
* Time: "um acht" → "**am achte**"; numbers: siebne → **siemne**, füfe, achte.
* "Keine Ahnung" as a stand-alone chat reply stays Standard ("Keine Ahnung, i
  bin no im Gschäft"); inside a sentence it's "kua Ahnung".
* eu stays eu in freuen: "I **freu** mi" (draft "frei"); Urlaub → **Urloub**.
* Possessive before neuter noun: "**mi** Handy" (draft "min Handy").
* Avoid double infinitives like "froga wella" (wollte fragen): the translator just drops the modal → "I hob di nur kurz froga, ob …".
* 2nd person singular of stems ending in -sch inserts an **e**: löschen →
  "wenn du din Account **löschesch**" (not "löschsch").
* 3rd person plural of regular verbs ends in **-and** (confirmed: zelland – zählen is **zella**, so not "zählend"/"zähland"): wähland, seahand,
  wartand, rutschand, kriagand. (künnand, werrand – not künnan/kümma/werand.)
* Passive "konnte nicht geladen werden" → "hot ned glada werra künna".
* Imperative (du): stem only – "Druck", "Tipp", "Wähl", "Gib … i", "Änder".
* When a dialog speaks to **several players** (party games, upload dialogs), use
  the plural imperative in **-and** (same as the plural verb): "Ladand nur echte
  Spiele uffe", "schrieband ma uafach", "Kummand doch ine" (translator switched
  the app's old "-at" to "-and", 2026-10-04). Use the bare
  stem only when addressing one person.
* behalten → bhebt (heba = halten), not "behaltet". sich vorbehalten →
  "Mir **bheband** üs vor".
* selbst → **sealba** ("die du sealba wählsch") or **sealbsch** ("jederzit
  sealbsch löscha"), not "sealbst".
* Contractions: hob i → hobi, kenn i → kenni, müssen wir → müssama,
  gehen wir → gomma, schauen wir uns → schouama üs.
* Settings/Buttons usually use the bare infinitive: "Account löscha",
  "Passwort ändra", "Bild entferna".

## 4. Pronouns and articles

| Standard | Vori |
|---|---|
| ich / mich / mir | i / mi / mir; unstressed dative mir → **ma** ("Kannsch **ma** bitte s Foto … schicka?") |
| du / dich / dir | du / di / dir (unstressed "da": "Bisch da sicher?", "Wie goht's **da**?") |
| er / ihn / ihm | er / ean / eam |
| wir / uns / unser | mir / üs / üsre |
| sie (pl) / ihnen | se / eana |
| mein, dein | min, din (fem/pl: mine, dine · dat: dinam, dina) |
| der / die / das (article) | da (masc) / d or die (fem) / s or des (neut) |
| dem / den | am, deam / da, dean |
| dieser / diese / dieses (dem, den, der) | da / dia / des (deam, dean, derra) |
| mit dem / auf dem / aus dem | mitam / ufam / usam |
| einem (dat, masc/neut) | nam ("vo nam andra Spieler", "uf nam Mac", "vo nam Erziehungsberechtigta", "bei nam Wort" – chat draft "bei am Wort" → fixed; **am** is only *dem*) |
| einer (dat, fem) | **na**, **nar** before a vowel ("an na gmeinsam gpflegta Karta", "bei na Aufsichtsbehörde", "vo nar Einwilligung") – not "nam" |
| die (plural article, e.g. the fish) | **da** for Fisch: draft "Fang d Fisch mitam Lasso!" → fixed "Fang da Fisch mitam Lasso!" |
| den (masc acc article) | **da** ("Mir nehmand da Schutz … ernst") – never "an", which means *einen* |
| diesen (dat pl) | deana; "all diesen" → **allna** ("vo allna Spieler", not "vo all deana Spieler") |
| diese (= this, e.g. this page) | **dia** ("über dia Sitta löscha") – plain "die" reads as the article |
| in die / in der | ind / in da |

Always informal **du**. Never "Sie" (the DE file has formal "Sie" in some
Undercover texts – do not carry it over).

## 5. What stays Standard German / English

* Loanwords and app terms stay as they are: App, Chat, Account, **E-Mail** (always with hyphen, also in compounds: Bestätigungs-E-Mail, E-Mail-Verifizierung – never "Email"/"email"), Event,
  Admin, Server, Feature, Bug, Highscores, Recap, Challenge, Link, Logs, Theme,
  Markdown, Emojis, Tour, Status, Profilbild, Passwort, Freund(e), Gruppe.
* In-game names (vehicles, items, power-ups) are **not** fixed: the translator
  localises them freely, e.g. Milchlaster → Milchlastwaga, Free Candy Bus →
  Ghettobus, Schneagg-Rakete → Rakete. Propose a Vori name rather than copying
  the German one, and flag it as a suggestion.
* Brand/feature names: Schneaggchat, Schneaggmap, Schneagg/Schneagga (snail –
  already Vori), Wordle, Yahtzee, Tetris, Undercover, Mr. White.
* Long technical compounds keep Standard spelling and only shift the ending:
  "Benachrichtigungsberechtigunga", "Datenschutzerklärung".
* Many short strings are legitimately identical to DE (Chats, Profilbild,
  Status, Event, E-Mail …). Identical ≠ untranslated by default.

## 6. Tone and register

* Casual, short, spoken. Shorter than DE is normal: "Account wird glada ..."
  instead of "Accountdaten werden geladen ...".
* Humour is welcome in fun places (games, Recap, empty states, rodeo popups):
  "Du Bimbo hosch koa Spiel igstelt", "Gruppenchatting. Immenser Terror.",
  "Abhaua" for "Gruppe verlassen".
* Stay precise where a user must understand consequences: deleting data,
  account/password/email, privacy, permissions, error messages, irreversible
  actions. Keep every fact from EN/DE there (what gets deleted, for whom,
  whether it can be undone). Humour or shortening is fine only if no
  information is lost.
* Game instructions: keep the controls (which key / tap / swipe does what)
  and the goal; flavour can be dialect-heavy. Leave out vivid detail that is
  neither control nor goal. In the rodeo instructions, for example, the
  translator cut the hat/arm/leg pecking sequence down to "wenn se di
  erwischand, isch s End vom Ritt". Gore and long descriptive chains don't
  belong in the Vori version.
* Never insult real groups; light teasing of the player is the house style.

## 7. Mechanical rules

* Keep every placeholder from EN with the same index: `%1$s`, `%2$d` … Order
  may change, a placeholder may not disappear or be invented.
* Keep XML escapes: `&amp;`, `&#127874;` emoji entities, `\n` line breaks
  (keep paragraph breaks where EN has them).
* Keep leading/trailing spaces when DE has them – those strings are glued
  together in code (e.g. `accept_agb_pt1` + `accept_agb_pt2`).
* Apostrophes and quotes as plain characters (`Los goht's`, `"%1$s"`).
* Unicode arrows/emoji (← → ✓ ❌ ✔ 👆) stay exactly where they are.
