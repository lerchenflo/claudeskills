#!/usr/bin/env python3
"""Helper for the Vorarlbergerisch (values-de-rAT) string resources.

Compares values/ (EN), values-de/ (DE) and values-de-rAT/ (AT = Vori) strings.xml.

Commands:
  missing                 keys present in EN but not in AT (with EN + DE text)
  show KEY [KEY ...]      EN / DE / AT side by side for the given keys
  dump [--prefix P] [--diff-only] [--same-only]
                          all triples (optionally filtered) for manual review
  lint                    mechanical checks on the AT file (see SKILL.md)
  compare FILE.json       show where the file now differs from a proposal JSON
                          (= the user's corrections after an insert)
  insert FILE.json [--replace]
                          insert approved translations {"key": "value", ...}
                          into AT, each placed after its nearest EN predecessor
                          that already exists in AT. --replace also overwrites
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

# Spelling variant groups seen in the AT file. First entry = preferred form.
VARIANT_GROUPS = [
    ["glich", "gliech"],
    ["gliche", "glieche"],
    ["glicha", "gliecha"],
    ["Nochricht", "Nachricht"],
    ["Nochrichta", "Nachrichta"],
    ["künnand", "künnan", "kümma"],
    ["nomml", "noml", "nomol"],
    ["ned", "net", "nit"],
    ["hond", "hon"],
    ["kua", "koa"],
    ["kuan", "koan"],
    ["Umfrog", "Umfrag"],
    ["zruck", "zurück"],
    ["Joar", "Jahr"],
    ["füf", "fünf"],
    ["Itrag", "Eintrag"],
    ["E-Mail", "Email"],
    ["huam", "ham"],
    ["azoaga", "anzeigen"],
    ["sealba", "sealbst"],
    ["ussahalb", "außerhalb"],
    ["gnennt", "gnannt"],
    ["gnennta", "gnannta"],
    ["Grüße", "Hoi"],
    ["uafach", "afach", "eifach", "einfach"],
    ["uafache", "einfache"],
    ["tägliche", "täglicha"],
    ["bem", "bim"],
    ["klingt", "tönt"],
    ["liaba", "lieber"],
    ["überno", "übernumma"],
    ["festghebt", "festghalta"],
    ["ufpasst", "uufpasst"],
    ["bliebt", "blibt"],
    ["ischas", "isch es"],
    ["mealdat", "mealdet", "meldet"],
    ["dinna", "drin"],
    ["bei", "bi"],
    ["Preise", "Priese"],
    ["klenn", "klua"],
    ["klenns", "kluas"],
    ["sött", "söt"],
    ["dafür", "doför"],
    ["louft", "laft", "läft"],
    ["stoht", "staht"],
    ["ago", "aganga"],
    ["hängand", "hangand"],
    ["nägschtes", "nägschts"],
    ["ussania", "usseneh", "ussaneh"],
    ["agno", "agnumma"],
    ["davo", "dävo"],
    ["ufam", "uf am"],
    ["mitam", "mit am"],
    ["liast", "läsat", "lesat"],
    ["zuasäga", "zuasaga"],
    ["gliecha", "gleicha"],
    ["zelland", "zähland", "zählend"],
]


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

    all_text = "\n".join(f"{k}\t{v}" for k, v in at.items())
    for group in VARIANT_GROUPS:
        counts = {w: len(re.findall(rf"\b{re.escape(w)}\b", all_text)) for w in group}
        if sum(1 for c in counts.values() if c) > 1:
            minority = [w for w in group[1:] if counts[w]]
            keys = sorted({k for k, v in at.items() for w in minority if re.search(rf"\b{re.escape(w)}\b", v)})
            add("Spelling variants (first = preferred)",
                f"{' / '.join(f'{w} {counts[w]}x' for w in group)} | minority in: {', '.join(keys)}")

    print(f"EN {len(en)} keys | DE {len(de)} | AT {len(at)} | missing in AT {len([k for k in en if k not in at])}\n")
    for title, lines in sections.items():
        print(f"## {title} ({len(lines)})")
        for line in lines:
            print(f"  - {line}")
        print()


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
    {"missing": cmd_missing, "show": cmd_show, "dump": cmd_dump,
     "lint": cmd_lint, "compare": cmd_compare, "insert": cmd_insert}[args.cmd](res, args)


if __name__ == "__main__":
    main()
