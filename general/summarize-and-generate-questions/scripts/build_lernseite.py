#!/usr/bin/env python3
"""Build a learning page: summary (from its print source) + connected quiz in ONE self-contained HTML file.

Usage:
  python3 build_lernseite.py --summary Zusammenfassung.html --questions questions.js \
      --template lernseite-template.html --out Kurs_Lernseite.html \
      --title "Kursname" --sub "WS 26/27" --key kurs-lernseite-v1

The summary HTML stays the single source (also used for the print PDF). Headings h2/h3 that start
with a number ("2.3 …") get ids s-2-3 – a question's `ref:'2.3'` links there. Exercise solutions
(<div class="a">) and theory answers (<div class="tq-a">) are wrapped in <details> („Lösung zeigen“).
"""
import argparse
import re
import sys
from pathlib import Path


def scope_css(css: str) -> str:
    """Prefix every rule of the summary CSS with .doc so it cannot clash with the quiz styles."""
    out = []
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        sel = sel.strip()
        if sel.startswith('@page') or not sel:
            continue
        parts = []
        for s in sel.split(','):
            s = s.strip()
            if s == 'body':
                parts.append('.doc')
            elif s == '*':
                parts.append('.doc, .doc *')
            else:
                parts.append('.doc ' + s)
        body = body.replace('break-before: page;', '')
        out.append(f"{', '.join(parts)} {{{body}}}")
    return '\n'.join(out)


def add_heading_ids(html: str) -> str:
    """Give h2/h3 (and the theory-question h4) ids s-1, s-1-4, … for the TOC and quiz links."""
    counter = {'n': 0}

    def text_of(inner):
        t = re.sub(r'<span class="src">.*?</span>', '', inner)
        t = re.sub(r'<span style="font-weight:400[^"]*">.*?</span>', '', t)
        return re.sub(r'<[^>]+>', '', t).strip()

    def h(m):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if 'data-toc=' in attrs:
            return m.group(0)
        title = text_of(inner)
        own = re.search(r'\s*id="([^"]+)"', attrs)
        if tag == 'h4' and 'Theoriefragen' not in title and not own:
            return m.group(0)
        num = re.match(r'^(\d+(?:\.\d+)?)\b', title)
        if own:
            # id set in the summary source (target of in-text links): keep it, only add the TOC entry
            hid = own.group(1)
            attrs = attrs.replace(own.group(0), '')
        elif num and tag in ('h2', 'h3'):
            hid = 's-' + num.group(1).replace('.', '-')
        else:
            counter['n'] += 1
            hid = f's-x{counter["n"]}'
        toc = title.replace('"', '&quot;')
        return f'<{tag}{attrs} id="{hid}" data-toc="{toc}">{inner}</{tag}>'

    return re.sub(r'<(h[234])([^>]*)>(.*?)</\1>', h, html, flags=re.S)


NOTE = ('<textarea class="note" placeholder="Eigene Lösung / Notizen (optional – wird nur in diesem Browser gespeichert)">'
        '</textarea>')
SUMMARY = '<details class="sol"><summary><span class="s-show">Lösung zeigen</span><span class="s-hide">Lösung verbergen</span></summary>'


def wrap_divs(html: str, opening: str) -> str:
    """Put every <div class="…"> block that starts with `opening` into a <details> (works without JavaScript)."""
    out, pos = [], 0
    while True:
        i = html.find(opening, pos)
        if i < 0:
            break
        depth, j = 0, i
        while True:
            o, c = html.find('<div', j), html.find('</div>', j)
            if o != -1 and o < c:
                depth += 1
                j = o + 4
            else:
                depth -= 1
                j = c + 6
                if depth == 0:
                    break
        out.append(html[pos:i] + NOTE + SUMMARY + html[i:j] + '</details>')
        pos = j
    out.append(html[pos:])
    return ''.join(out)


def make_interactive(html: str) -> str:
    n = {'a': 0, 't': 0}

    def aufg(m):
        n['a'] += 1
        return f'<div class="aufg" data-rid="a{n["a"]}">'

    def tq(m):
        n['t'] += 1
        return f'<div class="tq" data-rid="t{n["t"]}">'

    html = re.sub(r'<div class="aufg">', aufg, html)
    html = re.sub(r'<div class="tq">', tq, html)
    html = wrap_divs(html, '<div class="a">')
    html = wrap_divs(html, '<div class="tq-a">')
    return html


def build_toc(html: str) -> str:
    items = re.findall(r'<h([234])[^>]* id="(s-[^"]+)" data-toc="([^"]*)"', html)
    return ''.join(f'<li class="l{lv}"><a href="#{hid}" data-id="{hid}">{title}</a></li>' for lv, hid, title in items)


INTRO = '''<div class="box info"><div class="lbl">ℹ So funktioniert diese Seite</div>
Links zwischen <b>📖 Zusammenfassung</b> und <b>✎ Probetest</b> wechseln. In der Zusammenfassung sind bei allen <b>Übungsaufgaben</b> und <b>Theoriefragen</b> die Lösungen versteckt: erst selbst lösen (optional im Notizfeld), dann „Lösung zeigen“. Notizen und aufgedeckte Lösungen merkt sich der Browser. Im Probetest führt „Im Skript nachlesen“ zur passenden Stelle hier.</div>
'''


def main():
    ap = argparse.ArgumentParser()
    for f in ('summary', 'questions', 'template', 'out', 'title', 'sub', 'key'):
        ap.add_argument('--' + f, required=f not in ('sub',), default='')
    args = ap.parse_args()
    summary = Path(args.summary).read_text(encoding='utf-8')
    css = re.search(r'<style>(.*?)</style>', summary, re.S).group(1)
    body = re.search(r'<body>(.*?)</body>', summary, re.S).group(1)
    body = add_heading_ids(body)
    body = make_interactive(body)
    # intro box right after the title block (before the first <div class="cover">, if there is one)
    body = body.replace('<div class="cover">', INTRO + '<div class="cover">', 1) if '<div class="cover">' in body else INTRO + body
    questions = Path(args.questions).read_text(encoding='utf-8')
    tpl = Path(args.template).read_text(encoding='utf-8')
    tpl = tpl.replace('__TITLE__', args.title).replace('__SUB__', args.sub).replace('__KEY__', args.key)
    for marker in ('/*__DOCCSS__*/', '<!--__DOC__-->', '/*__QUESTIONS__*/', '<!--__TOC__-->'):
        if tpl.count(marker) != 1:
            sys.exit(f'template marker missing or duplicated: {marker}')
    page = (tpl.replace('/*__DOCCSS__*/', scope_css(css))
               .replace('<!--__DOC__-->', body)
               .replace('/*__QUESTIONS__*/', questions)
               .replace('<!--__TOC__-->', build_toc(body)))
    OUT = Path(args.out)
    OUT.write_text(page, encoding='utf-8')
    ids = re.findall(r' id="(s-[^"]+)"', body)
    dup = {i for i in ids if ids.count(i) > 1}
    refs = re.findall(r"ref:'([\d.]+)'", questions)
    missing = [r for r in refs if 's-' + r.replace('.', '-') not in ids]
    print(f'{OUT.name}: {len(page) // 1024} KB · {len(ids)} headings · '
          f'{body.count("data-rid=")} interactive items · {len(refs)} quiz refs')
    if dup:
        print('WARNING duplicate heading ids:', sorted(dup))
    if missing:
        print('WARNING quiz refs without section:', missing)


if __name__ == '__main__':
    main()
