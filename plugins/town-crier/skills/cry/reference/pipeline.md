# Pipeline contract

How the steps pass data to each other, and how theme skills extend base skills.

## Steps
| Step | Skill | Reads | Writes |
|---|---|---|---|
| 0. Resolve config | `cry` | user config, `config/default.yaml` | `config.resolved.yaml` |
| 1. Look for papers | `fetch-papers` | `config.resolved.yaml` | `candidates.jsonl` |
| 2. Select and count | `select-papers` | `candidates.jsonl`, config | `selection.json` |
| 3a. Extract | `extract-paper` or theme skill | `selection.json`, candidates | `extracted/<paper_id>.json` |
| 3b. Summarize | `summarize-category-<N>` or theme skill | `extracted/` | `summaries/<subsection_id>.md` |
| 4. Assemble | `assemble-digest` | `summaries/`, `selection.json`, config | output file |

## Run folder
```
town-crier-runs/<start>_<end>/
├── config.resolved.yaml
├── candidates.jsonl
├── selection.json
├── extracted/<paper_id>.json
├── summaries/<subsection_id>.md
└── <output.filename>
```
`<paper_id>` in file names: replace `:` and `/` with `_`.

## Records

### `config.resolved.yaml`
The merged configuration, with every default filled in, plus:
```yaml
period: {start: 2026-10-16, end: 2026-10-23, label: "this week"}
# every section and subsection carries its id: "1", "1.1", …
```

### `candidates.jsonl` — one paper per line
```json
{"paper_id": "arXiv:2610.01234", "title": "…", "authors": ["…"], "abstract": "…",
 "url": "https://arxiv.org/abs/2610.01234", "doi": null, "source": "arxiv",
 "categories": ["astro-ph.GA"], "date": "2026-10-20", "found_for": ["1.1", "2.2"]}
```
- `paper_id`: `arXiv:<id>`, else `doi:<DOI>`.
- `date`: first release date (arXiv v1 or journal publication date).
- `found_for`: subsections whose sources returned the paper.

### `selection.json`
```json
{"period": {"start": "2026-10-16", "end": "2026-10-23", "label": "this week"},
 "subsections": {
   "1.1": {"count": 14, "count_method": "on_theme",
           "papers": [{"paper_id": "arXiv:2610.01234", "rank": 1, "reason": "…"}]}
 }}
```
`count` is `null` when the subsection's `count` is false.

### `extracted/<paper_id>.json`
```json
{"paper_id": "…", "title": "…", "url": "…", "read": "abstract | full_text",
 "fields": {"context": "…", "aims": "…", "methods": "…", "results": "…",
            "conclusions": "…", "key_numbers": ["…"]},
 "theme_fields": {}}
```
`theme_fields` holds what a theme extraction skill adds.

### `summaries/<subsection_id>.md`
The subsection's entries, in rank order, in its category's format.
No subsection heading: `assemble-digest` adds it.

## Rules across steps
- A paper appears at most once in the output. Subsections are served in reading order; a paper kept by an earlier subsection is skipped by later ones.
- Only papers dated inside the period are kept.
- Never invent a paper, an author, a link or a result. If a step fails, the output says what is missing.

## Theme skills: inheritance
A theme skill specializes a base skill for one theme.

| Base skill | Theme skill name |
|---|---|
| `extract-paper` | `extract-paper-<theme>` |
| `summarize-category-1` | `summarize-category-1-<theme>` |
| `summarize-category-2` | `summarize-category-2-<theme>` |
| `summarize-category-3` | `summarize-category-3-<theme>` |

- The theme skill's body starts with a `## Extends` section naming its base skill.
- To run it: load the base skill, then the theme skill. Apply both.
- The theme skill may add fields and rules, or tighten them. It may not drop the base's required fields or exceed its length limit.
- A subsection uses a theme skill only when its config names it under `skills:`.
- A `summarize-category-N-<theme>` skill may only serve subsections of category N.
