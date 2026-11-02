# Town Crier

A configurable literature digest for researchers, over a tunable period (one week by default).
A daily GitHub Action collects new papers. Each digest run selects them by fit to your themes
or by impact, summarizes them at three depth levels, checks every number against the papers,
and assembles them into the sections you configured.

Install in Claude Code: `/plugin install town-crier --marketplace MatthieuPE/Town_Crier_Claude`.
In claude.ai: add the marketplace `https://github.com/MatthieuPE/Town_Crier_Claude` under
Customize → Plugins, then install **town-crier**.

- Set it up: *"Set up my Town Crier"* (`tcc-init`). Claude asks a few questions, stores your
  configuration in a scheduled task and schedules the digest. No file, no GitHub push.
- Change it: *"Send it on Fridays"*, *"add galaxy formation"* (`tcc-configure`).
- Run it now: *"Run my Town Crier"* (`tcc-cry`). New topic: *"Define a theme"* (`tcc-define-theme`).

Documentation: the repository [README](../../README.md) and [setup guide](../../docs/setup.md).
