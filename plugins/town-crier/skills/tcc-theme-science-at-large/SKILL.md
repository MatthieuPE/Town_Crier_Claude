---
name: tcc-theme-science-at-large
description: Theme definition for the Town Crier digest - major results of the period in any scientific field. Loaded by the Town Crier pipeline to judge candidates; not for general questions.
---

# Theme: science at large

`theme.yaml` (same folder) lists the journals fetched from OpenAlex and drops the journals'
weekly digest pages in stage 1. Every other article of the period is a candidate. This text
guides stage 2.

## On theme
Research articles reporting a new result, in any field. Kind `research`.

## Off theme (`n`)
Everything else, which OpenAlex also labels as articles:
- news, editorials, commentaries, perspectives, policy forums, letters;
- profiles, obituaries, book reviews;
- reviews: this section reports new results.

A short abstract or an opinion-style title usually means one of these. Read the abstract
when unsure.

## Field tag (required)
Give each on-theme paper one tag from the list printed at the top of the review sheet.

## Scoring (impact)
- 3: a result likely to be widely reported: first observation or detection, a long-standing
  question answered, a large clinical trial outcome, a new record.
- 2: an important advance in its field.
- 1: specialised.

Judge from the title and abstract only. Do not use citation counts or press coverage to
score: a paper of the period has had no time to gather either.
