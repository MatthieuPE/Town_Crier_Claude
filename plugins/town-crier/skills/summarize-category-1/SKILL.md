---
name: summarize-category-1
description: Step 3b of the Town Crier pipeline for category 1 subsections (specific research), and base skill of summarize-category-1-<theme> skills. Use to summarize papers in five bullets - Context, Aims, Methods, Results, Conclusions.
---

# Summarize — category 1 (specific research)

Base skill. Theme skills named `summarize-category-1-<theme>` extend it.
For the papers closest to the reader's own research. The reader is an expert.

## Input
The subsection's papers listed by `TC finalize`, best fit first, and their
`RUN/extracted/<paper>.json`.

## Output
`RUN/summaries/<subsection id>.md`: one block per paper, in the order of `finalize`.
Write the body only; `TC assemble` adds the title, link and authors.
```markdown
<!-- paper: arXiv:2610.30264 -->
- **Context:** ...
- **Aims:** ...
- **Methods:** ...
- **Results:** ...
- **Conclusions:** ...
```
The bullet labels follow `output.language`:
- English: Context, Aims, Methods, Results, Conclusions.
- French: Contexte, Objectifs, Méthodes, Résultats, Conclusions.
- Italian: Contesto, Obiettivi, Metodi, Risultati, Conclusioni.

These are the five headings of the structured abstracts of *Astronomy & Astrophysics*.

## How to write
- One or two sentences per bullet.
- Use the field's vocabulary; do not explain standard terms.
- **Methods:** data, sample, model or technique; name surveys, instruments and codes.
- **Results:** the main results, with their numbers, uncertainties and units, exactly as in
  the paper.
- **Conclusions:** what the authors conclude, with their own level of certainty.
- When the text read does not state a bullet's content, write `unknown` (in the output
  language).
- If only the abstract could be read, write the bullets from the abstract alone.

## Rules
- All five bullets, in this order, none empty.
- No links and no citations of other works.
- Numbers only from the paper. `TC check` verifies them.
- Paraphrase; do not copy the paper's sentences.
- Follow `reference/accuracy.md` of the cry skill.
