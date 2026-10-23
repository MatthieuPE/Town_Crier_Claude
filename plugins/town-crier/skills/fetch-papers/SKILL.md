---
name: fetch-papers
description: Step 1 of the Town Crier pipeline. Use to collect the papers released during a covered period from the sources of each subsection (arXiv categories, journals, news). Does not judge relevance.
---

# Fetch papers

Builds the pool of candidate papers for the covered period.

## Inputs
- `config.resolved.yaml`: the period and, for each subsection, its `sources` and `keywords`.

## Output
- `candidates.jsonl`: one paper per line (format: the `cry` skill's `reference/pipeline.md`).
- A short fetch log: sources queried, counts, failures.

## Instructions
TODO: detailed instructions.

Points to cover:
- arXiv: query each category of `sources.arxiv` over the period, with the arXiv API. Keep papers whose first version (v1) is in the period. Merge cross-listed papers.
- Journals and news (`sources.journals`, `sources.news`): find the major results of the period. Link to the paper itself (DOI) whenever possible, not only to the news article.
- Fill `found_for` with the subsections whose sources returned the paper.
- Respect the arXiv API terms of use: https://info.arxiv.org/help/api/tou.html

## Rules
- Do not filter or summarize here.
- Never invent a paper or a link.
