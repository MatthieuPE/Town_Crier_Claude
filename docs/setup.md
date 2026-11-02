# Setup guide

Steps 1–3 are done once, by the repository owner. Steps 4–6 are done by each user.

## 1. Push the repository
Keep the repository **public**: Claude reads the `data` branch and the configurations
through `raw.githubusercontent.com`, without credentials.

Three entries start with a dot and are hidden by Finder and Windows Explorer: `.github/`
(the workflows), `.claude-plugin/` (the marketplace file) and `.gitignore`. Check that they
are on GitHub: without `.github/` there is no Actions workflow, and without
`.claude-plugin/` the plugin cannot be installed.

## 2. Enable the daily fetch
1. Open **Settings → Secrets and variables → Actions** in the repository.
2. Add the secret `OPENALEX_API_KEY`: a free key from https://openalex.org/settings/api.
   Without it, the "Science at large" section falls back to web search and gets no list
   from the journals.
3. Optional: add the variable `CONTACT_EMAIL` (sent to the APIs as a polite contact).
4. Open **Actions → Fetch papers → Run workflow**. Set `backfill_days` to the length of your
   longest period (e.g. `35` for monthly digests). This creates the `data` branch.
5. Check the run log. A red run lists the failed queries; the data that did work is still
   published. After that, the workflow runs every day at 04:17 UTC.

GitHub disables scheduled workflows of public repositories after 60 days without
repository activity. If that happens, re-enable the workflow in the Actions tab.

## 3. Check the result
The `data` branch holds `index.json` and one folder per database. `index.json` lists the
days fetched and, under `coverage`, the categories and journals covered.

## 4. Install the plugin (each user)
- **claude.ai or Claude Desktop:** Customize → Plugins → Personal plugins → **+** →
  *Add marketplace* → *Add from a repository* → `https://github.com/MatthieuPE/Town_Crier_Claude`.
  Then install **town-crier**.
- **Claude Code:** `/plugin marketplace add MatthieuPE/Town_Crier_Claude`, then
  `/plugin install town-crier@town-crier`.

## 5. Connect alphaXiv (each user)
Category 1 reads full texts through the alphaXiv connector. Connect it, then set its tools
`get_paper_content` and `discover_papers` to **Always allow** (Customize → Connectors →
alphaXiv → Tool permissions). Without it, category 1 is summarized from abstracts.

## 6. Set up and schedule (each user)
1. Ask Claude *"Set up my Town Crier"* (`tcc-init`). Answer the questions; nothing to edit
   or push. Your configuration is stored in the scheduled task Claude creates.
2. Accept the first digest it offers, and read it.
3. Accept the one-off test run it offers, and check the digest: the notes at the top say whether full texts were read and whether anything
   failed. If runs wait for approvals, switch the scheduled task to **Automatically approve**
   in its settings.

## Updating
- **Configuration:** tell Claude what to change (`tcc-configure`); it updates the scheduled
  task, and the next run uses it.
- **Skills or themes:** push the change, bump `version` in
  `plugins/town-crier/.claude-plugin/plugin.json`, and refresh the plugin in Claude.
- **New theme categories** are fetched from the next daily run. To backfill them at once,
  run the workflow by hand with `backfill_days`.
