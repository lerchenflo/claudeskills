#!/usr/bin/env python3
"""Turn a domain model JSON file into the interactive HTML page.

Usage:
    python3 build.py model.json --out docs/domain-model.html --title "Acme Domain Model"
    python3 build.py docs/domain-model.html --dump > model.json

The page holds the whole model, so no separate JSON file has to stay in the project: --dump reads
it back out for the next update. Box positions already in the output page win, so a rebuild keeps a layout the user dragged and
saved. Boxes without a position are placed automatically. --relayout places every box again.
Exit code 2 means the model is invalid and nothing was written.
"""
import argparse
import html
import json
import math
import random
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
MODEL_RE = re.compile(r'(<script type="application/json" id="model">\s*)(.*?)(\s*</script>)', re.S)
KINDS = ("class", "embedded", "enum")
RELATION_KINDS = ("assoc", "comp")

DEFAULT_STANDARD = ["id", "createdAt", "updatedAt", "updatedBy", "deleted"]
DEFAULT_REFERENCE_TYPES = ["ObjectId", "UUID", "Uuid", "Guid"]
DEFAULT_INTRO = "Domain classes and how they relate."
USAGE_TEXT = (
    "Standard fields are hidden unless you use “Show all fields”. Hover or click a class to "
    "highlight its relations. Scroll or pinch to zoom, drag empty space to move around. Drag "
    "boxes, click one to edit. Edits are kept as a draft in this browser until you use “Save to file”."
)

# Types that need no box of their own, across the languages this skill targets.
BUILTIN_TYPES = set("""
    String Str Int Integer Long Short Byte Double Float Number Boolean Bool Char Decimal BigDecimal BigInt
    BigInteger Instant Date DateTime DateTimeOffset LocalDate LocalDateTime LocalTime OffsetDateTime
    ZonedDateTime Duration TimeSpan Timestamp Time UUID Uuid Guid ObjectId Object Any Unit Void None True False
    List Set Map Array Seq Vec Option Optional Nullable Collection ICollection IEnumerable IList Dictionary
    HashMap HashSet Record Tuple Mapping Sequence Iterable JSON Json JsonValue Bytes ByteArray ByteString
""".split())

# Same size rules as layoutOf in the page, used only to place boxes.
CHAR_W, LINE_H, HEAD_H, PAD, INNER, SUB_HEAD = 8.5, 22, 54, 14, 10, 28
GAP_X, GAP_Y = 150, 90


def fail(problems):
    print("Invalid model:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    sys.exit(2)


def validate(model):
    problems = []
    entities = model.get("entities", [])
    ids = [e.get("id") for e in entities]
    names = [e.get("name") for e in entities]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate entity id {dup}")
    for dup in sorted({n for n in names if names.count(n) > 1}):
        problems.append(f"duplicate entity name {dup}: rename one, nesting and references match by name")
    for e in entities:
        if e.get("kind") not in KINDS:
            problems.append(f"{e.get('id')}: kind must be one of {KINDS}")
        if not e.get("fields"):
            problems.append(f"{e.get('id')}: has no fields")
    known = set(ids)
    rel_ids = [r.get("id") for r in model.get("relations", [])]
    for dup in sorted({i for i in rel_ids if rel_ids.count(i) > 1}):
        problems.append(f"duplicate relation id {dup}")
    for r in model.get("relations", []):
        for end in ("from", "to"):
            if r.get(end) not in known:
                problems.append(f"relation {r.get('id')}: unknown {end} {r.get(end)}")
        if r.get("kind") not in RELATION_KINDS:
            problems.append(f"relation {r.get('id')}: kind must be one of {RELATION_KINDS}")
    if problems:
        fail(problems)


class Sizes:
    """Mirrors how the page draws boxes: nesting, hidden fields, reference display."""

    def __init__(self, model):
        self.model = model
        self.entities = {e["id"]: e for e in model["entities"]}
        self.standard = set(model.get("standardFields", DEFAULT_STANDARD))
        self.reference_types = model.get("referenceTypes", DEFAULT_REFERENCE_TYPES)
        self.parent = self._nesting()
        self.kids = {}
        for e in model["entities"]:
            if e["id"] in self.parent:
                self.kids.setdefault(self.parent[e["id"]], []).append(e["id"])
        self.tops = [e["id"] for e in model["entities"] if e["id"] not in self.parent]

    def _nesting(self):
        holders = {}

        def add(child, holder):
            if child != holder:
                holders.setdefault(child, set()).add(holder)

        for r in self.model["relations"]:
            add(r["to"], r["from"])
        for e in self.model["entities"]:
            for f in e["fields"]:
                t = ":".join(f.split(":")[1:])
                for x in self.model["entities"]:
                    if x["kind"] != "class" and re.search(rf"\b{re.escape(x['name'])}\b", t):
                        add(x["id"], e["id"])
        parent = {k: next(iter(v)) for k, v in holders.items() if self.entities[k]["kind"] != "class" and len(v) == 1}
        for i in list(parent):
            seen, q = {i}, parent.get(i)
            while q:
                if q in seen:
                    del parent[i]
                    break
                seen.add(q)
                q = parent.get(q)
        return parent

    def _reference(self, f):
        m = re.match(r"^(\w+?_?[Ii]ds?)\s*:\s*(.+)$", f)
        if not m or not any(re.search(rf"\b{re.escape(t)}\b", m.group(2)) for t in self.reference_types):
            return None
        base = re.sub(r"_", "", re.sub(r"_?[Ii]ds?$", "", m.group(1))).lower()
        best = None
        for x in self.model["entities"]:
            if x["kind"] != "enum" and base.endswith(x["name"].lower()) and (not best or len(x["name"]) > len(best["name"])):
                best = x
        if not best:
            return None
        many = re.search(r"^\s*(list|set|array|seq|vec|collection|icollection|ienumerable)\b|\[\s*\]\s*$", m.group(2), re.I)
        optional = re.search(r"\?\s*$|optional|nullable|\|\s*(none|null|undefined)", m.group(2), re.I)
        return f"{m.group(1)} → {best['name']}" + (" (many)" if many else " (optional)" if optional else "")

    @staticmethod
    def _wrap(items, width):
        out, cur = [], ""
        for it in items:
            nxt = f"{cur} · {it}" if cur else it
            if cur and len(nxt) > width:
                out.append(cur)
                cur = it
            else:
                cur = nxt
        return out + ([cur] if cur else [])

    def size(self, i, nested=False):
        e = self.entities[i]
        head = SUB_HEAD if nested else HEAD_H
        if e["kind"] == "enum":
            lines = self._wrap(e["fields"], 30) if nested else e["fields"]
        else:
            shown = [self._reference(f) or f for f in e["fields"] if f.split(":")[0].strip() not in self.standard]
            lines = shown + (["+ n standard fields"] if len(shown) < len(e["fields"]) else [])
        sub = [self.size(k, True) for k in self.kids.get(i, [])]
        title = f"«{e['kind']}» {e['name']}" if nested else e["name"]
        longest = max([len(title)] + [len(l) for l in lines] + [10])
        w = max([0 if nested else 200, math.ceil(longest * CHAR_W) + PAD * 2] + [s[0] + INNER * 2 for s in sub])
        h = head + max(0 if nested else 1, len(lines)) * LINE_H + (6 if nested else PAD)
        return w, h + sum(s[1] + INNER for s in sub)

    def top_of(self, i):
        while i in self.parent:
            i = self.parent[i]
        return i


def crosses(ax, ay, bx, by, rect):
    """Liang-Barsky: does the segment touch the rectangle?"""
    x0, y0, x1, y1 = rect
    t0, t1 = 0.0, 1.0
    dx, dy = bx - ax, by - ay
    for p, q in ((-dx, ax - x0), (dx, x1 - ax), (-dy, ay - y0), (dy, y1 - ay)):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def blocked_lines(edges, boxes):
    """Edges whose straight line runs behind a third box, as {edge: [boxes]}."""
    centers = {i: (x + w / 2, y + h / 2) for i, (x, y, w, h) in boxes.items()}
    rects = {i: (x - 8, y - 8, x + w + 8, y + h + 8) for i, (x, y, w, h) in boxes.items()}
    out = {}
    for a, b in edges:
        hit = [c for c in boxes if c not in (a, b) and crosses(*centers[a], *centers[b], rects[c])]
        if hit:
            out[(a, b)] = hit
    return out


def score(edges, boxes):
    centers = {i: (x + w / 2, y + h / 2) for i, (x, y, w, h) in boxes.items()}
    length = sum(math.dist(centers[a], centers[b]) for a, b in edges)
    return length + 3000 * sum(len(v) for v in blocked_lines(edges, boxes).values())


def grid_boxes(grid, sizes, rows, cols, start_x=40, start_y=40):
    col_w = [max([sizes[t][0] for (r, c), t in grid.items() if c == k] or [200]) for k in range(cols)]
    row_h = [max([sizes[t][1] for (r, c), t in grid.items() if r == k] or [120]) for k in range(rows)]
    xs = [start_x + sum(col_w[:k]) + GAP_X * k for k in range(cols)]
    ys = [start_y + sum(row_h[:k]) + GAP_Y * k for k in range(rows)]
    return {t: (xs[c], ys[r], *sizes[t]) for (r, c), t in grid.items()}


def auto_layout(ids, sizes, edges, start_x=40, start_y=40):
    """Busiest box in the middle, then swap boxes while lines get shorter and clearer."""
    degree = {i: 0 for i in ids}
    for a, b in edges:
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    linked = sorted([i for i in ids if degree[i]], key=lambda i: -degree[i])
    free = [i for i in ids if not degree[i]]
    positions = {}
    right = start_x
    if linked:
        cols = max(2, round(math.sqrt(len(linked) * 1.3)))
        rows = math.ceil(len(linked) / cols)
        cells = sorted(((r, c) for r in range(rows) for c in range(cols)),
                       key=lambda rc: 1.6 * (rc[0] - (rows - 1) / 2) ** 2 + (rc[1] - (cols - 1) / 2) ** 2)
        grid = dict(zip(cells, linked))
        local = [e for e in edges if e[0] in linked and e[1] in linked]
        rng = random.Random(1)
        best = score(local, grid_boxes(grid, sizes, rows, cols, start_x, start_y))
        for _ in range(min(4000, 300 * len(linked))):
            p, q = rng.sample(cells, 2)
            a, b = grid.get(p), grid.get(q)
            trial = dict(grid)
            trial.pop(p, None)
            trial.pop(q, None)
            if a:
                trial[q] = a
            if b:
                trial[p] = b
            s = score(local, grid_boxes(trial, sizes, rows, cols, start_x, start_y))
            if s < best:
                best, grid = s, trial
        boxes = grid_boxes(grid, sizes, rows, cols, start_x, start_y)
        positions.update({i: (x, y) for i, (x, y, _, _) in boxes.items()})
        right = max(x + w for x, y, w, h in boxes.values()) + GAP_X
    # Boxes without relations go to the side, so they never sit between connected ones.
    limit = max([y + h for i, (x, y) in positions.items() for w, h in [sizes[i]]] + [1600])
    x, y, width = right, start_y, 0
    for i in sorted(free, key=lambda f: -sizes[f][1]):
        w, h = sizes[i]
        if y + h > limit and y > start_y:
            x, y, width = x + width + 60, start_y, 0
        positions[i] = (x, y)
        y += h + 40
        width = max(width, w)
    return positions


def types_without_box(model):
    known = {e["name"] for e in model["entities"]} | BUILTIN_TYPES | set(model.get("knownTypes", []))
    missing = {}
    for e in model["entities"]:
        if e["kind"] == "enum":
            continue
        for f in e["fields"]:
            for token in re.findall(r"[A-Za-z_]\w*", ":".join(f.split(":")[1:])):
                if token[0].isupper() and token not in known:
                    missing.setdefault(token, []).append(e["name"])
    return missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", type=Path)
    ap.add_argument("--out", type=Path, help="page to write")
    ap.add_argument("--title", help="page title, by default the one of the existing page")
    ap.add_argument("--dump", action="store_true", help="print the model inside the given page and exit")
    ap.add_argument("--intro", default=DEFAULT_INTRO, help="first sentence below the title")
    ap.add_argument("--relayout", action="store_true", help="ignore existing positions")
    args = ap.parse_args()

    text = args.model.read_text(encoding="utf-8")
    source = MODEL_RE.search(text) if args.model.suffix == ".html" else None
    if args.model.suffix == ".html" and not source:
        fail([f"{args.model} has no model block"])
    model = json.loads(source.group(2) if source else text)
    if args.dump:
        print(json.dumps(model, indent=1, ensure_ascii=False))
        return
    if not args.out:
        ap.error("--out is required unless --dump is used")
    if not args.title:
        old = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        found = re.search(r"<title>(.*?)</title>", old)
        if not found:
            ap.error("--title is required for a new page")
        args.title = html.unescape(found.group(1))
    model.setdefault("packages", sorted({e.get("pkg", "") for e in model.get("entities", [])} - {""}))
    model.setdefault("relations", [])
    model.setdefault("questions", [])
    validate(model)
    sizing = Sizes(model)
    sizes = {i: sizing.size(i) for i in sizing.tops}

    placed = {}
    if not args.relayout:
        placed = {e["id"]: (e["x"], e["y"]) for e in model["entities"] if "x" in e and "y" in e}
        if args.out.exists():
            m = MODEL_RE.search(args.out.read_text(encoding="utf-8"))
            if m:
                old = json.loads(m.group(2))
                placed.update({e["id"]: (e["x"], e["y"]) for e in old.get("entities", []) if "x" in e and "y" in e})

    edges = sorted({tuple(sorted((sizing.top_of(r["from"]), sizing.top_of(r["to"])))) for r in model["relations"]})
    edges = [(a, b) for a, b in edges if a != b]
    missing = [i for i in sizing.tops if i not in placed]
    if len(missing) == len(sizing.tops):
        placed = auto_layout(sizing.tops, sizes, edges)
    elif missing:
        # New boxes go below the existing layout, so nothing the user arranged moves.
        below = max(placed[i][1] + sizes[i][1] for i in sizing.tops if i in placed) + GAP_Y
        inner = [(a, b) for a, b in edges if a in missing and b in missing]
        placed.update(auto_layout(missing, sizes, inner, start_y=below))
        print(f"placed new boxes below the layout: {', '.join(missing)}")
    for e in model["entities"]:
        # Nested boxes get their position from the holder; 0 keeps the field present for the page.
        e["x"], e["y"] = placed.get(e["id"], (0, 0))

    boxes = {i: (*placed[i], *sizes[i]) for i in sizing.tops}
    overlaps = [(a, b) for n, a in enumerate(sizing.tops) for b in sizing.tops[n + 1:]
                if boxes[a][0] < boxes[b][0] + boxes[b][2] and boxes[b][0] < boxes[a][0] + boxes[a][2]
                and boxes[a][1] < boxes[b][1] + boxes[b][3] and boxes[b][1] < boxes[a][1] + boxes[a][3]]
    blocked = blocked_lines(edges, boxes)
    gaps = types_without_box(model)

    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html.escape(args.title))
    page = page.replace("__SUBTITLE__", html.escape(f"{args.intro} {USAGE_TEXT}", quote=False))
    body = json.dumps(model, indent=1, ensure_ascii=False).replace("</", "<\\/")
    page, n = MODEL_RE.subn(lambda m: m.group(1) + body + m.group(3), page, count=1)
    assert n == 1, "model block not found in template"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")

    print(f"wrote {args.out}: {len(model['entities'])} entities ({len(sizing.tops)} boxes), {len(model['relations'])} relations")
    print(f"overlapping boxes: {len(overlaps)} {overlaps[:10] if overlaps else ''}")
    print(f"lines behind other boxes: {len(blocked)}")
    for (a, b), hit in list(blocked.items())[:12]:
        print(f"  {a} - {b}: behind {', '.join(hit)}")
    if gaps:
        print(f"types without a box: {len(gaps)} (add a box, or list them in \"knownTypes\" if they are framework types)")
        for t, used in sorted(gaps.items()):
            print(f"  {t}: used by {', '.join(sorted(set(used)))}")
    else:
        print("types without a box: 0")


if __name__ == "__main__":
    main()
