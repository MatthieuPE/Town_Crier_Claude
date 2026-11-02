---
name: define-theme
description: Use when the user wants to create or tune a Town Crier theme - the science it targets, its databases and categories, keywords, authors and example papers - so that the pipeline finds the right papers efficiently. Writes a theme-<name> folder for the plugin.
---

# Define a theme

A theme is a sub-skill of the paper search. It is a folder `theme-<name>/` with:
- `theme.yaml`: databases, categories, keywords, authors, examples. The daily fetch reads
  its databases; stage 1 applies its keywords and authors to every new paper.
- `SKILL.md`: the targeted science and how to score papers. Claude reads it in stage 2.

Templates: `templates/theme.yaml` and `templates/theme-SKILL.md.txt` in this folder.
`TC` is `python3 <cry skill folder>/scripts/tc.py`.

## Steps
1. **Ask.** Name (lowercase words with hyphens, e.g. `exoplanet-atmospheres`), title, and
   the science targeted, in the user's words. Ask for example papers if they have some.
2. **Databases.** Propose the smallest set that covers the theme:
   - arXiv categories for physics, astronomy, mathematics, computer science, statistics and
     quantitative biology (e.g. `astro-ph.GA`, `astro-ph.CO`, `stat.ME`).
   - bioRxiv or medRxiv subject categories for biology and medicine (or `all`).
   - OpenAlex journals, given by ISSN, for published papers.
3. **Keywords.** Draft them from the description:
   - `any`: papers must match at least one. Leave empty to keep every paper of the
     categories (then stage 2 does all the filtering).
   - `all`: papers must match every one. Rarely needed.
   - `exclude`: papers matching one are dropped. Use for known false positives.
   - Matching is on title and abstract, whole words, case-insensitive; `*` at the end
     matches any ending (`stream*`); hyphens count as spaces (`GD-1` matches `GD 1`).
   - `authors`: names or collaborations whose papers are always kept.
4. **Examples.** If the user has none, find 3 to 5 typical papers with alphaXiv
   `discover_papers` and ask the user to confirm them. Record their arXiv ids in `examples`.
   Never write an id that a tool did not return.
5. **Test.** Write the draft to `theme-<name>/theme.yaml`, then:
   - `TC validate-theme --theme theme-<name>/theme.yaml`, and fix any error;
   - `TC theme-test --theme theme-<name>/theme.yaml --days 7`.

   Show the user the count and the sample titles. Too many off-theme papers: add keywords
   to `exclude` or narrow `any`. Too few: widen `any`. Repeat up to three times.
   A `NOTE ... not fetched yet` means a category is new: the test can only run after the
   next daily fetch. Then use alphaXiv `discover_papers` on the last week as a rough check.
6. **Write `SKILL.md`** from the template: targeted science, what is on and off theme, and
   a scoring scale for relevance and for impact.
7. **Deliver.** Send both files. Tell the user to add the folder to
   `plugins/town-crier/skills/`, bump `version` in `plugin.json`, push, and refresh the
   plugin. New categories are fetched from the next daily run; the GitHub Action can also
   be run by hand, with `backfill_days` set to the length of their period.

## Rules
- The `name` field must equal the folder name without `theme-`.
- Keep keywords specific: each one should rarely match an off-theme paper.
- Draft keywords are a starting point; the test decides.
