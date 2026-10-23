---
name: summarize-category-N-THEME
description: Theme skill of the Town Crier pipeline, extending summarize-category-N for THEME papers. Used only for category N subsections whose configuration or theme names it under skills.summarize.
---

<!--
How to use this template:
1. Copy this folder to plugins/town-crier/skills/ and rename it
   summarize-category-<N>-<theme> (N = 1, 2 or 3; theme in lowercase with hyphens).
2. Replace N and THEME everywhere, including `name` above (it must equal the folder name).
3. Write the additional rules, then delete this comment.
4. Name the skill in theme-<theme>/theme.yaml (skills.summarize.<N>) or in a category N
   subsection of your configuration (skills.summarize).
-->

# Summarize — category N — THEME

## Extends
Base skill: `summarize-category-N`.
Load and apply the base skill first. The rules below add to it.
The base format and length limit still apply.

## Additional rules
...
