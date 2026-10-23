---
name: schedule-cry
description: Use when the user wants the Town Crier digest to run automatically - every week, every two weeks, every month or every day. Creates a Claude scheduled task that reads their configuration from the repository.
---

# Schedule the Town Crier

Creates a scheduled task. Each run starts a fresh session with no memory of this one, so
the task's prompt is self-contained and points to the configuration in the repository.
`TC` is `python3 <cry skill folder>/scripts/tc.py`.

## Steps
1. **Configuration.** Its raw URL on the `main` branch:
   `https://raw.githubusercontent.com/<repository>/main/configs/<name>.yaml`. If it is not
   committed yet, run the `configure` skill first. Check it:
   `TC resolve --config <URL> --dry-run --anchor calendar`.
2. **Time zone.** From `schedule.timezone`; ask when it is null (IANA name, e.g. `Europe/Paris`).
3. **Cadence** from `period`:

   | Period | Runs | Cron (local time) |
   |---|---|---|
   | 1 day | every day | `M H * * *` |
   | 1 week | every week on `schedule.weekday` | `M H * * D` |
   | 2 weeks | 1st and 15th of each month (half-months) | `M H 1,15 * *` |
   | N months (N = 1, 2, 3, 4, 6 or 12) | on `schedule.day_of_month`, every N months | `M H day */N *` (`*` when N = 1) |

   `H:M` is `schedule.time`; `D` is the weekday number (Monday = 1). Prefix the expression
   with `CRON_TZ=<time zone> `. Follow the scheduling tool's own guidance on the minute.
   Other periods cannot be scheduled exactly: offer the nearest supported one.
4. **Existing tasks.** List the user's scheduled tasks. If one already runs the Town Crier
   with this configuration, update it instead of creating a second one.
5. **Create** the task with the session's scheduling tool:
   - name: `Town Crier — <cadence>`, e.g. `Town Crier — weekly`;
   - prompt: the template below;
   - notifications from `schedule.notifications`: `none` means no notification channel at all
     (pass an empty setting); `push`, `email` or both otherwise;
   - it runs in the cloud: it does not need the user's computer.
6. **Report** in two lines: name, cadence, time zone, and the approval setting the task got.
   If its runs will ask for approval, say that runs stall on unanswered prompts, and that
   the task can be switched to "Automatically approve" in its settings.
7. **Offer a test:** a one-off run of the same prompt 10 minutes later, left unattended.
   Afterwards, check the digest's notes: full text used or abstracts only, any approval stall.

## Task prompt template
```
Run the Town Crier literature digest.
Load the `town-crier:cry` skill and follow it.
Configuration: <raw URL of configs/<name>.yaml>
Period anchor: calendar (use `--anchor calendar`).
Time zone: <IANA time zone> (use `--run-date "$(TZ=<IANA time zone> date +%F)"`).
This is an unattended run: do not ask questions; record assumptions and failures as notes.
When done, send the digest file.
```

## Before the first scheduled run
- The GitHub Action "Fetch papers" has run at least once (data branch exists).
- The alphaXiv connector is connected, and its `get_paper_content` and `discover_papers`
  tools are set to "Always allow". Otherwise category 1 falls back to abstracts.
