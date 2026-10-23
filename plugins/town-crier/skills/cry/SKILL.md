---
name: cry
description: Entry point of the Town Crier literature digest. Use when the user asks for the Town Crier, their literature digest, or the latest papers of a period (this week, this month), including from a scheduled task. Runs the whole pipeline from a configuration.
---

# Town Crier — cry

Produces one digest for one covered period.
Runs the pipeline steps in order, from a configuration.

## 1. Resolve the configuration
Use the first available:
1. A configuration given in the request: inline YAML, or an attached or linked file.
2. `config/default.yaml` in this folder.

Merge the user configuration over the default (rules: `config/schema.md`).
Then:
- Compute the period: start, end, label.
- Number sections and subsections (1, 1.1, 1.2, 2…).
- Fill missing subsection values from `defaults` for its category.
- Check the theme skills named under `skills:` (rules: `reference/pipeline.md`).
- If a placeholder `<…>` remains: ask the user when present. In an unattended run, stop and report what is missing.
- Write `config.resolved.yaml` in the run folder.

TODO: detailed instructions.

## 2. Run the pipeline
| Step | Skill |
|---|---|
| 1. Look for papers in the period | `fetch-papers` |
| 2. Select the relevant ones and count per subsection | `select-papers` |
| 3a. Extract paper information | `extract-paper`, or the subsection's `skills.extract` |
| 3b. Summarize at the subsection's category | `summarize-category-<N>`, or the subsection's `skills.summarize` |
| 4. Assemble the output file | `assemble-digest` |

Inputs, outputs and the run folder: `reference/pipeline.md`.

TODO: detailed instructions.

## 3. Deliver
TODO: delivery according to `output.delivery`.

## Unattended runs
A scheduled run has no one to answer questions.
- Never ask. Use the configured values or the defaults.
- List any assumption at the top of the output.
- If a step fails, carry on and state in the output what is missing.

## Rules
- Never invent a paper, an author, a link or a result.
- A paper appears at most once in the output.
