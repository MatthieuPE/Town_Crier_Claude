---
name: summarize-category-3
description: Step 3b of the Town Crier pipeline for category 3 subsections (opening on other fields), and base skill of summarize-category-3-<theme> skills. Use to summarize a major result from any scientific field in at most 10 sentences, for a high-school science student, with a news link when one exists.
---

# Summarize — category 3 (opening on other fields)

Base skill. Theme skills named `summarize-category-3-<theme>` extend it.
For the major results of the period in any field. The reader is a high-school student
who studies science.

## Input
The subsection's papers listed by `TC finalize`, strongest first, and their
`RUN/extracted/<paper>.json` (from the abstract). The field tag comes from the judgment;
`TC assemble` shows it.

## News link
For each paper, look for one news article about it with WebSearch (its title, or its key
result and journal). Keep an article only if it clearly covers this paper and comes from
a recognised outlet (a science magazine, a journal's news section, a major newspaper or a
university press office). Then:
`TC news --run RUN --paper <paper_id> --url <article URL> --outlet "<outlet name>"`.
If none is found, add nothing. The article is a link for the reader, never a source of
facts or numbers.

## Output
`RUN/summaries/<subsection id>.md`: one block per paper, in the order of `finalize`.
Write the body only.
```markdown
<!-- paper: doi:10.1038/s41586-026-01234-5 -->
One paragraph of at most 10 sentences.
```

## How to write
- At most 10 sentences.
- What question was asked, what was done, what was found, why it matters.
- Plain words. Avoid jargon; when a technical term is needed, explain it in the same sentence.
- Few numbers: only those that help understanding, exactly as in the paper.
- No exaggeration: keep the paper's own level of certainty.

## Rules
- No links in the body and no citations of other works.
- Numbers only from the paper. `TC check` verifies them.
- Paraphrase; do not copy the abstract or the news article.
- Follow `reference/accuracy.md` of the cry skill.
