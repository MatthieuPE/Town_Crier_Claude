---
name: fetch-papers
description: Step 1 of the Town Crier pipeline. Use to load the papers released during the covered period and build each subsection's candidate pool from its theme definition, or, when the paper data is unavailable, to find papers by search instead.
---

# Fetch papers

Builds the candidate pool of every subsection for the covered period.
`TC` is `python3 <cry skill folder>/scripts/tc.py`; `RUN` is the run folder.

## Where papers come from
A GitHub Action fetches new papers every day from arXiv, bioRxiv/medRxiv and OpenAlex,
for the databases declared by all theme definitions. It stores them in the repository's
`data` branch, each under the day it was first seen. Nothing here queries arXiv directly.

## Normal case
1. `TC load --run RUN`.
2. Read its output: candidates per subsection, and whether to review titles first.
3. Read the `NOTE` lines. They are already in the digest notes. Mention any serious one
   (data not updated, a category not fetched yet) to the user when present.

Stage 1 keeps a paper in a subsection's pool when it comes from the theme's databases and
categories, has none of its `exclude` keywords, and matches its keywords or authors. Each
theme definition is a sub-skill of this step: `theme-<name>/theme.yaml` holds those
filters, and `define-theme` creates or tunes them.

## Fallback: data unavailable
Use it when `TC load` exits with code 3, or when a subsection's pool is empty because its
database is not fetched (for example, no OpenAlex key for science at large).
1. Note why: `TC note --run RUN --text "..."`.
2. For each affected subsection, find papers of the period by search:
   - arXiv themes: alphaXiv `discover_papers`, with the theme's main keywords (without `*`),
     `published_after` and `published_before` set to the period, `prioritize: recency`.
   - Science at large: WebSearch for the main research results of the period in Nature,
     Science, Cell, PNAS, Physical Review Letters and NEJM. Keep the paper itself (DOI link),
     not the news article.
3. Write the papers found to `RUN/found.jsonl`, one JSON object per line:
   `{"paper_id": "arXiv:2610.12345" or "doi:10....", "title": ..., "url": ...,
   "found_for": ["1.1"], "abstract": ..., "authors": [...], "published": "YYYY-MM-DD"}`.
   Use only titles, links and abstracts returned by the tools. If an abstract is missing,
   leave it empty: extraction reads the paper.
4. `TC import --run RUN --file RUN/found.jsonl --reason "<why>"`.

Imported subsections show "unknown" as their count, and their lists may be incomplete.
The digest says so in its notes.

## Rules
- Never add a paper that no tool returned.
- Do not edit `candidates.jsonl` or `pools.json` by hand.
