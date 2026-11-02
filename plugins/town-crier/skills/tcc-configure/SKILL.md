---
name: tcc-configure
description: Use when the user wants to change their existing Town Crier setup in conversation - fields, themes, number of papers, day or time, language. Reads the stored configuration, applies the change and saves it back inside Claude. No file, no GitHub push. First-time setup is tcc-init.
---

# Change the Town Crier by talking

The configuration lives in the prompt of the user's Town Crier scheduled task (see `tcc-init`).
`TC` is `python3 <tcc-cry skill folder>/scripts/tc.py`. Field reference: `config/schema.md`
of the tcc-cry skill.

## Steps
1. **Read it.** Find the Town Crier task among the user's scheduled tasks and extract the YAML
   from its prompt. If there is none, run `tcc-init` instead.
2. **Understand the change** from what the user says ("drop stellar streams", "give me 5 deep
   papers", "send it on Fridays", "in French"). If a choice is needed, use the question tool
   (`ask_user_input_v0` / `AskUserQuestion`) with 2-4 options rather than a free-text question.
   One question at a time.
3. **Apply it** to a scratch copy `town-crier.yaml`, keeping only non-default values.
   Themes: those of the `tcc-theme-*` folders next to the tcc-cry skill, or an inline `themes:`
   block built with `tcc-define-theme`.
4. **Check.** `TC resolve --config town-crier.yaml --dry-run`. Fix every `ERROR`.
5. **Confirm** in plain language what changes (before / after), one confirmation question.
6. **Save.** Update the scheduled task with `tcc-schedule-cry` (it replaces the YAML in the
   prompt and the cron if cadence changed). The next run uses it.

Never ask the user to edit or commit a file.
