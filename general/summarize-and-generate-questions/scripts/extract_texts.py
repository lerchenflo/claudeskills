#!/usr/bin/env python3
"""Extract the text of every PDF (and HTML practice test) in a course folder, once.

Output: <out>/text/ mirrors the course folder, one .txt per source with
"===== Seite N =====" markers, plus <out>/INDEX.md (page counts, pages without text
= image-only slides that need a visual check, manual transcriptions). Files are only
re-extracted when the source is newer than the existing .txt, so re-run it after new
slides arrive and read the .txt files instead of parsing PDFs again.

Practice tests built from assets/quiz-template.html (a `const QUESTIONS` bank) are
written as a readable list: question, options with [x] = correct, explanation (needs
Node.js). Photos of quiz sheets have no text layer: transcribe them once by hand into
a .md file under <out>/text/ (INDEX.md lists those too).

Requires poppler (`brew install poppler` / `apt install poppler-utils`).

Usage:
  python3 extract_texts.py [COURSE_ROOT] [--out DIR] [--skip FOLDER ...] [--force]
COURSE_ROOT defaults to the folder two levels above this script when it lives in
<root>/06_Claude/tools/, else the current directory. --out defaults to
COURSE_ROOT/06_Claude.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

LOW_TEXT_CHARS = 40  # pages with fewer characters are flagged as image-only

NODE_DUMP = r"""
const src = require('fs').readFileSync(0, 'utf8');
const m = src.match(/const QUESTIONS\s*=\s*\[[\s\S]*?\n\];/);
eval(m[0].replace('const QUESTIONS', 'globalThis.QUESTIONS'));
console.log(JSON.stringify(QUESTIONS));
"""


def default_root():
    here = Path(__file__).resolve()
    if here.parent.name == "tools" and here.parents[1].name == "06_Claude":
        return here.parents[2]
    return Path.cwd()


def sources(root, skip):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or path.name.startswith(".") or any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts[0] in skip:
            continue
        if path.suffix.lower() in {".pdf", ".html"}:
            yield path


def pdf_pages(path):
    result = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                            capture_output=True, text=True, check=True)
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def question_bank(raw):
    """Practice tests built from the quiz template: list questions, options and answers."""
    if "const QUESTIONS" not in raw or not shutil.which("node"):
        return None
    result = subprocess.run(["node", "-e", NODE_DUMP], input=raw, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s))
    out = []
    for n, q in enumerate(json.loads(result.stdout), 1):
        extended = " · erweitert" if q.get("x") else ""
        out.append(f"### Frage {n} · {q['t']} · Typ {q['y']}{extended}\n{strip(q['q'])}")
        if q.get("code"):
            out.append(q["code"])
        for i, option in enumerate(q["o"]):
            out.append(f"- [{'x' if i in q['c'] else ' '}] {strip(option)}")
        out.append(f"Erklärung: {strip(q['e'])}\n")
    return ["\n".join(out)]


def html_pages(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    bank = question_bank(raw)
    if bank:
        return bank
    raw = re.sub(r"(?is)<(style|svg)\b.*?</\1>", "", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr)>", "\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", "", raw))
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return [text.strip()]


def clean(page):
    text = "\n".join(line.rstrip() for line in page.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--skip", action="append", default=[], help="top-level folder to ignore")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    root = (args.root or default_root()).resolve()
    out_dir = (args.out or root / "06_Claude").resolve()
    text_dir = out_dir / "text"
    skip = set(args.skip) | {"06_Claude"}
    if out_dir.is_relative_to(root):
        skip.add(out_dir.relative_to(root).parts[0])

    rows = []
    for src in sources(root, skip):
        rel = src.relative_to(root)
        dst = text_dir / rel.with_suffix(rel.suffix + ".txt")
        pages = pdf_pages(src) if src.suffix.lower() == ".pdf" else html_pages(src)
        pages = [clean(p) for p in pages]
        low = [i + 1 for i, p in enumerate(pages) if len(p) < LOW_TEXT_CHARS]
        if args.force or not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            dst.parent.mkdir(parents=True, exist_ok=True)
            body = [f"Quelle: {rel}\nSeiten: {len(pages)}\n"]
            body += [f"===== Seite {i} =====\n{page}\n" for i, page in enumerate(pages, 1)]
            dst.write_text("\n".join(body), encoding="utf-8")
            print(f"extracted  {rel}  ({len(pages)} pages)")
        rows.append((rel, dst.relative_to(out_dir), len(pages), low))

    lines = ["# Text-Index", "",
             "Automatisch erzeugt von `extract_texts.py`. Bildlastige Seiten (kaum Text) sind "
             "markiert und sollten bei Bedarf visuell geprüft werden.", "",
             "| Quelle | Text | Seiten | Seiten ohne Text |", "|---|---|---|---|"]
    for rel, txt, n, low in rows:
        lines.append(f"| {rel} | {txt} | {n} | {', '.join(map(str, low)) if low else '-'} |")
    manual = sorted(text_dir.rglob("*.md")) if text_dir.exists() else []
    if manual:
        lines += ["", "## Manuelle Transkriptionen und Analysen", ""]
        lines += [f"- {m.relative_to(out_dir)}" for m in manual]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} files indexed → {out_dir}")


if __name__ == "__main__":
    main()
