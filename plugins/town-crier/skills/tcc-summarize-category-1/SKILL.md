---
name: tcc-summarize-category-1
description: Step 3b of the Town Crier pipeline for category 1 subsections (specific research), and base skill of tcc-summarize-category-1-<theme> skills. Use to summarize papers in five bullets - Context, Aims, Methods, Results, Conclusions.
---

# Summarize — category 1 (specific research)

Base skill. Theme skills named `tcc-summarize-category-1-<theme>` extend it.
For the papers closest to the reader's own research. The reader is an expert of the theme.
Every category-1 subsection uses the same five bullets, whatever its theme.

## Input
The subsection's papers listed by `TC finalize`, best fit first, and their
`RUN/extracted/<paper>.json`. `finalize` also prints the subsection's
`writing guidance`, if any: apply it.

Only close fits are summarized: from 0 to `n_papers` (default 3) per subsection.
When `finalize` says "nothing to summarize", write no summary file for that subsection.
The digest then says that no paper fit closely and lists the closest ones.

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
- Use the theme's vocabulary; do not explain the theme's standard terms.
- **Outside the reader's expertise.** The writing guidance names fields the reader does not
  know well (for example chemical abundances for a dynamicist). When such a field is central
  to the paper, explain it in plain words: what the quantity measures and why it matters
  here. Standard notation of the field (such as [Fe/H]) can stay.
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
- Follow `reference/accuracy.md` of the tcc-cry skill.
