---
name: extract-paper-THEME
description: Theme skill of the Town Crier pipeline, extending extract-paper for THEME papers. Used only when a subsection or the THEME theme names it under skills.extract.
---

<!--
How to use this template:
1. Copy this folder to plugins/town-crier/skills/ and rename it extract-paper-<theme>
   (lowercase, hyphens).
2. Replace THEME everywhere, including `name` above (it must equal the folder name).
3. Write the additional fields and rules, then delete this comment.
4. Name the skill in theme-<theme>/theme.yaml (skills.extract) or in a subsection of
   your configuration (skills.extract).
-->

# Extract paper information — THEME

## Extends
Base skill: `extract-paper`.
Load and apply the base skill first. The rules below add to it.

## Additional fields
Written under `theme_fields` in `extracted/<paper>.json`. One line per field: name, what it
holds, and `unknown` when the paper does not state it.

## Additional rules
...
