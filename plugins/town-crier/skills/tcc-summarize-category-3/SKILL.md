---
name: tcc-summarize-category-3
description: Step 3b of the Town Crier pipeline for category 3 subsections (opening on other fields), and base skill of tcc-summarize-category-3-<theme> skills. Use to explain one major result from any scientific field in simple words, for a high-school or first-year university student, with a news link when one exists.
---

# Summarize — category 3 (opening on other fields)

Base skill. Theme skills named `tcc-summarize-category-3-<theme>` extend it.
One major result of the period, from any field, explained simply. The reader is a
high-school student or a first-year university student in science. The other strong results are only listed (by
`TC assemble`, with their field); they get no summary.

## Input
The subsection's paper listed by `TC finalize` (one by default) and its
`RUN/extracted/<paper>.json` (from the abstract). The field tag comes from the judgment;
`TC assemble` shows it. Apply the `writing guidance` that `finalize` prints, if any.

## News link
Look for one news article about the summarized paper with WebSearch (its title, or its key
result and journal). Keep an article only if it clearly covers this paper and comes from
a recognised outlet (a science magazine, a journal's news section, a major newspaper or a
university press office). Then:
`TC news --run RUN --paper <paper_id> --url <article URL> --outlet "<outlet name>"`.
If none is found, add nothing. The article is a link for the reader, never a source of
facts or numbers.

## Output
`RUN/summaries/<subsection id>.md`: one block for the summarized paper. Body only.
```markdown
<!-- paper: doi:10.1038/s41586-026-01234-5 -->
One paragraph of 5 to 8 short sentences.
```

## How to write
- **Start from everyday life:** the question, in words a student uses. "Why do some people
  lose their hearing?", not "Otoferlin deficiency in sensorineural deafness".
- **Short sentences:** one idea each, about 20 words at most.
- **No jargon.** Replace technical words with plain ones. If one word cannot be avoided,
  explain it in the same sentence.
- **One image** helps: a comparison with something familiar, when it is accurate.
- Then what was done, what was found, and why it matters, in that order.
- **One or two numbers at most,** only if they help, exactly as in the paper.
- **No exaggeration:** keep the paper's own level of certainty ("in mice", "in 11 patients",
  "a first step").

## Rules
- No links in the body and no citations of other works.
- Numbers only from the paper. `TC check` verifies them.
- Paraphrase; do not copy the abstract or the news article.
- Follow `reference/accuracy.md` of the tcc-cry skill.
