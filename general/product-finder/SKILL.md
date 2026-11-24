---
name: product-finder
description: Find a product online as cheaply as possible, used or new, by searching marketplaces (willhaben, Kleinanzeigen, ricardo, tutti, eBay.de/.at) in parallel tabs of the user's own browser (Safari for now). Asks for the exact product and the max price first, then filters the results, checks the best listings and writes an HTML report with links to the Desktop. Use this whenever the user wants to buy, find or compare prices for a product or part, especially second-hand or nearby ("ich brauche X gebraucht", "find me a cheap ...", "is there a ... near me", "search willhaben/Kleinanzeigen/eBay for ...", "what does a used ... cost"), even if they don't say "search" or name a site. Not for researching facts or comparing product specs without buying.
---

# Product finder

Classifieds sites block normal web fetching (WebFetch/WebSearch get "unable to fetch", 403 or CAPTCHAs), so this skill drives the user's real browser: `scripts/finder.py` opens one new browser window, loads every query × site as parallel tabs, reads the result lists with JavaScript, closes the window and prints a compact list. You judge the results and write the report.

Scripts live in `~/.claude/skills/product-finder/scripts/`. Use the session scratchpad as `--out` (written `$OUT` below).

## 1. Ask first (one AskUserQuestion call)

Ask everything that changes the result together. Pre-fill options from what the user already said:
- **What exactly**: model/variant and the specs that must match (size, fitting, compatibility, version). Ask what does *not* fit if that's a common trap.
- **Max price**: per piece or for the whole set. Also the quantity (1, or a set of N).
- **Condition and extras**: used/new/both, and parts to include or exclude (e.g. "rims without tyres").
- **Location**: a town to search around, plus the radius and which countries/sites to search, and whether shipping is OK. Ask every time and never store it. Tell the user the town is sent to the marketplaces only as a search filter. Use a town, not an address.

If a spec can be checked (e.g. which part fits which model), check it with WebSearch and state it in the report rather than asking.

## 2. Build queries

Write 2–5 short queries in the sites' language (German for AT/DE/CH sites). Marketplace search matches every word literally, so long queries return nothing. Vary them:
- synonyms (Felge / Felgen / Stahlfelge / Räder),
- twin models sold under other brands (e.g. Ducato = Boxer = Jumper),
- part numbers or key spec tokens (e.g. `5x118`).

## 3. Search

```bash
python3 ~/.claude/skills/product-finder/scripts/finder.py --out "$OUT" search \
  -q "query one" -q "query two" \
  --sites willhaben,kleinanzeigen,ricardo,tutti,ebay.de,ebay.at \
  --max-price 60 --at-area <state> --de-town <nearest German town> --radius 50 \
  --must 'ducato|boxer|jumper'
```
- `--at-area` is the willhaben state (tirol, wien, steiermark, …). Leave it out for all of Austria.
- `--de-town` centers Kleinanzeigen (location id is looked up automatically). For a user in Austria or Switzerland, pick the nearest German town across the border.
- `--ebay-zip` adds eBay's distance filter. eBay is mostly useful with shipping.
- ricardo and tutti have no location filter. Judge the distance from the town in each result.
- `--must` (regex, repeatable) hides printed items whose text lacks a word. Use it to cut eBay noise, but keep it loose. Everything stays in the JSON.
- Items above the max price, and Kleinanzeigen items beyond the radius, are hidden from the print but kept in the JSON. `--show-far` prints them too.
- Give the Bash call a long timeout (e.g. 600000 ms). About 12 pages take around 1–2 minutes.

The output lists each page's status (`ok`, `empty`, `blocked` = CAPTCHA/bot wall, `timeout`, `error`), then items as `price | site | km | text | url`, cheapest first. Price `?` means none was found in the card, so read the text.

Run more searches with new queries if hits are thin. Each run writes its own `results-*.json`.

## 4. Judge

Go through the list yourself. The script only sorts and filters by price:
- Does the spec match? Watch for sizes, variants and "fits" claims.
- Is the price per piece or per set? Is it VB (negotiable)? Does a sold-out/old price show beside the real one?
- Does it include extras the user doesn't want (e.g. worn tyres = disposal cost)?
- Is it close enough, or does shipping make sense? Remember customs/VAT when buying from Switzerland into the EU.
- Did the listing come from a dealer or a private seller?

For the 3–10 best candidates, read the listing pages:
```bash
python3 ~/.claude/skills/product-finder/scripts/finder.py --out "$OUT" details URL1 URL2 ...
```

Get a new-price ceiling, e.g. from the cheapest new item on eBay or a quick WebSearch. A used item should cost clearly less.

Never invent listings or details. If a field isn't stated, write "not stated, ask the seller".

## 5. Report

Write a small curated JSON to `$OUT/curated.json` (schema in the docstring of `scripts/report.py`). It holds best finds (tag `best`/`check`/`far`/`new`) with a one-line note on what to ask the seller, checked-but-unsuitable offers with the reason, the comparison price, ready search links for the user, and notes (blocked sites, local shops worth asking). Use the user's language for `lang`/texts if they wrote in German. Then:
```bash
python3 ~/.claude/skills/product-finder/scripts/report.py "$OUT/curated.json"
```
It writes `~/Desktop/<title-slug>-<date>.html` (never overwrites) and prints the path. In chat give the top 1–3 finds and the full file path.

## Rules

- **Blocks**: if a site shows a CAPTCHA or bot wall, report it and move on. Never try to get past it.
- **Read only**: don't log in, contact sellers, bid or buy.
- **Volume**: keep it human-scale, a few dozen pages per run.
- **Private data**: the only private data sent to sites is the search town the user gave. Nothing else (name, e-mail, address) goes into any URL or form.
- **Window**: the script works in its own window and closes it. `--keep-open` leaves it open for debugging.

## Setup and troubleshooting

- **Safari**: Settings > Advanced > "Show features for web developers", then Develop menu > "Allow JavaScript from Apple Events". On the first run macOS may ask to let the terminal control Safari. The script exits with this hint if JS is off.
- **A site returns `empty` though it has results**: its markup changed. Run with `--keep-open`, inspect the page, and update the site's `list` config in `scripts/sites.py`. Prefer link-URL patterns and data attributes over CSS classes.
- **Add a site**: add an entry in `scripts/sites.py` (URL builder, list config, optional detail selectors).
- **Add a browser** (e.g. Chrome): add a backend in `scripts/browsers/` with the same methods as `safari.py`, and register it in `browsers/__init__.py`. Then use `--browser chrome`.
