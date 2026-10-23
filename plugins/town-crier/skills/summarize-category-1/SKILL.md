---
name: summarize-category-1
description: Step 3b of the Town Crier pipeline for category 1 subsections (specific research), and base skill for summarize-category-1-<theme> skills. Use to summarize papers in five bullets - Context, Aims, Methods, Results, Conclusions.
---

# Summarize — category 1 (specific research)

Base skill. Theme skills named `summarize-category-1-<theme>` extend it.
For the papers closest to the user's own research.

## Inputs
- The subsection's `extracted/<paper_id>.json` files, in rank order (most relevant first).

## Output
- `summaries/<subsection_id>.md`: one entry per paper, in rank order.

## Entry format
```markdown
#### [<Paper title>](<link>)
- **Context:** …
- **Aims:** …
- **Methods:** …
- **Results:** …
- **Conclusions:** …
```
Same five headings as the structured abstracts of *Astronomy & Astrophysics*.

## Instructions
TODO: detailed instructions (length of each bullet, numbers, vocabulary).

## Rules
- All five bullets are required.
- Paraphrase. Do not copy the abstract.
- Never add a claim the paper does not make.
