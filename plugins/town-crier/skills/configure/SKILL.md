---
name: configure
description: Use when the user wants to set up or change their Town Crier configuration, such as themes, sections, subsections, summary categories, number of papers or covered period. Writes a configuration file.
---

# Configure the Town Crier

Builds a configuration with the user, starting from the `cry` skill's `config/default.yaml`.
Field reference: the `cry` skill's `config/schema.md`.

## Inputs
- Optional: an existing configuration to edit.

## Output
- A YAML file, `town-crier.yaml`, sent to the user.
- Only the values that differ from the default.

## Questions to cover
1. Main theme: title of section 1.
2. Specific research topic (subsection 1.1, category 1) and the sub-domain of the field (subsection 1.2, category 2).
3. Close fields for section 2: how many, and which.
4. For each subsection: category, number of papers, arXiv categories or other sources.
5. Covered period: length and unit.
6. Output language.

TODO: detailed instructions (order of questions, defaults to propose, validation).

## After writing
Offer to deploy it as a scheduled task with the `schedule-cry` skill.
