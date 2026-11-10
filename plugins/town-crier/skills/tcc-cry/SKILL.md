---
name: tcc-cry
description: Entry point of the Town Crier literature digest. Use when the user asks for the Town Crier, their literature digest, or the latest papers of a period (this week, this month), including from a scheduled task. Runs the whole pipeline from a configuration.
---

# Town Crier — cry

Produces one digest for one covered period: new papers on the user's themes, selected,
summarized at three depth levels, and assembled into the configured sections.

## Setup
- **Scripts.** `scripts/tc.py` in this skill's folder; written `TC` below
  (`python3 <this folder>/scripts/tc.py`). If the folder is not known:
  `find / -name tc.py -path "*tcc-cry/scripts*" 2>/dev/null | head -1`.
- **PyYAML.** If `python3 -c "import yaml"` fails: `pip install --break-system-packages pyyaml`.
- **Accuracy.** Read `reference/accuracy.md` now. Its rules bind every step.
- **Progress.** Create a task list: resolve, load, select, extract, summarize, assemble and check, deliver.

## Configuration
Use the first one available:
1. YAML pasted in the request (scheduled runs carry the user's configuration in their prompt):
   write it to `town-crier.yaml` and use it.
2. A configuration URL or file named in the request.
3. Interactive run with nothing given: look for the user's Town Crier scheduled task and
   use the YAML in its prompt. The user never has to name it.
4. Nothing stored: run the `tcc-init` skill (questions, no file to edit), then continue.
The default configuration has placeholders and is never run as is.

## Steps
1. **Resolve.** `TC resolve --config <source>`. Add `--anchor calendar` and
   `--run-date "$(TZ=<time zone> date +%F)"` when the request gives them (scheduled tasks
   do). Note the run folder it prints: `RUN` below.
   - Exit 2 (errors): with the user present, show the errors and fix them with the
     `tcc-configure` skill (it updates the stored configuration). Unattended: stop and send a message listing them.
2. **Load.** `TC load --run RUN`. It reads the period's papers and builds one pool of
   candidates per subsection (stage 1: databases and keywords of each theme).
   - Exit 3 (data unavailable): follow the fallback of the `tcc-fetch-papers` skill.
3. **Select.** For each subsection, in order: load its theme skill (`town-crier:tcc-theme-<theme>`),
   then follow the `tcc-select-papers` skill. Then run `TC finalize --run RUN`.
4. **Extract.** For each paper `finalize` lists: follow the subsection's extract skill.
5. **Summarize.** For each subsection with papers to summarize: follow the subsection's
   summarize skill, with the writing guidance `finalize` prints. Write
   `RUN/summaries/<subsection id>.md`. Skip subsections where `finalize` says "nothing to
   summarize": the digest states it and shows the list.
6. **Assemble and check.** Follow the `tcc-assemble-digest` skill until `TC check` reports 0 errors.
7. **Deliver.** Send the digest file with SendUserFile (status `proactive` when unattended).
   Reply in two or three lines: the period, the number of papers summarized, any notes.
   Keep the notes few: only what changes how the reader should trust a section.

## Skills per subsection
`TC resolve` prints the extract and summarize skills of each subsection. A theme skill,
such as `tcc-summarize-category-2-cosmology`, extends its base skill: load the base skill
first, then the theme skill, and apply both. The theme rules add to the base; the base
format and length limits always hold. Rules: `reference/pipeline.md`.

## Unattended runs
A scheduled run has no one to answer questions.
- Never ask. Use the configured values or the defaults.
- Record each assumption or failure: `TC note --run RUN --section <id> --text "..."`, with
  the section (`2`) or subsection (`2.1`) it concerns. The note appears under that heading.
  Without `--section`, it goes to a short Notes list at the end. Nothing goes at the top.
- If one paper or subsection fails, note it and carry on with the rest.

## Rules
- Never invent a paper, author, link, number or citation. Write "unknown" instead of guessing.
- A paper appears at most once in a digest. `finalize` enforces it.
- Never edit `candidates.jsonl`, `pools.json`, `selection.json` or the digest by hand.
- Write summaries in `output.language`.
