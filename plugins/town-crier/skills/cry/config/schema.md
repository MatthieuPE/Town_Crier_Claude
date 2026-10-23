# Configuration reference

A configuration is a YAML file. It only needs the values that differ from `default.yaml`.
It is merged over the default key by key; a `sections` list replaces the default list
entirely. Values in `<angle brackets>` are placeholders that must be filled in.
Check a configuration with `tc.py resolve --config <file> --dry-run`.

## `data`
| Field | Default | Meaning |
|---|---|---|
| `repository` | `MatthieuPE/Town_Crier_Claude` | GitHub repository holding the data branch. |
| `branch` | `data` | Branch written by the daily fetch. |

## `period`
| Field | Values | Default | Meaning |
|---|---|---|---|
| `length` | integer ≥ 1 | `1` | Number of units covered. |
| `unit` | `day`, `week`, `month` | `week` | Unit. |
| `end` | `yesterday`, `today`, `YYYY-MM-DD` | `yesterday` | Last covered day (rolling anchor). |
| `anchor` | `rolling`, `calendar` | `rolling` | Rolling: `length` units ending on `end`. Calendar: Monday–Sunday weeks, half-months (1st–14th, 15th–end) for 2 weeks, calendar months; always ending before the run day. Scheduled tasks use `calendar`. |

## `output`
| Field | Default | Meaning |
|---|---|---|
| `title` | `The Town Crier` | Digest title. |
| `language` | `English` | Language of the digest. English, French and Italian have built-in headings. |
| `filename` | `town-crier_{start}_{end}.md` | File name; `{start}`, `{end}` are dates. |
| `delivery` | `file` | Markdown file sent in the conversation. |
| `contents` | `true` | Table of contents under the header. |

## `schedule` (used by `schedule-cry`)
| Field | Default | Meaning |
|---|---|---|
| `weekday` | `monday` | Run day of weekly digests. |
| `day_of_month` | `1` | Run day of monthly digests. |
| `time` | `08:00` | Local run time. |
| `timezone` | `null` | IANA name, e.g. `Europe/Paris`. Asked when null. |
| `notifications` | `none` | `none`, `push`, `email` or `push+email`, when a run finishes. |

## `selection`
| Field | Default | Meaning |
|---|---|---|
| `title_screen_above` | `120` | Pools larger than this are screened on titles before reading abstracts. |

## `full_text` (category 1)
| Field | Default | Meaning |
|---|---|---|
| `source` | `alphaxiv` | `alphaxiv`: full text from the alphaXiv connector (arXiv papers). `abstract`: abstract only. `html`: planned, not available yet. |
| `sections` | `[abstract, methods, results, conclusions]` | Sections kept, among `abstract`, `introduction`, `methods`, `results`, `discussion`, `conclusions`. |

## `defaults` (per category; any subsection can override)
| Field | Cat. 1 | Cat. 2 | Cat. 3 | Meaning |
|---|---|---|---|---|
| `n_papers` | 3 | 1 | 3 | Papers summarized. |
| `rank_by` | `relevance` | `impact` | `impact` | Fit to the theme, or strength of the result. |
| `count` | `true` | `true` | `false` | Show the number of papers of the period on the theme. |
| `list_others` | `true` | — | — | List the other new papers on the theme. |
| `one_per_field` | — | — | `true` | At most one paper per field. |
| `exclude_fields` | — | — | `[]` | Fields to skip (tags below). |

## `sections`
A list of sections, each with a `title` and `subsections`. Numbered in order (1, 1.1, ...).

| Subsection field | Required | Meaning |
|---|---|---|
| `theme` | yes | Theme name: a `theme-<name>` skill of the plugin. |
| `category` | yes | Summary level: 1, 2 or 3. |
| `title` | no | Heading; default: the theme's title. |
| `n_papers`, `rank_by`, `count`, `list_others`, `one_per_field`, `exclude_fields` | no | Override the category defaults. |
| `full_text` | no | Overrides `full_text` (category 1). |
| `skills.extract` | no | Theme skill extending `extract-paper`. |
| `skills.summarize` | no | Theme skill extending `summarize-category-<category>`. |

## Summary categories
| Category | For | Summary |
|---|---|---|
| 1 | Specific research | Bullets: Context, Aims, Methods, Results, Conclusions. Full text read. Other new papers listed. |
| 2 | Opening on the same field | At most 10 sentences, mostly context, methods and conclusions, in the field's vocabulary. |
| 3 | Opening on other fields | At most 10 sentences, for a high-school science student. Field tag and news link. |

## Field tags (category 3)
Astronomy & astrophysics · Physics · Chemistry & materials · Biology · Medicine & health ·
Earth & environment · Mathematics & computing · Engineering & technology ·
Social & behavioural sciences
