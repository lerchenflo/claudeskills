#!/usr/bin/env python3
"""Helper for the Vorarlbergerisch (values-de-rAT / strings-de-at) string resources.

Compares EN, DE and AT (= Vori) strings of the app (values*/strings.xml) or of the
server website (strings-en/-de/-de-at.xml).

Commands:
  missing                 keys present in EN but not in AT (with EN + DE text)
  show KEY [KEY ...]      EN / DE / AT side by side for the given keys
  dump [--prefix P] [--diff-only] [--same-only]
                          all triples (optionally filtered) for manual review
  lookup WORD [WORD ...]  how a word is written: vocab.md rows plus every Vori string
                          (app and website file) with a word starting with it
  check FILE.json         check a draft {"key": "value"} before inserting it: avoid
                          forms from vocab.md, Standard-German leftovers, placeholders,
                          \n / spaces, and words neither Vori file has used yet
  lint                    mechanical checks on the whole AT file (see SKILL.md)
  compare FILE.json       show where the file now differs from a draft JSON
                          (= the user's corrections after an insert)
  insert FILE.json [--replace]
                          run check, then write the draft into AT, each new key placed
                          after its nearest EN predecessor. --replace also overwrites
                          existing keys in place.

Global options:
  --res DIR   the app's composeResources dir (auto-detected otherwise)
  --i18n DIR  a flat dir with strings-en.xml / strings-de.xml / strings-de-at.xml
              instead (the website texts of the server repo, e.g.
              SchneaggchatV3server/src/main/resources/static/i18n). Auto-detected
              when no app resources are found below the cwd.
Stdlib only. Edits are textual so formatting/comments of the AT file survive.
"""
import argparse
import json
import os
import re
import sys

STRING_RE = re.compile(r'<string name="([^"]+)"[^>]*>(.*?)</string>', re.S)
PLACEHOLDER_RE = re.compile(r'%(?:\d+\$)?[sdf]')

# Standard German words that almost always mean a phrase was left untranslated.
# Matched case-insensitively as whole words.
STANDARD_GERMAN_MARKERS = [
    "nicht", "nichts", "ist", "bist", "hast", "hat", "haben",
    "auf", "aus", "zurück", "eine", "einen", "einem", "keine", "keinen", "kein",
    "deine", "deinen", "meine", "meinen", "werden", "können", "kannst", "musst",
    "willst", "möchtest", "heute", "jahr", "sprache", "nachrichten", "seite",
    "hinzufügen", "eingeben", "anzeigen", "nochmal", "erneut", "weiter", "dieser",
    "diesen", "zeit", "gehen", "suchen",
]

VOCAB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "vocab.md")
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")


def load_vocab():
    """Rows of the vocab.md table: dicts with de, vori, avoid (list), note."""
    rows = []
    with open(VOCAB_PATH, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("| ") or line.startswith("| de |") or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if len(cells) < 4:
                cells += [""] * (4 - len(cells))
            de, vori, avoid, note = cells[:4]
            rows.append({"de": de, "vori": vori, "note": note,
                         "avoid": [a.strip() for a in avoid.split(",") if a.strip()]})
    return rows


def word_re(form):
    """Whole-word match, a hyphen counts as part of the word. Only the first letter ignores
    case (sentence start), so the avoid form "eu" doesn't hit the abbreviation "EU"."""
    first = form[:1]
    head = f"[{re.escape(first.lower())}{re.escape(first.upper())}]" if first.isalpha() else re.escape(first)
    return re.compile(rf"(?<![\w-]){head}{re.escape(form[1:])}(?![\w-])")


def avoid_hits(text, vocab, skip=()):
    """(form, row) for every vocab avoid form found in text."""
    hits = []
    for row in vocab:
        for form in row["avoid"]:
            if form.lower() not in skip and word_re(form).search(text):
                hits.append((form, row))
    return hits


# Paths of the three files; set in main() for either layout.
PATHS = {}


def app_paths(res):
    return {"en": os.path.join(res, "values", "strings.xml"),
            "de": os.path.join(res, "values-de", "strings.xml"),
            "at": os.path.join(res, "values-de-rAT", "strings.xml")}


def i18n_paths(d):
    return {"en": os.path.join(d, "strings-en.xml"),
            "de": os.path.join(d, "strings-de.xml"),
            "at": os.path.join(d, "strings-de-at.xml")}


def find_i18n_dir(start):
    for root, dirs, files in os.walk(start):
        dirs[:] = [d for d in dirs if d not in (".git", "build", ".gradle", "node_modules", ".idea", "mongodb_data")]
        if "strings-de-at.xml" in files and "strings-en.xml" in files:
            return root
    return None


def find_res_dir(start):
    for root, dirs, files in os.walk(start):
        dirs[:] = [d for d in dirs if d not in (".git", "build", ".gradle", "node_modules", ".idea")]
        if os.path.basename(root) == "values-de-rAT" and "strings.xml" in files:
            return os.path.dirname(root)
    return None


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return {m.group(1): m.group(2) for m in STRING_RE.finditer(text)}


def load_all(res):
    return load(PATHS["en"]), load(PATHS["de"]), load(PATHS["at"])


def other_at_files():
    """The Vori file of the sibling repo (app <-> server), so lookups and checks see both."""
    root = os.path.dirname(os.path.abspath(PATHS["at"]))
    while root != os.path.dirname(root) and not os.path.isdir(os.path.join(root, ".git")):
        root = os.path.dirname(root)
    parent = os.path.dirname(root)
    candidates = [os.path.join("composeApp", "src", "commonMain", "composeResources", "values-de-rAT", "strings.xml"),
                  os.path.join("src", "main", "resources", "static", "i18n", "strings-de-at.xml")]
    found = []
    try:
        siblings = sorted(os.listdir(parent))
    except OSError:
        return found
    for name in siblings:
        for rel in candidates:
            path = os.path.join(parent, name, rel)
            if os.path.isfile(path) and os.path.abspath(path) != os.path.abspath(PATHS["at"]):
                found.append(path)
    return found


def vori_corpus():
    """{(file label, key): value} of every Vori string in this and the sibling repo."""
    corpus = {}
    for path in [PATHS["at"]] + other_at_files():
        label = "website" if path.endswith("strings-de-at.xml") else "app"
        for k, v in load(path).items():
            corpus[(label, k)] = v
    return corpus


def words(text):
    return {w.lower() for w in WORD_RE.findall(text)}


def triple(key, en, de, at):
    out = [f"[{key}]", f"  EN: {en.get(key, '<missing>')}", f"  DE: {de.get(key, '<missing>')}"]
    out.append(f"  AT: {at[key]}" if key in at else "  AT: <missing>")
    return "\n".join(out)


def cmd_missing(res, args):
    en, de, at = load_all(res)
    missing = [k for k in en if k not in at]
    print(f"{len(missing)} keys missing in {PATHS['at']} (EN has {len(en)}, AT has {len(at)})\n")
    for k in missing:
        print(triple(k, en, de, at))


def cmd_show(res, args):
    en, de, at = load_all(res)
    for k in args.keys:
        print(triple(k, en, de, at))


def cmd_dump(res, args):
    en, de, at = load_all(res)
    for k in en:
        if args.prefix and not k.startswith(args.prefix):
            continue
        if k not in at:
            continue
        same = at[k] == de.get(k)
        if args.diff_only and same:
            continue
        if args.same_only and not same:
            continue
        print(triple(k, en, de, at))


def placeholders(s):
    return sorted(PLACEHOLDER_RE.findall(s))


def cmd_lint(res, args):
    en, de, at = load_all(res)
    sections = {}

    def add(section, line):
        sections.setdefault(section, []).append(line)

    for k in at:
        if k not in en:
            add("Orphaned keys (not in EN - may be deleted)", k)

    marker_re = re.compile(r"\b(" + "|".join(STANDARD_GERMAN_MARKERS) + r")\b", re.I)
    for k, v in at.items():
        if k not in en:
            continue
        if placeholders(v) != placeholders(en[k]):
            add("Placeholder mismatch vs EN (extra or unknown index = crash, missing = info lost)",
                f"{k}: EN {placeholders(en[k])} AT {placeholders(v)}")
        if re.search(r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)", v) or "<" in v:
            add("Unescaped & or < (breaks the XML)", f"{k}: {v}")
        d = de.get(k, "")
        if d and (d[:1].isspace() != v[:1].isspace() or d[-1:].isspace() != v[-1:].isspace()):
            add("Leading/trailing space differs from DE (concatenated strings)", f"{k}: DE {d!r} AT {v!r}")
        if v.count("\\n") != en[k].count("\\n"):
            add("Line-break (\\n) count differs from EN (info)", f"{k}: EN {en[k].count(chr(92) + 'n')} AT {v.count(chr(92) + 'n')}")
        if v == d:
            add("Identical to DE (untranslated? fine for loanwords/names)", f"{k}: {v}")
        else:
            hits = sorted({m.group(1).lower() for m in marker_re.finditer(v)})
            if hits:
                add("Standard-German leftovers", f"{k}: {', '.join(hits)} -> {v}")
        if d and len(d) > 80 and len(v) < 0.45 * len(d):
            add("Much shorter than DE (summarised or outdated? compare meaning)",
                f"{k}: DE {len(d)} chars, AT {len(v)} chars")

    markers = {m.lower() for m in STANDARD_GERMAN_MARKERS}
    for row in load_vocab():
        for form in row["avoid"]:
            if form.lower() in markers:
                continue  # already reported as a Standard-German leftover
            keys = [k for k, v in at.items() if word_re(form).search(v)]
            if keys:
                add("Known wrong or old forms (vocab.md; older strings: fix only when asked)",
                    f"{form} -> {row['vori']} | in: {', '.join(keys)}")

    print(f"EN {len(en)} keys | DE {len(de)} | AT {len(at)} | missing in AT {len([k for k in en if k not in at])}\n")
    for title, lines in sections.items():
        print(f"## {title} ({len(lines)})")
        for line in lines:
            print(f"  - {line}")
        print()


def check_draft(draft, en, de):
    """Problems of a draft {key: value}; returns (sections dict, has_errors)."""
    vocab = load_vocab()
    corpus = vori_corpus()
    known = set()
    for v in corpus.values():
        known |= words(v)
    for row in vocab:
        known |= words(row["vori"])
    marker_re = re.compile(r"\b(" + "|".join(STANDARD_GERMAN_MARKERS) + r")\b", re.I)

    sections = {}
    errors = False

    def add(section, line):
        sections.setdefault(section, []).append(line)

    copied, coined = {}, {}
    for key, value in draft.items():
        if key not in en:
            add("ERROR key not in EN", key)
            errors = True
            continue
        value = xml_escape_value(value)
        if placeholders(value) != placeholders(en[key]):
            add("ERROR placeholder mismatch vs EN", f"{key}: EN {placeholders(en[key])} draft {placeholders(value)}")
            errors = True
        if value.count("\\n") != en[key].count("\\n"):
            add("Line-break (\\n) count differs from EN", f"{key}: EN {en[key].count(chr(92) + 'n')} draft {value.count(chr(92) + 'n')}")
        d = de.get(key, "")
        if d and (d[:1].isspace() != value[:1].isspace() or d[-1:].isspace() != value[-1:].isspace()):
            add("Leading/trailing space differs from DE (concatenated strings)", f"{key}: DE {d!r} draft {value!r}")
        flagged = set()
        for form, row in avoid_hits(value, vocab):
            add("Use the vocab form (vocab.md)", f"{key}: '{form}' -> {row['vori']}" + (f"  ({row['note']})" if row["note"] else ""))
            flagged |= words(form)
        leftovers = sorted({m.group(1).lower() for m in marker_re.finditer(value)})
        flagged |= set(leftovers)
        if leftovers and value != d:
            add("Standard-German leftovers", f"{key}: {', '.join(leftovers)}")
        if value == d:
            add("Identical to DE (fine for loanwords/names)", f"{key}: {value}")
        source_en, source_de = words(en[key]), words(d)
        for w in words(value) - known - flagged:
            if len(w) < 3 or w in source_en:
                continue  # short words, names and loanwords taken over from EN
            (copied if w in source_de else coined).setdefault(w, []).append(key)

    def hint(w):
        return "  <- Standard -en ending, -a?" if w.endswith("en") else ""

    for w, keys in sorted(copied.items()):
        add("Copied from DE, not in any Vori file (left unshifted? lookup it)", f"{w}  [{', '.join(keys)}]{hint(w)}")
    for w, keys in sorted(coined.items()):
        add("New words, not in any Vori file (formed from the rules - tell the user)", f"{w}  [{', '.join(keys)}]{hint(w)}")
    return sections, errors


def print_sections(sections):
    for title, lines in sections.items():
        print(f"## {title} ({len(lines)})")
        for line in lines:
            print(f"  - {line}")
        print()


def cmd_check(res, args):
    en, de, at = load_all(res)
    with open(args.file, encoding="utf-8") as f:
        draft = json.load(f)
    sections, errors = check_draft(draft, en, de)
    print_sections(sections)
    print(f"{len(draft)} draft strings checked" + (" - ERRORS, insert would skip those keys" if errors else ""))
    sys.exit(1 if errors else 0)


def cmd_lookup(res, args):
    vocab = load_vocab()
    corpus = vori_corpus()
    for term in args.words:
        t = term.lower()
        # From the start of a word, so a stem finds its forms ("diskut") but "auch" skips "Bauch"
        starts = re.compile(rf"(?<![\w]){re.escape(t)}", re.I)
        print(f"=== {term}")
        rows = [r for r in vocab if any(starts.search(c) for c in [r["de"], r["vori"], r["note"]] + r["avoid"])]
        for r in rows:
            avoid = f"  avoid: {', '.join(r['avoid'])}" if r["avoid"] else ""
            note = f"  ({r['note']})" if r["note"] else ""
            print(f"  vocab: {r['de']} -> {r['vori']}{avoid}{note}")
        hits = [(label, k, v) for (label, k), v in corpus.items() if starts.search(v)]
        for label, k, v in hits[:args.limit]:
            i = starts.search(v).start()
            snippet = v[max(0, i - 45):i + len(t) + 45].replace("\\n", " ").replace("\n", " ")
            print(f"  {label} {k}: …{snippet}…")
        if len(hits) > args.limit:
            print(f"  … {len(hits) - args.limit} more strings")
        if not rows and not hits:
            print("  not used yet - form it from dialect-rules.md and list it as a new word")


def cmd_compare(res, args):
    en, de, at = load_all(res)
    with open(args.file, encoding="utf-8") as f:
        proposed = json.load(f)
    changed = 0
    for key, value in proposed.items():
        current = at.get(key)
        if current is None:
            print(f"[{key}] removed by user")
            changed += 1
        elif current != xml_escape_value(value):
            print(f"[{key}]\n  PROPOSED: {xml_escape_value(value)}\n  NOW:      {current}")
            changed += 1
    print(f"\n{changed} of {len(proposed)} proposals were changed by the user")


def xml_escape_value(v):
    v = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)", "&amp;", v)
    return v.replace("<", "&lt;")


def cmd_insert(res, args):
    en, de, at = load_all(res)
    at_path = PATHS["at"]
    with open(args.file, encoding="utf-8") as f:
        new = json.load(f)
    sections, _ = check_draft(new, en, de)
    if sections:
        print("# check (fix 'Use the vocab form' / leftovers with insert --replace)\n")
        print_sections(sections)
    with open(at_path, encoding="utf-8") as f:
        text = f.read()

    en_keys = list(en)
    inserted, replaced, skipped = [], [], []
    for key, value in new.items():
        if key not in en:
            skipped.append(f"{key} (not in EN)")
            continue
        value = xml_escape_value(value)
        if placeholders(value) != placeholders(en[key]):
            skipped.append(f"{key} (placeholders {placeholders(value)} != EN {placeholders(en[key])})")
            continue
        existing = re.search(rf'<string name="{re.escape(key)}"[^>]*>.*?</string>', text, re.S)
        if existing:
            if not args.replace:
                skipped.append(f"{key} (exists, use --replace)")
                continue
            line = f'<string name="{key}">{value}</string>'
            text = text[:existing.start()] + line + text[existing.end():]
            replaced.append(key)
            continue
        line = f'    <string name="{key}">{value}</string>\n'
        anchor = None
        for prev in reversed(en_keys[:en_keys.index(key)]):
            m = re.search(rf'<string name="{re.escape(prev)}"[^>]*>.*?</string>[^\n]*\n', text, re.S)
            if m:
                anchor = m.end()
                break
        if anchor is None:
            anchor = text.index("</resources>")
        text = text[:anchor] + line + text[anchor:]
        inserted.append(key)

    with open(at_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"inserted {len(inserted)}: {', '.join(inserted)}")
    print(f"replaced {len(replaced)}: {', '.join(replaced)}")
    if skipped:
        print(f"SKIPPED {len(skipped)}:")
        for s in skipped:
            print(f"  - {s}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--res", help="composeResources directory (auto-detected from cwd)")
    p.add_argument("--i18n", help="flat dir with strings-en/-de/-de-at.xml (server website texts)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("missing")
    s = sub.add_parser("show")
    s.add_argument("keys", nargs="+")
    d = sub.add_parser("dump")
    d.add_argument("--prefix")
    d.add_argument("--diff-only", action="store_true")
    d.add_argument("--same-only", action="store_true")
    lk = sub.add_parser("lookup")
    lk.add_argument("words", nargs="+")
    lk.add_argument("--limit", type=int, default=8)
    ck = sub.add_parser("check")
    ck.add_argument("file")
    sub.add_parser("lint")
    c = sub.add_parser("compare")
    c.add_argument("file")
    i = sub.add_parser("insert")
    i.add_argument("file")
    i.add_argument("--replace", action="store_true")
    args = p.parse_args()

    res = None
    if args.i18n:
        PATHS.update(i18n_paths(args.i18n))
    else:
        res = args.res or find_res_dir(os.getcwd())
        if res:
            PATHS.update(app_paths(res))
        else:
            i18n = find_i18n_dir(os.getcwd())
            if not i18n:
                sys.exit("No values-de-rAT/strings.xml or strings-de-at.xml found below the cwd; pass --res or --i18n")
            PATHS.update(i18n_paths(i18n))
    {"missing": cmd_missing, "show": cmd_show, "dump": cmd_dump, "lookup": cmd_lookup,
     "check": cmd_check, "lint": cmd_lint, "compare": cmd_compare, "insert": cmd_insert}[args.cmd](res, args)


if __name__ == "__main__":
    main()
