---
name: select-papers
description: Step 2 of the Town Crier pipeline. Use to pick, for each subsection, the papers that best fit its theme or have the strongest impact, and to count the papers released on that theme during the period.
---

# Select papers

Chooses the papers each subsection will summarize, and counts the papers of the period on each theme.

## Inputs
- `candidates.jsonl`.
- `config.resolved.yaml`: for each subsection, `theme`, `description`, `keywords`, `category`, `n_papers`, `rank_by`, `count`, and `defaults.count_method`.

## Output
- `selection.json` (format: the `cry` skill's `reference/pipeline.md`).

## Instructions
TODO: detailed instructions.

Points to cover:
- **On-theme test:** judge each candidate against the subsection's theme and description, from the title and abstract.
- **Count** (when `count` is true):
  - `on_theme`: number of candidates of the period judged on the theme.
  - `categories`: number of new papers of the period in the subsection's arXiv categories.
- **Ranking:**
  - `relevance`: closest fit to the theme first (default for category 1).
  - `impact`: strongest result of the period first (default for categories 2 and 3).
- Keep the top `n_papers`, with a one-line reason for each.
- Serve subsections in reading order. Skip papers already kept by an earlier subsection.
- If no paper qualifies, keep none.
