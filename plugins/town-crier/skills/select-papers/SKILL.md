---
name: select-papers
description: Step 2 of the Town Crier pipeline. Use to judge each candidate of a subsection against its theme, score it by relevance or impact, and save the judgments, before the selection and counts are computed.
---

# Select papers

Stage 2: Claude judges every candidate of a subsection. The script then picks the papers,
removes duplicates across subsections and counts papers per theme.
`TC` is `python3 <cry skill folder>/scripts/tc.py`; `RUN` is the run folder.

## For each subsection, in order
1. **Theme.** Load the theme skill `town-crier:theme-<theme>`. It defines what is on theme
   and how to score.
2. **Read the candidates.** `TC load` printed which way to read each subsection.
   - Pool of up to `title_screen_above` papers (default 40), or screening `off`:
     `TC sheet --run RUN --sub <id>`.
   - Larger pool, titles first: `TC sheet --run RUN --sub <id> --titles`.
     - Plainly off theme, or not a paper (see below), from the title alone: `n`.
     - Plainly on theme but not a candidate for a summary: `y`, score 1.
     - Every other paper, and every paper that could be summarized (at least the best
       3 × `n_papers` by title): read its abstract with
       `TC sheet --run RUN --sub <id> --ids <id1>,<id2>,...`.
     - Give a score of 2 or 3 only after reading the abstract.
   - Empty pool: skip the subsection.
3. **Judge.** Write one line per candidate to `RUN/judgments_<id>.txt`:
   ```
   <paper_id> | y | <score> | <kind> | <field or -> | <short reason>
   <paper_id> | n
   ```
   - `y` if the paper fits the theme's targeted science, `n` otherwise.
   - **Not a paper:** news, editorial, commentary, perspective, policy piece, profile,
     obituary, book review, or a journal's digest page. Always `n`, whatever the theme.
     A very short abstract often signals one.
   - Score 1-3, by the subsection's `rank_by` (printed in the sheet header):
     - `relevance` (category 1): how closely the paper fits the theme. Use the theme's scale.
     - `impact` (categories 2 and 3): strength of the result. Favour a new measurement or
       detection, a high significance, a large data set, a first of its kind, a data release.
   - Kind (the sheet's flags are hints; decide from the paper):
     - `research`: a research paper;
     - `review`: a review article;
     - `proceedings`: a conference contribution;
     - `erratum`: a correction to an earlier paper;
     - `other`: a data release, catalogue, instrument, software or white paper.
   - What each category can summarize: category 1, every kind but `erratum`;
     category 2, `research` and `other`; category 3, `research` only.
   - Field: category 3 only, one tag from the sheet header.
4. **Save.** `TC judge --run RUN --sub <id> --file RUN/judgments_<id>.txt`. Fix any error
   it reports (every candidate judged exactly once).

## Then
`TC finalize --run RUN`. It prints, per subsection, the count, the papers to summarize and
whether to read their full text. Reading order decides: a paper summarized once is skipped
later; category-1 lists hold the remaining on-theme papers.

## Rules
- Judge from the title and abstract shown, not from memory of the paper or its authors.
- Do not favour famous authors or groups; judge the result.
- When unsure whether a paper is on theme, mark it `y` with score 1: the count and lists
  stay complete, and low scores are not summarized ahead of better papers.
