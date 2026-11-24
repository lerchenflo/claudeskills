#!/usr/bin/env python3
"""Product finder: runs many marketplace searches as parallel tabs in the user's browser and collects results.

  finder.py search -q "query 1" -q "query 2" --sites willhaben,kleinanzeigen --max-price 60 \
      --at-area tirol --de-town Muenchen --radius 50 --out DIR
  finder.py details --out DIR URL [URL ...]

Writes the raw results as JSON to DIR and prints a compact list (cheapest first) for the agent to judge.
Opens its own browser window and closes it at the end; never touches the user's tabs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browsers import get_browser  # noqa: E402
from browsers.safari import BrowserError  # noqa: E402
from sites import SITES, site_for_url  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def js_file(name: str) -> str:
    with open(os.path.join(HERE, "js", name), encoding="utf-8") as f:
        return f.read()


# ---------- prices ----------

_FREE = re.compile(r"zu verschenken|gratis|kostenlos|\bfree\b|à donner", re.I)
_CUR = re.compile(r"(?:€|EUR|CHF|Fr\.)\s*(\d[\d.',]*)|(\d[\d.',]*)\s*(?:€|EUR|CHF|Fr\.)")
_CHF_DASH = re.compile(r"(?<![\d.])(\d[\d']*)\.[-–]")
_CHF_PLAIN = re.compile(r"(?<![\d.])(\d[\d']*\.\d{2})(?![\d.])")
_SHIP = re.compile(r"\+\s*(?:EUR|CHF|€)\s*(\d[\d.,']*)\s*(?:Versand|Lieferung|shipping|delivery)", re.I)
_SHIP_FREE = re.compile(r"Gratis (?:Versand|Lieferung)|Kostenloser Versand|Free (?:shipping|delivery)", re.I)
_KM = re.compile(r"\((?:ca\. )?(\d+) km\)")
_EBAY_ID = re.compile(r"ebay\.[a-z.]+/itm/(\d+)")


def _num(s: str):
    s = s.replace("'", "").strip(".,")
    if not s:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if len(s.split(",")[-1]) == 2 else s.replace(",", "")
    elif "." in s and len(s.split(".")[-1]) == 3:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_price(text: str, currency: str):
    if not text:
        return None
    t = text.replace("\xa0", " ")
    m = _CUR.search(t)
    if m:
        return _num(m.group(1) or m.group(2))
    if _FREE.search(t):
        return 0.0
    if currency == "CHF":
        m = _CHF_DASH.search(t) or _CHF_PLAIN.search(t)
        if m:
            return _num(m.group(1))
    return None


# ---------- browser batch ----------

def load_batch(b, win, urls, first_batch, wait_s):
    """Load urls into tabs 1..n of win (opening tabs as needed), wait until loaded."""
    count = b.tab_count(win)
    for i, u in enumerate(urls, start=1):
        if first_batch and i == 1:
            continue  # tab 1 already loads it (window was created with it) or was navigated
        if i <= count:
            b.navigate(win, i, u)
        else:
            b.open_tab(win, u)
    time.sleep(2.0)
    deadline = time.time() + wait_s
    pending = set(range(1, len(urls) + 1))
    while pending and time.time() < deadline:
        for i in list(pending):
            if b.ready_state(win, i) == "complete":
                pending.discard(i)
        if pending:
            time.sleep(0.7)
    time.sleep(1.5)  # let client-side rendering settle
    return pending


def run_pages(b, win, jobs, js_builder, max_tabs, wait_s, first_loaded=False):
    """jobs: list of dicts with 'url'. Returns list of (job, parsed_json_or_error)."""
    out = []
    for start in range(0, len(jobs), max_tabs):
        batch = jobs[start:start + max_tabs]
        if not (start == 0 and first_loaded):
            b.navigate(win, 1, batch[0]["url"])
        slow = load_batch(b, win, [j["url"] for j in batch], True, wait_s)
        for i, job in enumerate(batch, start=1):
            try:
                raw = b.run_js(win, i, js_builder(job))
                data = json.loads(raw) if raw else {"status": "error", "error": "no result"}
            except (BrowserError, json.JSONDecodeError) as e:
                if "Apple Events" in str(e):
                    raise
                data = {"status": "error", "error": str(e)[:200]}
            if i in slow and data.get("status") == "ok" and not data.get("items") and not data.get("fields"):
                data["status"] = "timeout"
            out.append((job, data))
    return out


def ka_lookup_town(b, win, town):
    js = ("(function(){var x=new XMLHttpRequest();x.open('GET','/s-ort-empfehlungen.json?query='+"
          "encodeURIComponent(%s),false);x.send();return x.responseText})()" % json.dumps(town))
    raw = b.run_js(win, 1, js)
    data = json.loads(raw)
    for k, v in data.items():
        if k != "_0":
            return k.lstrip("_"), v
    return None, None


def slugify(s):
    s = s.lower()
    for a, r in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, r)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ---------- commands ----------

def cmd_search(a):
    sites = [s.strip() for s in a.sites.split(",") if s.strip()]
    for s in sites:
        if s not in SITES:
            sys.exit(f"Unknown site '{s}'. Known: {', '.join(SITES)}")
    opts = {"max_price": a.max_price, "at_area": a.at_area, "radius": a.radius, "ebay_zip": a.ebay_zip,
            "de_town_id": a.de_town_id, "de_town_slug": slugify(a.de_town) if a.de_town else None}

    b = get_browser(a.browser)
    first_url = "https://www.kleinanzeigen.de/" if ("kleinanzeigen" in sites and a.de_town and not a.de_town_id) else None
    win = b.new_window(first_url or "about:blank")
    notes = []
    try:
        if first_url:
            load_batch(b, win, [first_url], True, a.wait)
            tid, tname = ka_lookup_town(b, win, a.de_town)
            if tid:
                opts["de_town_id"] = tid
                notes.append(f"kleinanzeigen location: {tname} (id {tid}, radius {a.radius} km)")
            else:
                notes.append(f"kleinanzeigen: town '{a.de_town}' not found, searching all of Germany")
        else:
            b.run_js(win, 1, "1+1")  # fails early with a clear hint if JS from Apple Events is off

        jobs = [{"site": s, "query": q, "url": SITES[s]["url"](q, opts)} for q in a.query for s in sites]

        def js_for(job):
            return "var CFG = %s;\n%s" % (json.dumps(SITES[job["site"]]["list"]), js_file("extract_list.js"))

        results = run_pages(b, win, jobs, js_for, a.max_tabs, a.wait)
    finally:
        if not a.keep_open:
            b.close_window(win)

    # merge, parse, dedupe
    items, pages = {}, []
    for job, data in results:
        cur = SITES[job["site"]]["currency"]
        st = data.get("status", "error")
        pages.append({"site": job["site"], "query": job["query"], "url": job["url"], "status": st,
                      "count": len(data.get("items", [])), "total": data.get("total"),
                      "text": data.get("text", "")[:300] if st != "ok" else "", "error": data.get("error")})
        for it in data.get("items", []):
            url = it.get("url") or ""
            if not url:
                continue
            m = _EBAY_ID.search(url)
            if m:  # same item on ebay.de and ebay.at; drop tracking params
                url = url.split("/itm/")[0] + "/itm/" + m.group(1)
            key = "ebay:" + m.group(1) if m else url.split("?")[0]
            text = " ".join(x for x in (it.get("title"), it.get("price"), it.get("location"), it.get("text")) if x)
            price = parse_price(it.get("price") or it.get("text") or "", cur)
            if key in items:
                items[key]["queries"].append(job["query"])
                continue
            km = _KM.search(text)
            sm = _SHIP.search(text)
            ship = _num(sm.group(1)) if sm else (0.0 if _SHIP_FREE.search(text) else None)
            items[key] = {"site": job["site"], "currency": cur, "price": price, "ship": ship, "title": it.get("title"),
                          "location": it.get("location"), "km": int(km.group(1)) if km else None,
                          "text": text[:420], "url": url, "queries": [job["query"]]}

    def total(x):
        return (x["price"] or 0) + (x["ship"] or 0)
    allitems = sorted(items.values(), key=lambda x: (x["price"] is None, total(x)))
    for it in allitems:
        it["over_max"] = bool(a.max_price and it["price"] is not None and it["price"] > a.max_price)

    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "results-%s.json" % datetime.now().strftime("%Y%m%d-%H%M%S"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"queries": a.query, "sites": sites, "options": opts, "notes": notes, "pages": pages,
                   "items": allitems}, f, ensure_ascii=False, indent=1)

    # compact print
    for n in notes:
        print("NOTE", n)
    print("PAGES (site | query | status | items):")
    for p in pages:
        extra = f" | {p['error'] or p['text'][:120]}" if p["status"] != "ok" else ""
        print(f"  {p['site']} | {p['query']} | {p['status']} | {p['count']}{extra}")
        if p["status"] != "ok":
            print(f"    {p['url']}")
    musts = [re.compile(m, re.I) for m in (a.must or [])]
    radius = a.radius if a.de_town or a.ebay_zip else None
    shown, hidden = [], {"over max price": 0, "missing --must word": 0, "outside radius": 0}
    for i in allitems:
        if i["over_max"]:
            hidden["over max price"] += 1
        elif musts and not all(m.search(i["text"]) for m in musts):
            hidden["missing --must word"] += 1
        elif radius and i["km"] is not None and i["km"] > radius and not a.show_far:
            hidden["outside radius"] += 1
        else:
            shown.append(i)
    hid = ", ".join(f"{v} {k}" for k, v in hidden.items() if v)
    print(f"ITEMS: {len(shown)} shown (cheapest incl. shipping first){'; hidden: ' + hid if hid else ''} (all in JSON):")
    for it in shown[: a.limit]:
        pr = "?" if it["price"] is None else f"{it['price']:g} {it['currency']}"
        if it["ship"]:
            pr += f" +{it['ship']:g} ship"
        km = f" | {it['km']} km" if it["km"] is not None else ""
        print(f"- {pr} | {it['site']}{km} | {it['text'][:a.chars]} | {it['url']}")
    if len(shown) > a.limit:
        print(f"... {len(shown) - a.limit} more in JSON")
    print("JSON:", path)


def cmd_details(a):
    b = get_browser(a.browser)
    jobs = [{"url": u, "site": site_for_url(u)} for u in a.urls]

    def js_for(job):
        sel = (SITES.get(job["site"]) or {}).get("detail") or {}
        return "var CFG = %s;\n%s" % (json.dumps({"sel": sel, "max": a.chars}), js_file("extract_detail.js"))

    win = b.new_window(jobs[0]["url"])
    try:
        results = run_pages(b, win, jobs, js_for, a.max_tabs, a.wait, first_loaded=True)
    finally:
        if not a.keep_open:
            b.close_window(win)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "details-%s.json" % datetime.now().strftime("%Y%m%d-%H%M%S"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump([{"url": j["url"], **d} for j, d in results], f, ensure_ascii=False, indent=1)
    for job, d in results:
        print("===", job["url"], "|", d.get("status"))
        for k, v in (d.get("fields") or {}).items():
            print(f"  {k}: {v}")
        if d.get("error"):
            print("  error:", d["error"])
    print("JSON:", path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--browser", default="safari")
    p.add_argument("--out", required=True, help="folder for JSON results (session scratchpad)")
    p.add_argument("--max-tabs", type=int, default=8, help="tabs loaded at once")
    p.add_argument("--wait", type=float, default=25, help="seconds to wait for a batch to load")
    p.add_argument("--keep-open", action="store_true", help="leave the search window open (debugging)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("-q", "--query", action="append", required=True)
    s.add_argument("--sites", default="willhaben,kleinanzeigen,ricardo,tutti,ebay.de,ebay.at")
    s.add_argument("--max-price", type=float)
    s.add_argument("--at-area", help="willhaben state, e.g. tirol, wien, steiermark")
    s.add_argument("--de-town", help="Kleinanzeigen center town, e.g. Muenchen")
    s.add_argument("--de-town-id", help="Kleinanzeigen location id (skips the lookup)")
    s.add_argument("--radius", type=int, default=50, help="km around --de-town / --ebay-zip")
    s.add_argument("--ebay-zip", help="postal code for eBay distance filter")
    s.add_argument("--must", action="append", help="regex an item text must match to be printed, e.g. 'ducato|boxer|jumper' (repeatable, all must match)")
    s.add_argument("--show-far", action="store_true", help="also print items beyond --radius (Kleinanzeigen adds far results)")
    s.add_argument("--limit", type=int, default=60, help="max items printed")
    s.add_argument("--chars", type=int, default=150, help="chars of text printed per item")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("details")
    d.add_argument("urls", nargs="+")
    d.add_argument("--chars", type=int, default=900)
    d.set_defaults(func=cmd_details)

    a = p.parse_args()
    try:
        a.func(a)
    except BrowserError as e:
        sys.exit(f"Browser error: {e}")


if __name__ == "__main__":
    main()
