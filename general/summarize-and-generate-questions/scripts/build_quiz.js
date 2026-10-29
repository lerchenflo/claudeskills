// Usage: node build_quiz.js questions.js quiz-template.html out.html
// Validates the question bank, then injects it into the template at /*__QUESTIONS__*/.
// Exits 1 with a list of problems if anything fails. Checks:
//  - exactly 4 unique options, `c` = sorted array of 1–4 unique indices in 0..3
//  - correct-count mix of the core set, calibrated on 45 real exam quiz questions
//    (≈ 62 % one correct, 24 % two, 11 % three, 2 % all four): with ≥ 20 core questions
//    at least 45 % have one correct, at most 25 % have three or four, and all four
//    correct at most once per 30 questions; with ≥ 10, every count 1, 2, 3 occurs
//  - length cue: among single-correct core questions, the correct option is the
//    longest option in at most 40 % (chance ≈ 25 %)
//  - stems: never "Welche EINE" / "genau eine" / "die einzige"; superlatives
//    ("am besten", "am ehesten", "am deutlichsten", "hauptsächlich" …) with several
//    correct options only in a slash-form stem that hides the count ("Welche Aussage/n
//    beschreibt/en …"); without a slash form they need exactly one correct option;
//    a singular stem ("Welcher …", "Welches …") must have exactly one correct option;
//    a plain plural "Welche … sind/treffen/werden …" stem must have at least two
//  - unique ids and questions
//  - explanations never reference options by letter or by position ("die letzten beiden",
//    "die erste Aussage") – options are shuffled at runtime;
//    text inside „…“ quotes and "z. B." is ignored
//  - no who/when/source questions ("Von wem stammt" …)
//  - no in-class activities/exercises in stem or explanation ("Activity 3", "Mini-Aktivität" …)
//  - optional `x: 1` marks an extended-mode question (same concept, new example); every topic
//    with extended questions must also have core questions
const fs = require('fs');
// flags: --mix  = enforce the correct-count mix (only for courses whose real exams show it, e.g. SE: 55/30/15)
//        --link = every question needs `ref` (learning page: wrong answer links to the summary section)
//  - input questions {kind:'num'|'text'|'set', a:[…], show, e, ref} skip all MC rules
const flags = process.argv.slice(2).filter(a => a.startsWith('--'));
const MIX = flags.includes('--mix'), LINK = flags.includes('--link');
const [qf, tf, out] = process.argv.slice(2).filter(a => !a.startsWith('--'));
const qs = fs.readFileSync(qf, 'utf8');
eval(qs.replace('const QUESTIONS', 'globalThis.QUESTIONS'));
const err = [];
const seen = new Set(), ids = new Set();
const strip = s => String(s).replace(/<[^>]+>/g, '');
const LETTER = /(^|[\s(„"/])[A-D](?=[\s)\/,:;=–.]|$)/;
const BAN = /von wem|wer hat|wer prägte|wer entwickelte|wer erfand|in welchem jahr|auf welcher folie|who (coined|defined|developed)/i;
const POSITION = /\b(?:die |den |der )?(?:ersten|letzten|erste|letzte|zweite|dritte|vierte|obere|untere)\s+(?:beiden|zwei|drei|Option(?:en)?|Aussage(?:n)?|Antwort(?:en)?|Paar(?:e|en)?|Einwände|Regeln|Zuordnung(?:en)?|Formulierung(?:en)?|Zeile(?:n)?)\b/i;
const SINGLE = /welche eine\b|die einzige|genau eine/i;
const SUPERLATIVE = /am (besten|ehesten|deutlichsten|unmittelbarsten|wichtigsten|stärksten)|hauptsächlich/i;
const SLASH = /\w\/(n|en|e|r|s|t)\b/;
const SINGULAR = /^(Welcher|Welches)\s/;
const PLURAL_VERB = /\b(sind|treffen|werden|gehören|beschreiben|passen|erklären|entsprechen|zählen)\b/;
QUESTIONS.forEach((x, i) => {
  const n = `#${i + 1} (id ${x.id})`;
  if (x.kind !== undefined) {
    // input question (mixed format): no MC rules, only a valid answer, solution text and section link
    if (!['num', 'text', 'set', 'venn', 'chips', 'clock', 'bits', 'grid'].includes(x.kind)) err.push(`${n}: kind must be num, text, set, venn, chips, clock, bits or grid`);
    if (x.kind === 'venn' && !(x.venn && [2, 3].includes((x.venn.names || []).length) && (x.a || []).every(c => new RegExp(`^[01]{${x.venn.names.length}}$`).test(c)))) err.push(`${n}: venn needs venn.names (2–3) and region codes like '110' in a`);
    if (x.kind === 'chips' && !(Array.isArray(x.chips) && (x.a || []).every(v => x.chips.includes(v)))) err.push(`${n}: chips: every answer in a must be one of the chips`);
    if (x.kind === 'clock' && !(x.clock && Number.isInteger(x.clock.n) && +x.a[0] >= 0 && +x.a[0] < x.clock.n)) err.push(`${n}: clock needs clock.n and an answer 0..n-1`);
    if (x.kind === 'bits' && !(Number.isInteger(x.bits) && /^[01]+$/.test(x.a[0]) && x.a[0].length === x.bits)) err.push(`${n}: bits answer must be a 0/1 string of length bits`);
    if (x.kind === 'grid' && !(x.grid && Array.isArray(x.grid.rows) && x.grid.rows.flat().filter(c => c === '?').length === (x.a || []).length)) err.push(`${n}: grid: number of '?' cells must equal a.length`);
    if (['venn', 'chips', 'grid'].includes(x.kind) && !x.show) err.push(`${n}: ${x.kind} question needs show (solution text)`);
    if (!Array.isArray(x.a) || !x.a.length) err.push(`${n}: input question needs a non-empty answer array a`);
    if (x.kind === 'num' && Array.isArray(x.a) && x.a.some(v => !/^-?[\d.,]+$/.test(String(v)))) err.push(`${n}: num answers must be plain numbers`);
    if (!x.e) err.push(`${n}: missing explanation e`);
    if (LINK && !x.ref) err.push(`${n}: missing ref (summary section) – required for the learning page`);
    if (x.id === undefined || ids.has(x.id)) err.push(`${n}: missing/duplicate id`); ids.add(x.id);
    if (seen.has(x.q)) err.push(`${n}: duplicate question`); seen.add(x.q);
    if (BAN.test(x.q)) err.push(`${n}: who/when/source question`);
    return;
  }
  if (LINK && !x.ref) err.push(`${n}: missing ref (summary section) – required for the learning page`);
  if (!Array.isArray(x.o) || x.o.length !== 4) err.push(`${n}: needs exactly 4 options`);
  else if (new Set(x.o).size !== 4) err.push(`${n}: duplicate options`);
  const c = x.c;
  if (!Array.isArray(c) || c.length < 1 || c.length > 4 || new Set(c).size !== c.length || c.some(v => !Number.isInteger(v) || v < 0 || v > 3))
    err.push(`${n}: c must be an array of 1–4 unique indices 0..3`);
  const key = x.q + (x.code || '');
  if (seen.has(key)) err.push(`${n}: duplicate question`); seen.add(key);
  if (x.id === undefined || ids.has(x.id)) err.push(`${n}: missing/duplicate id`); ids.add(x.id);
  const e = strip(x.e || '').replace(/„[^“]*“/g, '').replace(/z\. ?B\./g, '');
  // letters A–D that the stem itself uses as names (sets A, B, C …) are variables, not option references
  const named = new Set((strip(x.q + ' ' + (x.code || '') + ' ' + JSON.stringify(x.venn || '')).match(/(^|[^\p{L}])[A-D](?![\p{L}])/gu) || []).map(m => m.slice(-1)));
  const eL = named.size ? e.replace(new RegExp(`(^|[^\\p{L}])[${[...named].join('')}](?![\\p{L}])`, 'gu'), '$1·') : e;
  if (LETTER.test(eL)) err.push(`${n}: explanation references an option by letter: ${x.e.slice(0, 80)}`);
  if (POSITION.test(e)) err.push(`${n}: explanation references options by position (erste/letzte …): ${e.match(POSITION)[0]}`);
  if (BAN.test(x.q)) err.push(`${n}: who/when/source question`);
  if (/aktivität|activity|übung|mini-akt/i.test(x.q + ' ' + x.e)) err.push(`${n}: mentions an in-class activity/exercise`);
  const stem = strip(x.q).replace(/„[^“]*“/g, '');
  if (SINGLE.test(stem)) err.push(`${n}: stem demands exactly one answer: ${x.q.slice(0, 80)}`);
  if (SUPERLATIVE.test(stem) && !SLASH.test(stem) && Array.isArray(c) && c.length !== 1) err.push(`${n}: superlative stem without slash form reads as single-answer but has ${c.length} correct; use „Welche Aussage/n beschreibt/en … am besten?“: ${x.q.slice(0, 80)}`);
  if (SINGULAR.test(stem) && !SLASH.test(stem) && Array.isArray(c) && c.length !== 1) err.push(`${n}: singular stem („Welcher/Welches …“) but ${c.length} correct options`);
  if (/^Welche\s/.test(stem) && !SLASH.test(stem) && PLURAL_VERB.test(stem) && Array.isArray(c) && c.length < 2) err.push(`${n}: plural stem („Welche … sind/treffen …“) but only 1 correct option; use a slash or singular form`);
  if (x.x !== undefined && x.x !== 1 && x.x !== true) err.push(`${n}: x must be 1/true or absent`);
});
const N = QUESTIONS.length;
const core = QUESTIONS.filter(x => !x.x && x.kind === undefined);   // MC core set
const NC = core.length;
const cnt = k => core.filter(x => Array.isArray(x.c) && x.c.length === k).length;
const nC = [0, cnt(1), cnt(2), cnt(3), cnt(4)];
const pct = v => Math.round(100 * v / NC);
if (MIX && NC >= 10) [1, 2, 3].forEach(k => { if (!nC[k]) err.push(`core set has no question with ${k} correct option(s)`); });
if (MIX && NC >= 20) {
  if (nC[1] < 0.45 * NC) err.push(`too few single-answer questions in the core set (${nC[1]}/${NC} = ${pct(nC[1])} %); real exams ≈ 60 %, aim for 55 %`);
  if (nC[3] + nC[4] > 0.25 * NC) err.push(`too many three/four-correct questions in the core set (${nC[3] + nC[4]}/${NC}); real exams ≈ 13 %`);
}
if (MIX && nC[4] > Math.ceil(NC / 30)) err.push(`all-four-correct used ${nC[4]}× in the core set; at most one per 30 questions`);
const singles = core.filter(x => Array.isArray(x.c) && x.c.length === 1 && Array.isArray(x.o));
const longestRight = singles.filter(x => {
  const L = x.o.map(o => strip(o).length), mx = Math.max(...L);
  return L[x.c[0]] === mx && L.filter(l => l === mx).length === 1;
}).length;
if (singles.length >= 10 && longestRight > 0.4 * singles.length)
  err.push(`length cue: the correct option is the longest in ${longestRight}/${singles.length} single-answer questions; keep options parallel in length (≤ 40 %)`);
const coreTopics = new Set(core.map(x => x.t));
[...new Set(QUESTIONS.filter(x => x.x).map(x => x.t))].forEach(t => { if (!coreTopics.has(t)) err.push(`topic "${t}" has extended questions but no core questions`); });
if (err.length) { console.error(err.join('\n')); process.exit(1); }
const t = fs.readFileSync(tf, 'utf8');
if (!t.includes('/*__QUESTIONS__*/')) { console.error('template has no /*__QUESTIONS__*/ marker'); process.exit(1); }
fs.writeFileSync(out, t.replace('/*__QUESTIONS__*/', () => qs));
const by = {}; QUESTIONS.forEach(x => by[x.t] = (by[x.t] || 0) + 1);
const mc = QUESTIONS.filter(x => x.kind === undefined), ni = N - mc.length;
const r = mc.filter(x => (x.y || '')[0] === 'R').length, code = mc.filter(x => (x.y || '')[0] === 'C').length;
const nx = QUESTIONS.filter(x => x.x).length;
console.log('OK', N, 'questions', nx ? `(MC core ${NC}, extended ${nx})` : '', JSON.stringify(by),
  `| core correct per question: 1×${nC[1]} (${pct(nC[1])} %) 2×${nC[2]} 3×${nC[3]} 4×${nC[4]}`,
  `| recall ${r} applied ${mc.length - r - code} code/formula ${code} input ${ni}`, MIX ? '' : '(mix check off)',
  `| longest option correct in ${longestRight}/${singles.length} single-answer questions`);
