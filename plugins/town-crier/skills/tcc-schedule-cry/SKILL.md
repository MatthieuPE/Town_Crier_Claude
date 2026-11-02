---
name: tcc-schedule-cry
description: Use to create or update the Claude scheduled task that runs the Town Crier digest (every day, week, two weeks or month). The task's prompt carries the user's configuration, so nothing is stored in a repository.
---

# Schedule the Town Crier

Creates or updates one scheduled task. Each run starts a fresh session with no memory of
this one, so the task prompt is self-contained and **contains the configuration YAML**.
That prompt is where the user's configuration is stored. `TC` is
`python3 <tcc-cry skill folder>/scripts/tc.py`.

## Steps
1. **Configuration.** The YAML from `tcc-init` or `tcc-configure`, in `town-crier.yaml`.
   Check it: `TC resolve --config town-crier.yaml --dry-run --anchor calendar`.
2. **Time zone.** From `schedule.timezone`; ask when it is null (IANA name, e.g. `Europe/Paris`).
3. **Cadence** from `period`:

   | Period | Runs | Cron (local time) |
   |---|---|---|
   | 1 day | every day | `M H * * *` |
   | 1 week | every week on `schedule.weekday` | `M H * * D` (the week ends the day before: a Sunday run covers Sunday–Saturday) |
   | 2 weeks | 1st and 15th of each month (half-months) | `M H 1,15 * *` |
   | N months (N = 1, 2, 3, 4, 6 or 12) | on `schedule.day_of_month`, every N months | `M H day */N *` (`*` when N = 1) |

   `H:M` is `schedule.time`; `D` is the weekday number (Monday = 1). Prefix the expression
   with `CRON_TZ=<time zone> `. Follow the scheduling tool's own guidance on the minute.
   Other periods cannot be scheduled exactly: offer the nearest supported one.
4. **Existing task.** List the user's scheduled tasks. If one already runs the Town Crier,
   **update it** (new prompt, new cron) instead of creating a second one.
5. **Create or update** the task with the session's scheduling tool:
   - name: `Town Crier — <cadence>`, e.g. `Town Crier — weekly`;
   - prompt: the template below, with the YAML pasted in;
   - notifications from `schedule.notifications`: `none` means no notification channel at all;
   - it runs in the cloud: it does not need the user's computer.
   If the session has no scheduling tool, say so in one sentence, give the digest now with
   `tcc-cry`, and explain that scheduling needs Claude Cowork or Claude Code.
6. **Report** in two lines: name, cadence, time zone, and the approval setting the task got.
   If its runs will ask for approval, say that runs stall on unanswered prompts, and that
   the task can be switched to "Automatically approve" in its settings.
7. **Offer a test:** a one-off run of the same prompt 10 minutes later, left unattended.
   Afterwards, check the digest's notes: full text used or abstracts only, any approval stall.

## Task prompt template
````
Run the Town Crier literature digest.
Load the `town-crier:tcc-cry` skill and follow it.
Configuration (this is the user's stored Town Crier configuration; write it to
`town-crier.yaml` and use it):
```yaml
<the configuration YAML>
```
Period anchor: calendar (use `--anchor calendar`).
Time zone: <IANA time zone> (use `--run-date "$(TZ=<IANA time zone> date +%F)"`).
This is an unattended run: do not ask questions; record assumptions and failures as notes.
When done, send the digest file.
````
The YAML is also what `tcc-configure` reads back and edits later.

## Before the first scheduled run
- The daily "Fetch papers" job of the repository owner has run at least once (the `data`
  branch exists). Users do nothing for this.
- The alphaXiv connector is connected, and its `get_paper_content` and `discover_papers`
  tools are set to "Always allow". Otherwise category 1 falls back to abstracts.
