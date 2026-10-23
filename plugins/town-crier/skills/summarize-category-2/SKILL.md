---
name: summarize-category-2
description: Step 3b of the Town Crier pipeline for category 2 subsections (opening on the same field), and base skill for summarize-category-2-<theme> skills. Use to summarize a paper in at most 10 sentences, with the field's vocabulary.
---

# Summarize — category 2 (opening on the same field)

Base skill. Theme skills named `summarize-category-2-<theme>` extend it.
For the most impactful papers of a sub-domain or a close field.

## Inputs
- The subsection's `extracted/<paper_id>.json` files, in rank order (strongest result first).

## Output
- `summaries/<subsection_id>.md`: one entry per paper, in rank order.

## Entry format
```markdown
#### [<Paper title>](<link>)
<At most 10 sentences.>
```

## Instructions
TODO: detailed instructions.

Points to cover:
- Mostly context, methods and conclusions.
- Use the vocabulary of the field; the reader is a researcher.

## Rules
- At most 10 sentences.
- Paraphrase. Do not copy the abstract.
- Never add a claim the paper does not make.
