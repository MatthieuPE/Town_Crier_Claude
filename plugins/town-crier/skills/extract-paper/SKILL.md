---
name: extract-paper
description: Step 3a of the Town Crier pipeline, and base skill of extract-paper-<theme> skills. Use to extract from a selected paper the information its summary needs, from its full text (category 1, via alphaXiv) or its abstract.
---

# Extract paper information

Base skill. Theme skills named `extract-paper-<theme>` extend it.
`TC` is `python3 <cry skill folder>/scripts/tc.py`; `RUN` is the run folder.

## Get the text
1. `TC paper --run RUN --id <paper_id>`: title, link, abstract, source.
2. **Category 1, with `full_text.source: alphaxiv`, arXiv papers only:**
   - Call alphaXiv `get_paper_content` with `url: https://arxiv.org/abs/<arXiv id>` and
     `fullText: true`.
   - If the result was saved to a file (the tool output gives its path):
     `TC cut --run RUN --paper <paper_id> --input <path>`, then read
     `RUN/fulltext/<paper>.txt`. Only the configured sections are kept, to save tokens.
   - If the result came back inline, use it directly and note it
     (`TC note --run RUN --text "<paper_id>: full text read whole"`).
   - If alphaXiv fails, is not connected, or the paper is not on arXiv: use the abstract
     and note it.
3. **Categories 2 and 3, or `full_text.source: abstract`:** use the abstract.

## Write `RUN/extracted/<paper>.json`
```json
{"paper_id": "arXiv:2610.30264", "read": "full_text | abstract",
 "sections_read": ["abstract", "methods", "results", "conclusions"],
 "fields": {"context": "...", "aims": "...", "methods": "...", "results": "...", "conclusions": "..."},
 "key_numbers": [{"quantity": "...", "value": "...", "uncertainty": "... or unknown",
                  "unit": "...", "where": "abstract | section name"}],
 "theme_fields": {},
 "notes": []}
```
`<paper>` is the paper id with `:` and `/` replaced by `_`.
- Each field: one or two sentences in your own words, or `unknown` when the text read
  does not state it.
- `key_numbers`: the main measured or derived values, copied exactly, with uncertainty and
  unit as written. Skip debris from figures and equations.
- `theme_fields`: filled by theme extraction skills only.

## Rules
- Record only what the text read states. Not memory, not other papers.
- Do not round, convert or combine numbers.
- If the full text is garbled around a number, take the number from the abstract, or
  leave it out.
- Follow `reference/accuracy.md` of the cry skill.
