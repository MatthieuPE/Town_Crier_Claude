---
name: summarize-category-3
description: Step 3b of the Town Crier pipeline for category 3 subsections (opening on other fields), and base skill for summarize-category-3-<theme> skills. Use to summarize a paper from any scientific field in at most 10 sentences, for a high-school science student.
---

# Summarize — category 3 (opening on other fields)

Base skill. Theme skills named `summarize-category-3-<theme>` extend it.
For major results of the period in any scientific field.

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
- Understandable by a high-school student who studies science.
- Explain any technical term, or avoid it.

## Rules
- At most 10 sentences.
- Paraphrase. Do not copy the abstract or the news article.
- Never add a claim the paper does not make.
