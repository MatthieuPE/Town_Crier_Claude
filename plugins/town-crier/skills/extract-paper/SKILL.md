---
name: extract-paper
description: Step 3a of the Town Crier pipeline, and base skill for theme extraction skills (extract-paper-<theme>). Use to pull from a selected paper the information its summary needs, such as context, aims, methods, results, conclusions and key numbers.
---

# Extract paper information

Base skill. Theme skills named `extract-paper-<theme>` extend it.

## Inputs
- One selected paper: its record from `candidates.jsonl`.
- The category of the subsection it serves.

## Output
- `extracted/<paper_id>.json` (format: the `cry` skill's `reference/pipeline.md`).
- Required fields: `context`, `aims`, `methods`, `results`, `conclusions`, `key_numbers`.
- `read`: `abstract` or `full_text`, whichever was used.

## Instructions
TODO: detailed instructions.

Points to cover:
- When the abstract is enough, and when to read the full text.
- How to record numbers, with their uncertainties and units.

## Rules
- Record only what the paper states.
- Leave a field empty rather than guess it.
