# Accuracy rules

These rules bind every step of a Town Crier run: selection, extraction, summaries.

## Never invent
- No paper, title, author, link, journal or date that is not in the run's data.
- No number, result or claim that the paper does not state.
- No citation of other works. Summaries cite nothing; the heading already links the paper.

## Write "unknown"
When the paper does not state something the format asks for (for example its aims, or
an uncertainty), write `unknown` (French: `inconnu`; Italian: `sconosciuto`). An honest
"unknown" is better than a plausible guess.

## Sources
- The only source of a summary is the paper itself: its title, its abstract, and the
  full-text sections read during extraction.
- Not memory, not other papers, not news articles. News articles are linked for
  category 3, never used as a source of facts or numbers.
- If only the abstract was read, anything not in the abstract is `unknown`.

## Numbers
- Copy numbers exactly as the paper gives them, with their uncertainties and units.
- Do not round, convert, combine or compute new numbers.
- `tc.py check` flags every number not found in the paper's text. Fix each flag by
  correcting the number from the paper, or by writing `unknown`. Use `tc.py verify` only
  when the number is in the paper but written differently there; quote the paper exactly.

## Wording
- Paraphrase. Do not copy sentences from the abstract or the paper.
- Keep the paper's own hedging: "suggest" stays "suggest", not "prove".

## When something fails
Say so in a note (`tc.py note`) and in the summary if needed ("full text unavailable;
summary from the abstract"). Never hide a failure behind plausible text.
