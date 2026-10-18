# Store listing text

Written next to the images, into `storeassets/listing/<locale>.txt`, one file per locale. Same
language as the screenshots. Every field has a hard limit - count characters (`len()` in Python, not
bytes) before handing over; App Store Connect and Play Console cut or reject anything longer.

| Field | Store | Limit | Notes |
|---|---|---|---|
| App name | both | 30 | Usually fixed already; only suggest if asked. |
| Subtitle | App Store | 30 | One benefit, under the name in search. Indexed for search. |
| Promotional text | App Store | 170 | Top of the description, changeable without a review - news, seasonal hooks. Not indexed. |
| Keywords | App Store | 100 | Comma-separated, **no spaces after commas**, no words already in name/subtitle, no plurals of the same word, no competitor names. Indexed. |
| Short description | Play | 80 | Shown before "more". Indexed. |
| Description | both | 4000 | First 2-3 lines are what people read before expanding: lead with the core benefit, then features as short paragraphs or `•` lines, then who it is for. No keyword stuffing (Play penalises it). |

How to write it:
- Source the features from the app itself (the screens just captured, the nav destinations, the
  README/CLAUDE.md product section), never invent capabilities. Follow the same feature order as the
  screenshots so text and images tell one story.
- Mention paid/subscription facts only as the user states them.
- Draft all fields, show them, let the user edit, then write the file. Check limits with:

```bash
python3 - <<'PY'
import re,sys
t=open("storeassets/listing/de.txt").read()
for name,lim in [("Subtitle",30),("Promotional text",170),("Keywords",100),("Short description",80),("Description",4000)]:
    m=re.search(rf"^## {name}\n(.*?)(?=^## |\Z)",t,re.S|re.M); n=len(m.group(1).strip()) if m else -1
    print(f"{name}: {n}/{lim}", "OK" if 0<=n<=lim else "TOO LONG/MISSING")
PY
```

File layout (the checker relies on the `## ` headings):

```
## Subtitle
...
## Promotional text
...
## Keywords
...
## Short description
...
## Description
...
```
