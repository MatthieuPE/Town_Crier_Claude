# Extending the Town Crier

Two kinds of additions, both as skill folders in `plugins/town-crier/skills/`.

## 1. Theme definitions (finding papers)
A theme is a folder `theme-<name>/` with `theme.yaml` (databases, categories, keywords,
authors, examples) and `SKILL.md` (targeted science and scoring). It is a sub-skill of the
paper search: the daily fetch reads its databases, stage 1 applies its keywords, stage 2
reads its `SKILL.md`.

Create one with Claude: *"Define a theme for exoplanet atmospheres"* (`define-theme` skill).
It drafts the keywords, tests them on the last week of data, and gives you the two files.
Templates: `plugins/town-crier/skills/define-theme/templates/`.

Keyword syntax (title and abstract, case-insensitive):

| Write | Matches |
|---|---|
| `stellar stream` | the whole phrase, as whole words |
| `stream*` | `stream`, `streams`, `streaming` |
| `GD-1` | `GD-1`, `GD 1` (hyphens and slashes count as spaces) |

`any`: at least one must match (empty: keep every paper of the categories). `all`: every
one must match. `exclude`: none may match. `authors`: always kept.

## 2. Theme skills (extracting and summarizing)
A theme skill specializes a base skill for one theme, e.g. cosmology. It adds rules; the
base format and limits still apply.

| Base skill | Theme skill | Template |
|---|---|---|
| `extract-paper` | `extract-paper-<theme>` | `templates/extract-paper-THEME/` |
| `summarize-category-1` | `summarize-category-1-<theme>` | `templates/summarize-category-N-THEME/` |
| `summarize-category-2` | `summarize-category-2-<theme>` | `templates/summarize-category-N-THEME/` |
| `summarize-category-3` | `summarize-category-3-<theme>` | `templates/summarize-category-N-THEME/` |

Examples in the plugin: `extract-paper-cosmology` and `summarize-category-2-cosmology`
(no rules yet).

Steps:
1. Copy the template folder into `plugins/town-crier/skills/` and rename it.
2. Set `name` to the folder name; replace `N` and `THEME`.
3. Keep the `## Extends` section; write the additional rules under it.
4. Use it, either for every subsection of a theme (in `theme-<theme>/theme.yaml`):
   ```yaml
   skills:
     extract: extract-paper-exoplanets
     summarize: {2: summarize-category-2-exoplanets}
   ```
   or for one subsection (in `configs/<name>.yaml`):
   ```yaml
   - theme: exoplanets
     category: 2
     skills:
       summarize: summarize-category-2-exoplanets
   ```
5. Bump `version` in `plugin.json`, push, refresh the plugin.

Rules (checked by `tc.py resolve`): an extract skill starts with `extract-paper`; a
summarize skill for a category N subsection is `summarize-category-N` or starts with
`summarize-category-N-`.

## 3. Tests
The scripts have a test suite. From the repository root:
```
pip install pyyaml pytest
python -m pytest            # everything
python -m pytest -m fetch   # daily fetch only
python -m pytest -m run     # digest run tools only
```
