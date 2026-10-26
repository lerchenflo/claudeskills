# Schneaggchat Vori vocabulary

One row per word or phrase the translator has settled. Don't read it top to
bottom: `vori_strings.py lookup WORD` searches it together with both Vori files,
and `check` / `insert` / `lint` flag every **avoid** form automatically.

Columns: **de** = Standard German meaning · **vori** = the form to write ·
**avoid** = comma-separated forms that are wrong in new Vori text (Standard
spellings, wrong dialect variants, earlier drafts the translator fixed) ·
**note** = usage or the draft → fix it came from. When a Vori file disagrees
with a row, the file wins (it gets edited by hand): fix the row.

To add a word (learning loop): one row, the rejected draft form in **avoid**.

| de | vori | avoid | note |
|---|---|---|---|
| abbrechen | abbreacha | abbrechen | |
| aktivieren / deaktivieren | aktiviera / deaktiviera | aktivieren, deaktivieren | |
| akzeptieren / ablehnen | akzeptiera / ablehna | akzeptieren, ablehnen | |
| ändern | ändra | ändern | |
| anrufen | arufa | anrufen | |
| anzeigen / zeigen | azoaga / zoaga | anzeigen | |
| auswählen | uswähla | auswählen | |
| bearbeiten | bearbeita | bearbeiten | |
| beitreten | beitreata | beitreten | |
| entfernen | entferna | entfernen | |
| erstellen | erstella | erstellen | |
| hinzufügen / hinzugefügt / du fügst hinzu | dazuatua / dazuato / dazuatuasch | hinzufügen, hinzufüga | hinzufüga still in older strings - don't sweep; participle "I hob … dazuato" |
| herunterladen / hochladen | abalada / uffelada | herunterladen, hochladen | |
| kopieren | kopiera | kopieren | |
| löschen | löscha | löschen | du-form löschesch, not löschsch |
| öffnen / aufmachen | öffna / uftua | öffnen | |
| schließen | schlüßa | schließen | |
| senden / schicken / gesendet | senda / schicka / gsendet, gschickt | | |
| speichern | speichra | speichern | |
| starten / stoppen | starta / stoppa | | |
| suchen / finden | suacha / finda | suchen, finden | |
| teilen | teila (also toala) | teilen | |
| verlassen | verlo | verlassen | |
| verwenden | verwenda | verwenden | |
| zurücksetzen | zrucksetza | zurücksetzen | |
| erneut versuchen | Nomml versuacha | erneut | |
| weiter / fortsetzen | witta / wittamacha | weiter | |
| zurück | zruck | zurück | |
| einloggen / ausloggen | ilogga / uslogga | einloggen, ausloggen | |
| einladen / eingeladen | ilada / iglada (d igladana User) | einladen | |
| eingeben | igia | eingeben | |
| tippen / drücken / wischen / halten | tippa / drucka / wüscha / heba | drücken, wischen | |
| springen / hüpfen | jucka (springa also used) | | |
| schauen / anschauen | luaga, schoua / aluaga, aschoua | | |
| Nachricht / Nachrichten | Nochricht / Nochrichta | Nachricht, Nachrichten, Nachrichta | |
| Sprachnachrichten | Sprochnochrichta | Sprachnachrichten | |
| Einstellungen | Einstellunga | Einstellungen | |
| Benachrichtigungen | Benachrichtigunga | Benachrichtigungen | |
| Umfrage / Umfragen / Unterumfrage | Umfrog / Umfroga / Unterumfrog | Umfrage, Umfragen, Umfrag | |
| Frage / Anfrage / Freundschaftsanfrage | Frog / Afrog / Freundschaftsanfrog | Frage, Anfrage, Freundschaftsanfrage | |
| Antworten | Antworta (Antwort stays) | Antworten | |
| Optionen | Optiona (Option stays) | Optionen | |
| Gruppe / Gruppen | Gruppe (also Gruppa) / Gruppa | Gruppen | |
| Name / Nutzername | Nama / Benutzernama | | |
| Sprache | Sproch | Sprache | |
| Jahr | Joar | Jahr | |
| Tag / Tage | Tag / Täg | | |
| Woche / Stunde | Wocha / Stund | Woche, Stunde | |
| Zeit / Zeitstempel | Zit / Zitstempel | Zeit, Zeitstempel | |
| Seite | Sitta | Seite | |
| Karte (map) | Karta (also Map) | Karte | |
| Spieler | Spieler / Spiela (both used) | | |
| Leben (lives) | Leba | | |
| Bestenliste | Highscores | Bestenliste | |
| Zeichen | Zeicha | Zeichen | |
| Feld | Feald | Feld | |
| Haus / nach Hause | Hus / huam | ham | "gang ham" in the Undercover rules is on purpose |
| Schnecken | Schneagga | Schnecken | |
| Werkzeuge | Werkzüg | Werkzeuge | |
| Geld | Geald | Geld | |
| Daten | Data (Benutzerdata, Standortdata) | | "Daten" in some compounds |
| Medien | Media | Medien | |
| Eintrag / Einträge | Itrag / Iträg | Eintrag, Einträge | everywhere, also "Neuer Itrag" |
| Karteneintrag | Kartaitrag | Kartenitrag, Karteneintrag | draft Kartenitrag → fixed; compound joint follows the Vori word Karta, older Kartenanzeige / Kartenänderunga stay as they are |
| Ausgabe | Usgab | Usgob | only aus→us |
| Anweisung, Syntaxfehler, Compiler (code) | Anweisung, Syntaxfehler, Compiler | Awisung | programming terms stay Standard |
| Mitglied | s Mitglied | da Mitglied | neuter article s |
| Preis / Preise | Preis / Preise | Priese | |
| Token (a foreign token) | a fremds Token | an fremda | neuter after a takes -s |
| Versuch / Versuche | Versuach / Versuche / Versuache | | sg "bem erschta Versuach"; after a number "3 Versuche"; after kua "Kua Versuache mehr!" |
| E-Mail (also compounds) | E-Mail | Email | Bestätigungs-E-Mail, E-Mail-Verifizierung |
| Fische (die) | da Fisch | d Fisch | "Fang da Fisch mitam Lasso!" |
| Wagen / Laster | Waga (Milchlastwaga, Ikoufswäga) | | |
| Seilbahn | Seilbahn | Seilbah | final -n of a non -en word stays |
| Zugang / Zugangsdaten | Zugang / Zugangsdata | Zuagangsdata | noun prefix Zu- stays |
| Gewinner | Gewinner / Gwinner | | |
| Berg / Bauch / Montag | Berg / Bauch / Montag | Bearg, Mäntig | don't over-shift; Samstag → Samstig |
| Wetter | Weatta | Wetter | |
| Wochenende | Wochenende | | |
| Abend / heute Abend | Obad / hüt zobad | | zobad is one word |
| heute / morgen | hüt / morn | heute | |
| gestern | gest | geschter, gester, gestern | "Gest um 18:00 gseaha" |
| Januar | Jänner | Januar | |
| Stein | Stua | | masculine: "isch an Stua" |
| Mädchen / Junge | Schmelle / Buab | | |
| Brötchen / Kartoffeln | Brötle / Grumpara | | |
| Freunde (casual story) | Kollega | | |
| Freund / Freunde | Freund / Freunde | | loanword-like, stays |
| mit / bei Freunden | mit / bei Freunden | mit Freunde, bei Freunde | dative plural keeps -n (website draft fixed) |
| Bruder | Brüadar | | |
| Urlaub | Urloub | Urlaub | |
| Handy (mein) | mi Handy | min Handy | possessive before a neuter noun |
| Deutsch | Dütsch | Deutsch | |
| Vorarlbergerisch | Vori (language picker label: "S einzig wahre") | | |
| Systemsprache | Handysproch | Systemsprache | |
| ist / ist es | isch / ischas, ischs | isch es | "dussa ischas iskalt" |
| nicht | ned | net, nit | |
| nichts | nix | | |
| nicht mehr | nümma | ned meh, ned mehr | "Du bisch nümma in da Gruppe" |
| kein / keine | kuan (masc. acc.) / kua | koa, koan | |
| ein (number) | uan (masc) / ua (fem) | | "mindestens ua Zahl" |
| noch / noch keine | no / no kua | | |
| nochmal / erneut / wieder | nomml | noml, nomol, nochmal | |
| schon | scho | schon | |
| auch | o | ou, auch | "Des goht o offline" (test answer 2026-10-26) |
| immer | immer | allat, allad | stays Standard |
| dann | denn | | |
| jetzt | jetzt (casual: jz) | | |
| nach (preposition) | noch (nocham = nach dem) | | "1 Tag nocham Event" |
| geben / gibt es | gia / git, gits | | "Es git scho an Account" |
| ein (neuter article) | a (also as) | | "a Event", "was as Programm usgit" - either is fine, don't sweep |
| hier | do | hier | "Do tippa zum starta", "Do kannsch du …" |
| dort | döt | dött, dort | single t |
| vielleicht | villicht | vilicht, vielleicht | "Villicht morn." |
| ein bisschen | a bitzle | a bitz, bissle, bisschen | |
| etwas / etwas anderes | eapas / eapas andres | etwas | |
| anders (adverb) | andersch | | |
| mal / jedes Mal | mol / jedes mol, amol | | |
| zu (too) | z | | "z lang" |
| dass es | dassas | | |
| sogar | sogär | | |
| zusammen | zemma; zemm before "ga + verb" | zusammen | "zemm ga wandra go" |
| nachher | nocha | Nochher | |
| danach | danoch | | |
| gegen (time) | gegs | | "gegs Mittag" |
| seit | sit | | "dabei sit %1$s", "sit na Stund" |
| zuletzt | s letzte mol / letztes mol | Zletscht | "S letzte mol aktualisiert", "letztes mol online" |
| gerade jetzt | aktuell | | |
| weil / wie | weil / wie | wil | question word "wie" doesn't shift |
| gleich wie | glich wia | | |
| gleich (same) / dasselbe | glich / gliche / glicha | gliech, glieche, gliecha, gleicha | "für alle s glich", "mit da glicha Farb" |
| ins | ins | is | |
| mit dem / auf dem / aus dem / nach dem | mitam / ufam / usam / nocham | mit am, uf am | always one word |
| bei / beim | bei / bem | bi, bim | |
| von / davon | vo / davo | dävo | |
| drin | dinna | drin | |
| dafür | dafür | doför | |
| was | was | wa | |
| wohin / woher | wo ane / woher | Wohi, wohär | |
| euch | euch | eu | |
| selbst | sealba / sealbsch | sealbst, selbst | |
| außerhalb | ussahalb | außerhalb | |
| genannt | gnennt / gnennta | gnannt, gnannta | "die oba gnennta Dienstleister" |
| geltend | gealtend | geltend | |
| einholen | ihola | einholen | |
| sich vorbehalten | bheba … vor | | "Mir bheband üs vor" |
| behält / behalten | bhebt / bheba | behaltet | |
| einfach / einfache | uafach / uafache | afach, eifach, einfach, einfache | |
| tägliche (before a plural noun) | tägliche | täglicha | "Tägliche Rätsel", "Tägliche Challenge" |
| nächstes / als nächstes | nägschtes / als nägschtes | nägschts | |
| klein | klenn / klenns | klua, kluas | cf. Klennbuchstab |
| lieber | liaba | lieber | |
| höher | höher / höhera | höchera | |
| neblig | neablig | | |
| fünf / sieben / acht | füf / siemne / achte | fünf | "um acht" → "am achte" |
| klingen / klingt | klinga / klingt | tönt | |
| sagen / sag! | säga / säg | sag | |
| zusagen / zugesagt | zuasäga / zuasägt | zuasaga | |
| lesen / liest | leasa / liast | läsat, lesat | |
| gesehen | gseaha | gseha, gesehen | ea of seaha also in the participle |
| gegessen | geassa | gessa | |
| gewandert | gwandert | gwandrat | |
| übernommen / angenommen | überno / agno | übernumma, agnumma | participles of nehmen end in -no |
| herausnehmen | ussania | usseneh, ussaneh | |
| festgehalten | festghebt | festghalta | |
| aufgepasst | ufpasst | uufpasst | |
| bleibt | bliebt | blibt | |
| läuft / steht | louft / stoht | laft, läft, staht | |
| angehen | ago | aganga | |
| hängen (sie) | hängand | hangand | |
| zählen / sie zählen | zella / zelland | zähland, zählend | |
| meldet / wartet / arbeitet / redet | mealdat / wartat / arbeitat / redat | mealdet, meldet | -at only after d/t stems |
| sollte | sött | söt | |
| könnte (du) | künntasch | künntisch | |
| können (sie, pl) | künnand | künnan, kümma | |
| werden (sie, pl) | werrand | werand | |
| haben (sie, pl) / haben wir | hond / homma | hon, hond mir | |
| kann (er/sie) | kann | ka | |
| mitkommen | mitko | mitkumma | "dass er ned mitko kann" |
| kommen / gekommen | kumma, kut / ko | kumma isch | "bevor da Film usse ko isch" |
| gehen / gehen wir | go, goht / gomma | | before another infinitive: ga ("gang i ga schlofa") |
| schlafen gehen | ga schlofa | go schlofa | |
| wollen wir … ? | Wemma … ? | Wennd mir | |
| dürfen | darf | Dörf | |
| freuen | freu | | "I freu mi" |
| verschieben | verschiaba | verschieben | |
| anziehen | azüha | | |
| weinen | blägga | | |
| melken | mealka | | |
| schneien | schneia | | |
| pitschnass | pflätschnass | | |
| hervorheben | fürraheba | hervorheben | |
| Verstecken (game) | Verstecki | | |
| Fahrrad | Fahrrad | Velo | |
| der beste … der Welt | … uf da Welt | | |
| danke vielmals / sehr nett | danke vielmols / voll nett vo dir | | |
| ja / nein / ok | jo (button "yes" = mol) / na / passt | | |
| hallo (greeting) | Grüße / Zeawas | Hoi | |
| Bist du sicher? | Bisch da sicher? | | |
| Willst du … ? | Magsch … ? / Willsch du … ? | | |
| Es funktioniert nicht | Es tuat ned | | |
| … konnte nicht geladen werden | … hot ned glada werra künna | | |
| Prüfe deine Internetverbindung und versuche es erneut. | Prüf dine Internetverbindung und versuachs nomml. | | |
| Dies kann nicht rückgängig gemacht werden. | Des kann ned rückgängig gmacht werra. | | |
| Tippen, um fortzufahren | Tipp zum wittamacha | | |
| Lass uns zurück zu den Einstellungen gehen | Gomma zruck zu da Einstellunga | | |
| Erfolgreich … | (usually dropped: "Usgloggt") | | |
| Keine Ahnung | Keine Ahnung (stand-alone reply) / kua Ahnung (inside a sentence) | | |
| Heißluftballon / Schneagg-Rakete | Heißluftballo / Rakete (button: Raketa) | | on purpose, don't fix |
