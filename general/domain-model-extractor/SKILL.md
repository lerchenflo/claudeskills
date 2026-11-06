---
name: domain-model-extractor
description: Extract the domain model of a codebase in any language (classes, tables, documents, embedded types, enums and their relations) and generate one interactive HTML page from it - a draggable diagram with click and hover highlighting of relations, an inspector, a 3D view and a plain overview list, always in the same UI. Use this whenever the user asks for a domain model, data model, entity diagram, ER diagram, class map, schema overview or "a map of all the classes and how they relate", wants to see the entities of a project, or wants to update an existing docs/domain-model.html - even if they never say "domain model". Works for Kotlin, Java, TypeScript, Python, C#, Go, Ruby, PHP, Rust, Swift and plain SQL.
---

# Domain Model Extractor

Read a project's persisted data shapes and turn them into a single self-contained page. The page
UI is fixed in `assets/template.html`, so every project gets the same look: only the model changes.
Do not write page HTML or CSS by hand, and do not change the template for one project.

## Workflow

1. Check for an existing page, by default `docs/domain-model.html`. If there is one, update it:
   `python3 <skill>/scripts/build.py docs/domain-model.html --dump > <scratch>/model.json`.
   Keep its ids, notes and open questions, and correct only what changed.
2. Find every persisted shape. `references/stacks.md` says where each stack keeps them. List all
   document, table or entity declarations with a search first and count them, so the count can be
   compared with the finished model. Read the code; do not model from memory or from old docs.
3. Write `model.json` in a scratch directory (format below). It is not a project file: the page
   holds the whole model and `--dump` gets it back.
4. Build: `python3 <skill>/scripts/build.py <scratch>/model.json --out docs/domain-model.html --title "<Project> Domain Model" --intro "<one sentence>"`.
5. Act on the build report (see "Reading the report").
6. Check the page. On macOS build `scripts/render_check.swift` (build line at its top) and run it:
   it opens the page in real WebKit, clicks the busiest box, tries the 3D view and prints overlaps,
   the click result and script errors. Look at the screenshot too. Elsewhere use any browser tool.
7. Tell the user the path and what the check proved. Say what you did not test.

## Model format

```json
{
  "packages": ["user", "billing"],
  "standardFields": ["id", "created_at", "updated_at"],
  "referenceTypes": ["UUID"],
  "knownTypes": ["Money"],
  "entities": [
    {"id": "customer", "name": "Customer", "pkg": "user", "kind": "class",
     "fields": ["id: UUID", "email: String", "tier: Tier", "address: Address?"],
     "note": "Table customers. email is unique."},
    {"id": "address", "name": "Address", "pkg": "user", "kind": "embedded", "fields": ["city: String"]},
    {"id": "tier", "name": "Tier", "pkg": "user", "kind": "enum", "fields": ["FREE", "PRO"]}
  ],
  "relations": [
    {"id": "r1", "from": "order", "to": "customer", "label": "customer", "fromCard": "*", "toCard": "1", "kind": "assoc"}
  ],
  "questions": []
}
```

- `kind`: `class` for anything with its own table or collection, `embedded` for value objects
  stored inside one, `enum` for enums (fields are the values).
- `fields`: `name: Type`, with names and types spelled as in the source language. The page matches
  on this text, so keep the colon form.
- `standardFields`: names hidden behind "Show all fields", usually id and audit columns. Pick what
  repeats on most classes in this project.
- `referenceTypes`: id types of foreign keys. A field like `customerId: UUID` or `customer_id: UUID`
  then reads `→ Customer`. Numeric keys need `"Int"` or `"Long"` here; only fields ending in id match.
- `knownTypes`: framework or library types that need no box.
- `relations`: `assoc` for references, `comp` for contained data. `fromCard` and `toCard` take `1`,
  `0..1`, `*`, `1..*` or a number. Also add a relation for a reference stored as a plain string.
- `note`: what the code does not show at a glance: collection name, uniqueness, soft delete, how a
  relation really works. It appears behind the info icon.
- Leave out `x` and `y`. The build places boxes; positions in the existing page win.

## What makes a good model

- **Same depth for every feature.** Give each feature its embedded types and enums, not only the
  one being worked on. A feature with full detail next to bare boxes looks like the main feature,
  and missing value types are what readers notice first. The `types without a box` line finds these.
- **The core stays central.** The newest or biggest feature is not automatically the core. The
  build puts the most connected class in the middle; if a large side feature dominates, move it to
  the edge in `model.json` and rebuild with `x`/`y` set on its box.
- **Keep sealed types and unions compact.** Embedded types held by exactly one class are drawn
  inside it, so one box per subclass makes that class huge. For more than a handful of subclasses
  use one embedded box with a line per subclass: `Radar: speedLimit, mobile?, redLight`. Wrap long
  lines at about 60 characters and say in the note if names were shortened.
- **A type used by several classes gets its own box.** That happens by itself, because nesting
  only applies to a single holder. Add `comp` relations so clicking it shows who uses it.
- **Do not guess.** A relation in the diagram is a claim about the code. If it is unclear whether
  something is a real link, leave it out and put it into `questions`.

## Reading the report

- `overlapping boxes`: fix before finishing, by moving a box or with `--relayout`.
- `lines behind other boxes`: some are normal around a central class. Lower the number where it is
  cheap, by setting `x`/`y` on a few boxes. Do not spend long on it: a click fades everything else,
  so the relations stay readable.
- `types without a box`: add the box, or list real framework types in `knownTypes`.
- New boxes in an existing layout land below it, so a layout the user arranged stays as it is.

## Scripts

- `scripts/build.py`: validates, places boxes, fills the template, writes the page and reports.
- `scripts/render_check.swift`: macOS render and click check.
- `references/stacks.md`: where to find the data shapes per language and framework.
