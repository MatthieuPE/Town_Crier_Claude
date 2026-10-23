---
name: configure
description: Use when the user wants to set up or change their Town Crier configuration - sections, themes, summary categories, number of papers, covered period or language. Writes a configs/<name>.yaml file for the repository.
---

# Configure the Town Crier

Builds a user configuration: only the values that differ from the default.
Field reference: `config/schema.md` of the cry skill. Default: `config/default.yaml`.
`TC` is `python3 <cry skill folder>/scripts/tc.py`.

## Before asking
- List the available themes: the `theme-*` folders next to the cry skill
  (`ls <cry skill folder>/..`). Read the `title` and `description` of each `theme.yaml`.
- If the user gives an existing configuration (file or URL), start from it.

## Questions (one short message each, or grouped when the user prefers)
1. **Name.** A short name for the file, e.g. their first name: `configs/<name>.yaml`.
2. **Section 1.** Its title, and its subsections: theme and category for each. Default:
   two subsections, category 1 then category 2. Subsections are independent: any theme,
   any category.
3. **Section 2, close fields.** Which themes, each in category 2 by default.
4. **Section 3, science at large.** Keep it (theme `science-at-large`, category 3)? Which
   field to exclude, usually their own (tags in `schema.md`)?
5. **Period and language.** Default: one week, English.
6. **Numbers of papers.** Defaults: 3 (category 1), 1 (category 2), 3 (category 3).

For a theme that does not exist yet, offer the `define-theme` skill, then come back.

## Write and check
1. Write `<name>.yaml` in the working folder with only the non-default values. Keep
   comments short.
2. `TC resolve --config <name>.yaml --dry-run`. Fix every `ERROR`.
3. Show the YAML to the user and ask for approval.
4. Send the file. Tell the user to commit it to `configs/<name>.yaml` on the `main` branch.
   Runs read it from there, so later edits need no new scheduled task.

## After
Offer to deploy it as a scheduled task with the `schedule-cry` skill.
