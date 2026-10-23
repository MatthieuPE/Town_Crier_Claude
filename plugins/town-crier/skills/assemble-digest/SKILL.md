---
name: assemble-digest
description: Step 4 of the Town Crier pipeline. Use to assemble the subsection summaries and paper counts into the final output file, following the configured sections.
---

# Assemble the digest

Builds the output file from the summaries, in the order of the configuration.

## Inputs
- `config.resolved.yaml`: title, language, period, sections and subsections.
- `selection.json`: the count of each subsection.
- `summaries/<subsection_id>.md`.

## Output
- The output file, named after `output.filename`, following `template.md` in this folder.

## Instructions
TODO: detailed instructions.

Points to cover:
- One heading per section, one per subsection, numbered as in the configuration.
- Under each counted subsection (categories 1 and 2 by default), the number of papers released on its theme during the period.
- A subsection with no paper says so in one line.
- Unattended runs: assumptions and missing steps listed at the top.

## Final checks
- Every link points to a paper in `candidates.jsonl`.
- No paper appears twice.
- Every summary respects its category's format and length.
