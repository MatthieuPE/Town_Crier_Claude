---
name: assemble-digest
description: Step 4 of the Town Crier pipeline. Use to assemble the digest file from the summaries, counts and lists, and to run the accuracy and format checks until they pass.
---

# Assemble the digest

`TC` is `python3 <cry skill folder>/scripts/tc.py`; `RUN` is the run folder.

## Steps
1. `TC assemble --run RUN`. It builds the digest from the data:
   - header with the period, notes, and a table of contents;
   - one heading per section and subsection, with the count of papers on the theme
     (categories 1 and 2 by default);
   - for each summarized paper: linked title, first author, journal and, for category 3,
     field tag and news link, then the body from `summaries/`;
   - for category 1: the list of the other new papers on the theme;
   - "No new paper this period." for empty subsections.
2. `TC check --run RUN`.
3. Fix every `ERROR`, then repeat steps 1 and 2 until there are none:
   - **Number not in the paper:** reread the paper's text (`RUN/fulltext/<paper>.txt` or the
     abstract from `TC paper`). Correct the number, or write `unknown`. If the number is in
     the paper but written differently (for example `10^4` and `10 000`), record it:
     `TC verify --run RUN --paper <id> --number <n> --quote "<exact words of the paper>"`.
   - **Missing or empty bullet:** add it; write `unknown` if the paper does not say.
   - **Citation or link in a summary:** remove it.
   - **Summary missing, or for a paper not selected:** fix `summaries/<id>.md`.
4. Review every `WARNING` (for example, more than 10 sentences) and fix what is real.

## Rules
- Never edit the digest file by hand; edit the summaries and assemble again.
- Never remove a correct statement just to silence a check; correct the statement instead.
- The digest file is the run's deliverable; it is sent by the `cry` skill.
