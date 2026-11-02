---
name: tcc-init
description: First-time setup of the Town Crier. Use when the user wants to start, set up or personalise their weekly cosmology/astrophysics digest, or when no stored Town Crier configuration exists. Asks a few multiple-choice questions, stores the answers inside Claude (the scheduled task) and schedules the digest. No file to edit, no GitHub push.
---

# tcc-init: set up the Town Crier by answering questions

The user only answers questions. They never edit a file, write a prompt or push to GitHub.
`TC` is `python3 <tcc-cry skill folder>/scripts/tc.py`. Defaults: `config/default.yaml` of
the tcc-cry skill. Field reference: `config/schema.md` of the same skill.

## Where the answers are stored
The answers become a short YAML configuration (only the values that differ from the default).
It is stored **in the scheduled task's prompt** (see `tcc-schedule-cry`), because each run
starts a fresh session and reads its instructions from that prompt. Nothing is written to
the user's computer or to a repository. Scratch files in the working folder are only used
to validate the YAML.
If the session's memory is enabled, also save one line saying that the Town Crier is set up
and where its configuration lives (the scheduled task name). Never rely on memory alone.

## Before asking
1. Look for an existing Town Crier task in the user's scheduled tasks. If one exists, do not
   start over: use `tcc-configure` to change it.
2. List the themes: `ls <tcc-cry skill folder>/..` and read `title` and `description` of each
   `tcc-theme-*/theme.yaml`. Offer only these themes in the questions.
3. Check the fetched coverage (arXiv categories, journals) in `index.json` of the data branch:
   `TC resolve --config <scratch yaml> --dry-run` warns when a theme has no data.

## Questions
Use the session's question tool (`ask_user_input_v0`, or `AskUserQuestion` in Claude Code):
tappable options, at most 3 questions per call, 2 to 4 options each. One short sentence of
introduction before each call. Skip a question whose answer is already known.
Do not ask the user to type a prompt or a YAML value. Free text is only for an "Other" answer.

**Call 1: the research.**
1. *Which area is closest to your own research?* Options: the themes of the plugin
   (cosmology, galactic archaeology, galaxy formation, stellar streams). Multi-select.
   These become section 1, category 1 (deep summaries, full text read).
2. *How many deep summaries per week?* 1, 2, 3 (default), 5.
3. *Rank them by:* fit to my topic (default), or impact.

**Call 2: the surrounding field.**
1. *Which neighbouring fields should I follow more briefly?* Multi-select among the remaining
   themes. These become section 2, category 2 (short summaries, 1 paper each by default).
2. *Include "Science at large" (big results from any field, explained simply)?* Yes (default), No.
3. *Which field should it skip?* Astronomy & astrophysics (default), none, other.
   Ask only when the previous answer is yes.

**Call 3: delivery.**
1. *How often?* Every week (default), every 2 weeks, every month, every day.
2. *Which day and time?* Offer Monday 08:00 (default), Friday 17:00, Sunday evening, other.
3. *Language?* English (default), French, Italian, other.

**Only if the user mentions a topic no theme covers** (e.g. "weak lensing", "21 cm"):
say it in one sentence, then use `tcc-define-theme` in its inline form (a `themes:` block in
the configuration, no file). Use only arXiv categories that are already fetched, otherwise
the pool is empty: tell the user which categories are available.

Ask for the time zone (IANA name) only if it cannot be guessed from the conversation.

## Build, check, confirm
1. Write the YAML to a scratch file `town-crier.yaml`: title for each section, subsections with
   `theme` and `category`, `n_papers`, `rank_by`, `exclude_fields`, `period`, `schedule`,
   `output.language`. Keep comments short.
2. `TC resolve --config town-crier.yaml --dry-run`. Fix every `ERROR`.
3. Summarise it to the user in plain language (not YAML): sections, themes, number of papers,
   cadence. Ask one confirmation question (Looks good / Change something). Show the YAML
   only if they ask.
4. On confirmation, follow `tcc-schedule-cry` with this YAML.
5. Offer a first digest right now (follow `tcc-cry` with the same YAML).

## Rules
- Never ask for a GitHub account, a commit or a file path.
- Never invent a theme or an arXiv category.
- Keep the whole exchange under three question calls when the user accepts the defaults.
