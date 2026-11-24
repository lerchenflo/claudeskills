#!/usr/bin/env python3
"""Render the product-finder HTML report from a small curated JSON written by the agent.

  report.py curated.json [-o ~/Desktop/<slug>-<date>.html]

curated.json:
{
  "lang": "en",                                   # "en" or "de" (section headings)
  "title": "Fiat Ducato 15\" steel rim, used",
  "subtitle": "Search around <town>, rims only, max €60",
  "date": "2026-11-24",
  "spec": [["Size", "6Jx15"], ["Bolt pattern", "5x118"]],          # what must match (optional)
  "best": [{"tag": "best|check|far|new", "title": "...", "url": "...", "note": "...",
            "price": "€60 / 4", "location": "Town (DE), ~50 km"}],
  "rejected": [{"title": "...", "url": "...", "price": "€100", "why": "16\""}],
  "compare": {"text": "New price ...", "links": [{"label": "...", "url": "..."}]},   # optional
  "searches": [{"label": "willhaben: 'query', Vorarlberg", "url": "...", "note": "..."}],
  "notes": ["Local shops to ask ...", "tutti showed a CAPTCHA, not checked"]
}
Without -o the file goes to ~/Desktop/<slug of title>-<date>.html (never overwrites; adds -2, -3 ...).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
from datetime import date

H = {
    "en": {"best": "Best finds", "rejected": "Checked, not suitable", "compare": "For comparison",
           "searches": "Search again yourself", "notes": "Notes", "offer": "Offer", "price": "Price",
           "where": "Location", "why": "Why not", "searched": "Searched", "stale":
           "Listings change fast, so check each one is still online."},
    "de": {"best": "Beste Treffer", "rejected": "Geprüft, passt nicht", "compare": "Zum Vergleich",
           "searches": "Selbst nochmal suchen", "notes": "Hinweise", "offer": "Angebot", "price": "Preis",
           "where": "Ort", "why": "Warum nicht", "searched": "Gesucht am", "stale":
           "Inserate ändern sich schnell, also prüfen, ob sie noch online sind."},
}

CSS = """
:root{--bg:#f7f6f3;--fg:#1d1d1f;--muted:#6b6b70;--line:#dedcd6;--card:#fff;--accent:#1f6f50;--warn:#9a5b00;--bad:#a33;--new:#3a5fb0}
@media (prefers-color-scheme:dark){:root{--bg:#161617;--fg:#ececee;--muted:#9a9aa0;--line:#333336;--card:#1f1f21;--accent:#5cc39a;--warn:#e0a84a;--bad:#ef7b7b;--new:#8fb0f0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 20px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 10px}
.sub{color:var(--muted);margin:0 0 20px}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.spec{display:flex;flex-wrap:wrap;gap:8px 22px}.spec b{display:block;font-size:12px;color:var(--muted);font-weight:500;text-transform:uppercase;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}tr:last-child td{border-bottom:none}
td.price{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:600}a{color:var(--accent)}
.tag{display:inline-block;font-size:12px;font-weight:600;padding:1px 8px;border-radius:99px;border:1px solid currentColor;white-space:nowrap}
.t-best{color:var(--accent)}.t-check,.t-far{color:var(--warn)}.t-no{color:var(--bad)}.t-new{color:var(--new)}
ul{padding-left:20px;margin:6px 0}.muted{color:var(--muted)}footer{margin-top:40px;font-size:13px;color:var(--muted)}
"""


def e(s):
    return html.escape(str(s or ""))


def link(title, url):
    return f'<a href="{e(url)}">{e(title)}</a>' if url else e(title)


def render(d):
    h = H.get(d.get("lang", "en"), H["en"])
    dt = d.get("date") or date.today().isoformat()
    out = [f'<!DOCTYPE html><html lang="{e(d.get("lang", "en"))}"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(d.get("title"))}</title>'
           f'<style>{CSS}</style></head><body><main>',
           f'<h1>{e(d.get("title"))}</h1><p class="sub">{e(d.get("subtitle"))} {h["stale"]}</p>']
    if d.get("spec"):
        out.append('<div class="card"><div class="spec">' +
                   "".join(f"<div><b>{e(k)}</b>{e(v)}</div>" for k, v in d["spec"]) + "</div></div>")
    if d.get("best"):
        out.append(f'<h2>{h["best"]}</h2><table><thead><tr><th></th><th>{h["offer"]}</th><th>{h["price"]}</th>'
                   f'<th>{h["where"]}</th></tr></thead><tbody>')
        for b in d["best"]:
            tag = b.get("tag", "check")
            note = f'<br><span class="muted">{e(b.get("note"))}</span>' if b.get("note") else ""
            out.append(f'<tr><td><span class="tag t-{e(tag)}">{e(tag)}</span></td><td>{link(b.get("title"), b.get("url"))}'
                       f'{note}</td><td class="price">{e(b.get("price"))}</td><td>{e(b.get("location"))}</td></tr>')
        out.append("</tbody></table>")
    if d.get("rejected"):
        out.append(f'<h2>{h["rejected"]}</h2><table><thead><tr><th>{h["offer"]}</th><th>{h["price"]}</th>'
                   f'<th>{h["why"]}</th></tr></thead><tbody>')
        for r in d["rejected"]:
            out.append(f'<tr><td>{link(r.get("title"), r.get("url"))}</td><td class="price">{e(r.get("price"))}</td>'
                       f'<td><span class="tag t-no">{e(r.get("why"))}</span></td></tr>')
        out.append("</tbody></table>")
    c = d.get("compare")
    if c:
        out.append(f'<h2>{h["compare"]}</h2><p>{e(c.get("text"))}</p>')
        if c.get("links"):
            out.append("<ul>" + "".join(f'<li>{link(x.get("label"), x.get("url"))}</li>' for x in c["links"]) + "</ul>")
    if d.get("searches"):
        out.append(f'<h2>{h["searches"]}</h2><ul>')
        for s in d["searches"]:
            note = f' <span class="muted">({e(s.get("note"))})</span>' if s.get("note") else ""
            out.append(f'<li>{link(s.get("label"), s.get("url"))}{note}</li>')
        out.append("</ul>")
    if d.get("notes"):
        out.append(f'<h2>{h["notes"]}</h2><ul>' + "".join(f"<li>{e(n)}</li>" for n in d["notes"]) + "</ul>")
    out.append(f'<footer>{h["searched"]} {e(dt)}.</footer></main></body></html>')
    return "\n".join(out)


def default_path(d):
    slug = re.sub(r"[^a-z0-9]+", "-", (d.get("title") or "products").lower()).strip("-")[:50] or "products"
    base = os.path.expanduser(f"~/Desktop/{slug}-{d.get('date') or date.today().isoformat()}")
    path, n = base + ".html", 2
    while os.path.exists(path):
        path, n = f"{base}-{n}.html", n + 1
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("curated")
    p.add_argument("-o", "--out")
    a = p.parse_args()
    with open(a.curated, encoding="utf-8") as f:
        d = json.load(f)
    path = os.path.expanduser(a.out) if a.out else default_path(d)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(d))
    print(path)


if __name__ == "__main__":
    main()
