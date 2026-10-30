#!/usr/bin/env python3
"""Extract text from .pptx/.docx without python-pptx: read the XML inside the zip.

Usage: python3 extract_office.py COURSE_ROOT --out WORKDIR
Writes WORKDIR/text/<rel>.txt with "===== Folie N =====" markers (pptx) and lists
embedded images per slide so image-only slides can be checked visually.
"""
import argparse, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def pptx_text(path):
    z = zipfile.ZipFile(path)
    slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                    key=lambda n: int(re.findall(r"\d+", n)[-1]))
    out = []
    for n in slides:
        root = ET.fromstring(z.read(n))
        paras = []
        for p in root.iter(A + "p"):
            t = "".join(x.text or "" for x in p.iter(A + "t"))
            if t.strip():
                paras.append(t)
        rels = n.replace("slides/", "slides/_rels/") + ".rels"
        imgs = []
        if rels in z.namelist():
            imgs = re.findall(r'Target="\.\./media/([^"]+)"', z.read(rels).decode())
        notes = ""
        nn = n.replace("slides/slide", "notesSlides/notesSlide")
        if nn in z.namelist():
            nr = ET.fromstring(z.read(nn))
            notes = "\n".join("".join(x.text or "" for x in p.iter(A + "t")) for p in nr.iter(A + "p"))
            notes = "\n".join(l for l in notes.splitlines() if l.strip() and not l.strip().isdigit())
        num = re.findall(r"\d+", n)[-1]
        block = f"===== Folie {num} =====\n" + "\n".join(paras)
        if imgs:
            block += f"\n[Bilder: {', '.join(imgs)}]"
        if notes.strip():
            block += f"\n[Notizen]\n{notes}"
        out.append(block)
    return out


def docx_text(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    lines = []
    for el in body:
        if el.tag == W + "p":
            t = "".join(x.text or "" for x in el.iter(W + "t"))
            if el.iter(W + "drawing") and list(el.iter(W + "drawing")):
                t += " [Bild]"
            lines.append(t)
        elif el.tag == W + "tbl":
            for tr in el.iter(W + "tr"):
                cells = ["".join(x.text or "" for x in tc.iter(W + "t")) for tc in tr.iter(W + "tc")]
                lines.append(" | ".join(cells))
            lines.append("")
    text = "\n".join(lines)
    return [re.sub(r"\n{3,}", "\n\n", text)]


ap = argparse.ArgumentParser()
ap.add_argument("root", type=Path)
ap.add_argument("--out", type=Path, required=True)
args = ap.parse_args()
for p in sorted(args.root.rglob("*")):
    rel = p.relative_to(args.root)
    if rel.parts[0] == args.out.name or p.name.startswith(".") or p.suffix.lower() not in {".pptx", ".docx"}:
        continue
    pages = pptx_text(p) if p.suffix.lower() == ".pptx" else docx_text(p)
    dst = args.out / "text" / (str(rel) + ".txt")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(f"Quelle: {rel}\n\n" + "\n\n".join(pages) + "\n", encoding="utf-8")
    print(f"extracted {rel} ({len(pages)} {'slides' if p.suffix=='.pptx' else 'doc'}) -> {sum(len(x) for x in pages)} chars")
