---
name: tcc-summarize-category-2
description: Step 3b of the Town Crier pipeline for category 2 subsections (opening on the same field), and base skill of tcc-summarize-category-2-<theme> skills. Use to summarize the strongest paper of a sub-domain in at most 10 sentences, for a graduate-level reader, mostly explaining the physics and the open question it addresses.
---

# Summarize — category 2 (opening on the same field)

Base skill. Theme skills named `tcc-summarize-category-2-<theme>` extend it.
For the most impactful result of the period in a close field. The reader is at graduate
level, with only a rough view of this sub-domain: they know what the CMB, gravitational
waves or dark energy are, but not the current research on them, its specific effects and
observables, or its open debates.

## Input
The subsection's papers listed by `TC finalize`, strongest first, and their
`RUN/extracted/<paper>.json` (from the abstract). `finalize` also prints the subsection's
`writing guidance`, if any: apply it.

## Output
`RUN/summaries/<subsection id>.md`: one block per paper, in the order of `finalize`.
Write the body only; `TC assemble` adds the title, link and authors.
```markdown
<!-- paper: arXiv:2610.30264 -->
One paragraph of at most 10 sentences.
```

## How to write
The text explains what is being discussed. The result comes last and briefly.
Same length as before (at most 10 sentences, aim for 6 to 9); spend it on the context.
1. **The physics (about half of the text).** Name the specific effect, observable or model
   the paper is about, and explain it: what it is, what produces it, how it is measured.
   Example: for a paper on cosmic birefringence, explain that it is a rotation of the CMB
   polarization direction on its way to us, which some new fields that violate parity
   would produce, and that it shows up as a correlation between E and B modes.
2. **The open question (1 or 2 sentences).** Why it matters now: the tension, the earlier
   hint, the missing measurement.
3. **What was done (1 or 2 sentences).** Data and approach, in plain terms.
4. **What was found and what it changes (1 or 2 sentences).** The key result with its
   number when the abstract states it, and the authors' own level of certainty.

- Do not explain the broad field (what the CMB, a galaxy or a gravitational wave is).
- Do explain every term specific to the sub-domain, the first time it appears.
- The context is general physics knowledge: state it without numbers, and without
  claims about other papers. Numbers only from the paper's result.
- One paragraph, no bullets.

## Rules
- No links and no citations of other works.
- Numbers only from the paper. `TC check` verifies them.
- If the abstract does not say something about the result, do not supply it; say less, or
  write `unknown`.
- Paraphrase; do not copy the abstract.
- Follow `reference/accuracy.md` of the tcc-cry skill.
