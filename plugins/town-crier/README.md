# Town Crier

A configurable literature digest for researchers, over a tunable period (one week by default).
A daily GitHub Action collects new papers. Each digest run selects them by fit to your themes
or by impact, summarizes them at three depth levels, checks every number against the papers,
and assembles them into the sections you configured.

Install in Claude Code: `/plugin install town-crier --marketplace MatthieuPE/Town_Crier_Claude`.
In claude.ai: add the marketplace `https://github.com/MatthieuPE/Town_Crier_Claude` under
Customize → Plugins, then install **town-crier**.

- Run it: ask Claude *"Run the Town Crier with configs/<name>.yaml"* (`cry` skill).
- Set it up: *"Set up my Town Crier"* (`configure`), *"Define a theme"* (`define-theme`).
- Automate it: *"Schedule my Town Crier"* (`schedule-cry`).

Documentation: the repository [README](../../README.md) and [setup guide](../../docs/setup.md).
