# Pipeline reference

## Overview
```
GitHub Action (daily)          Claude run (per digest)
──────────────────────         ──────────────────────────────────────────────
arXiv, bioRxiv/medRxiv,  ──►   data branch ──► load ──► select ──► extract ──► summarize ──► assemble ──► check
OpenAlex  ──► data branch                     (stage 1)  (stage 2)  (alphaXiv for
                                                                    category 1)
```

## Data branch (written by the Action)
```
index.json                    databases, files, run days, coverage per scope, compiled themes
last_run.json                 papers added and errors of the last fetch
<database>/<YYYY-MM-DD>.jsonl papers first seen that day
```
Each paper is stored once, under the day the daily fetch first saw it (about its arXiv
announcement day). Consecutive digests therefore never miss or repeat a paper.
Databases: `arxiv`, `biorxiv`, `medrxiv`, `openalex`. What is fetched is the union of
the `databases` declared by all theme definitions.

## Run folder (written by `tc.py`)
| File | Written by | Content |
|---|---|---|
| `config.resolved.yaml` | `resolve` | Merged configuration, period, numbered subsections, themes used |
| `candidates.jsonl` | `load` / `import` | Papers of the period that passed stage 1, with `found_for` |
| `pools.json` | `load` / `import` | Subsection id -> candidate ids |
| `judgments/<id>.json` | `judge` | Claude's stage-2 judgments |
| `selection.json` | `finalize` | Counts, summarized papers, category-1 lists |
| `fulltext/<paper>.txt` | `cut` | Kept sections of a full text |
| `extracted/<paper>.json` | Claude | Extracted information (extract-paper) |
| `summaries/<id>.md` | Claude | Summary bodies, one block per paper |
| `news.json` | `news` | News links of category-3 papers |
| `verified.json` | `verify` | Quotes for numbers written differently in the paper |
| `notes.json` | `note`, `load` | Notes shown at the top of the digest |
| `fallback.json` | `import` | Subsections filled by search (counts unknown) |
| `<output.filename>` | `assemble` | The digest |

`<paper>` is the paper id with `:` and `/` replaced by `_`.

## Two-stage selection
1. **Stage 1 (script).** A paper enters a subsection's pool if it comes from the theme's
   databases and categories, has none of its `exclude` keywords, and matches its keywords
   (`any`, `all`) or one of its `authors`.
2. **Stage 2 (Claude).** Claude reads the pool and judges each paper: on theme or not,
   score 1-3, kind, and field (category 3).

The count of a subsection is the number of papers judged on theme in stage 2.

## Once per digest
Summaries are served in reading order; a paper summarized once is skipped by later
subsections. Category-1 lists then hold the remaining on-theme papers, minus every
summarized paper and every paper listed earlier.

## Theme skills: inheritance
| Base skill | Theme skill |
|---|---|
| `extract-paper` | `extract-paper-<theme>` |
| `summarize-category-1` | `summarize-category-1-<theme>` |
| `summarize-category-2` | `summarize-category-2-<theme>` |
| `summarize-category-3` | `summarize-category-3-<theme>` |

- A theme skill starts with an `## Extends` section naming its base.
- To apply it: load the base, then the theme skill; apply both.
- It may add fields and rules, or tighten them. It may not drop the base's required fields
  or exceed its length limit.
- It is used when a subsection names it under `skills:`, or when its theme definition names
  it under `skills:` (the subsection wins).
- A `summarize-category-N-<theme>` skill serves category N subsections only.

## Theme definitions
A theme is a skill folder `theme-<name>/` with two files:
- `theme.yaml`: databases, categories, keywords, authors, examples, default theme skills.
  Read by the daily fetch and by `load`.
- `SKILL.md`: the targeted science and how to score it. Read by Claude in stage 2.

Create and test themes with the `define-theme` skill.
