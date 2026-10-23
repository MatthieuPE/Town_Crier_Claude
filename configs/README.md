# Configurations

One file per user: `configs/<name>.yaml`. Scheduled runs read it from the `main` branch
at each run, so editing and pushing it changes the next digest; no new scheduled task is
needed.

- Start from [`example-stellar-streams.yaml`](example-stellar-streams.yaml), or ask Claude
  *"Set up my Town Crier"* (`configure` skill).
- Only write the values that differ from the
  [default configuration](../plugins/town-crier/skills/cry/config/default.yaml).
- Field reference: [`schema.md`](../plugins/town-crier/skills/cry/config/schema.md).
- The repository is public: do not put anything private in these files.
