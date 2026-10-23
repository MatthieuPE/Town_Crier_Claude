---
name: schedule-cry
description: Use when the user wants the Town Crier digest to run automatically, every week, every month or on another cadence. Creates a Claude scheduled task from their configuration.
---

# Schedule the Town Crier

Deploys the digest as a Claude scheduled task.
Each run starts a fresh session with no memory of this one, so the task's prompt must be self-contained.

## Inputs
- The user's configuration. If there is none, run the `configure` skill first.
- `schedule` block of the configuration: run day, time, time zone.

## Steps
1. Get the configuration. Ask for the time zone if `schedule.timezone` is null.
2. Derive the cadence from `period` (table below).
3. Build the task prompt from the template below, with the full configuration inline.
4. Create the scheduled task with the session's scheduling tool.
5. Tell the user the name, the cadence and the approval setting the task received.

TODO: detailed instructions.

## Cadence
| `period.unit` | Runs | Default |
|---|---|---|
| `day` | every day | at `schedule.time` |
| `week` | every week | on `schedule.weekday`, at `schedule.time` |
| `month` | every month | on `schedule.day_of_month`, at `schedule.time` |

TODO: periods longer than one unit (e.g. 2 weeks).

## Task prompt template
````
Run the Town Crier literature digest.
Load the `town-crier:cry` skill and follow it with the configuration below.
This is an unattended run: do not ask questions; state any assumption at the top of the output.
The covered period ends on the day of this run.

```yaml
<full configuration>
```
````

## Rules
- Name the task "Town Crier — <period>", e.g. "Town Crier — weekly".
- Never create a second task for the same configuration: check existing scheduled tasks first.
