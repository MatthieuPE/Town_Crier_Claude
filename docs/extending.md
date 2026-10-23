# Adding a theme skill

A theme skill specializes a base skill for one theme, e.g. cosmology.
It adds rules to the base skill; it never replaces it.

## Base skills that can be extended
| Base skill | Theme skill name | Template |
|---|---|---|
| `extract-paper` | `extract-paper-<theme>` | `templates/extract-paper-THEME/` |
| `summarize-category-1` | `summarize-category-1-<theme>` | `templates/summarize-category-N-THEME/` |
| `summarize-category-2` | `summarize-category-2-<theme>` | `templates/summarize-category-N-THEME/` |
| `summarize-category-3` | `summarize-category-3-<theme>` | `templates/summarize-category-N-THEME/` |

Examples already in the plugin: `extract-paper-cosmology`, `summarize-category-2-cosmology`.

## Steps
1. Copy the template folder into `plugins/town-crier/skills/`.
2. Rename the folder, e.g. `summarize-category-2-exoplanets`. Lowercase and hyphens only.
3. In `SKILL.md`, set `name` to the folder name. Replace `N` and `THEME`.
4. Keep the `## Extends` section. Write the additional rules under it.
5. Name the skill in the configuration of the subsections that need it:
   ```yaml
   - theme: "Exoplanets"
     category: 2
     skills:
       summarize: summarize-category-2-exoplanets
   ```
6. Bump `version` in `plugins/town-crier/.claude-plugin/plugin.json`, push, and refresh the plugin.

## Inheritance rules
Full rules: `plugins/town-crier/skills/cry/reference/pipeline.md`.
- At run time, Claude loads the base skill, then the theme skill, and applies both.
- A theme skill may add fields and rules, or tighten them.
- It may not drop the base's required fields or exceed its length limit.
- A `summarize-category-N-<theme>` skill only serves category N subsections.
