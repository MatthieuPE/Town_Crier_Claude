---
name: summarize-category-2
description: Step 3b of the Town Crier pipeline for category 2 subsections (opening on the same field), and base skill of summarize-category-2-<theme> skills. Use to summarize the strongest paper of a sub-domain in at most 10 sentences, with the field's vocabulary.
---

# Summarize — category 2 (opening on the same field)

Base skill. Theme skills named `summarize-category-2-<theme>` extend it.
For the most impactful result of the period in a sub-domain or a close field. The reader
is a researcher of the same broad field, not a specialist of this sub-domain.

## Input
The subsection's papers listed by `TC finalize`, strongest first, and their
`RUN/extracted/<paper>.json` (from the abstract).

## Output
`RUN/summaries/<subsection id>.md`: one block per paper, in the order of `finalize`.
Write the body only; `TC assemble` adds the title, link and authors.
```markdown
<!-- paper: arXiv:2610.30264 -->
One paragraph of at most 10 sentences.
```

## How to write
- At most 10 sentences; aim for 5 to 8.
- Mostly the context (why it matters), the methods (data and approach) and the conclusions.
- Give the key result with its number when the abstract states it.
- Use the field's vocabulary. Define only terms specific to the sub-domain.
- One paragraph, no bullets.

## Rules
- No links and no citations of other works.
- Numbers only from the paper. `TC check` verifies them.
- If the abstract does not say something, do not supply it; say less, or write `unknown`.
- Paraphrase; do not copy the abstract.
- Follow `reference/accuracy.md` of the cry skill.
