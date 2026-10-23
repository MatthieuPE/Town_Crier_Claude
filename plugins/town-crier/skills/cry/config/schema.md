# Configuration reference

A configuration is a YAML file. Start from `default.yaml`.
A user configuration is merged over the default, key by key.
A `sections` list given by the user replaces the default list entirely.
Any value in `<angle brackets>` is a placeholder and must be filled in.

## `period`
| Field | Values | Default | Meaning |
|---|---|---|---|
| `length` | integer ≥ 1 | `1` | Number of units covered. |
| `unit` | `day`, `week`, `month` | `week` | Unit of the period. |
| `end` | `today` or `YYYY-MM-DD` | `today` | Last day covered (included). |

The period starts `length` × `unit` before `end`. Months are calendar months.
Label used in the output: "today", "this week", "this month", or "in the last N weeks".

## `output`
| Field | Default | Meaning |
|---|---|---|
| `title` | `The Town Crier` | Title of the output file. |
| `language` | `English` | Language of the whole output. |
| `filename` | `town-crier_{start}_{end}.md` | Output file name. `{start}` and `{end}` are dates. |
| `delivery` | `file` | TODO: `file` (sent to the user) or `artifact` (shareable page). |

## `schedule`
Used only by the `schedule-cry` skill.
| Field | Default | Meaning |
|---|---|---|
| `weekday` | `monday` | Run day when `period.unit` is `week`. |
| `day_of_month` | `1` | Run day when `period.unit` is `month`. |
| `time` | `08:00` | Local run time. |
| `timezone` | `null` | IANA name (e.g. `Europe/Paris`). Asked when null. |

## `defaults`
Per-category defaults, used when a subsection does not set the value.
| Field | Meaning |
|---|---|
| `count_method` | `on_theme`: count the papers of the period judged on the subsection's theme. `categories`: count all new papers in the subsection's arXiv categories. |
| `category_N.n_papers` | Number of papers summarized in the subsection. |
| `category_N.rank_by` | `relevance` (fit to the theme) or `impact` (strongest result of the period). |
| `category_N.count` | Show the number of papers released in the period. |

Defaults: category 1 → 3 papers, by relevance, counted. Category 2 → 1 paper, by impact, counted. Category 3 → 3 papers, by impact, not counted.

## `sections`
A list. Each section has a `title` and a list of `subsections`.
Sections and subsections are numbered in order (1, 1.1, 1.2, 2, 2.1…).

### Subsection fields
| Field | Required | Meaning |
|---|---|---|
| `theme` | yes | Subject of the subsection, in a few words. |
| `category` | yes | Summary level: `1`, `2` or `3` (see below). |
| `description` | no | One or two sentences on what counts as relevant. Used for selection. |
| `keywords` | no | Terms that help find and judge papers. |
| `sources.arxiv` | no | arXiv categories to search, e.g. `[astro-ph.GA]`. |
| `sources.journals` | no | Journals to search. |
| `sources.news` | no | News outlets used to find major results. |
| `n_papers`, `rank_by`, `count` | no | Override the category defaults. |
| `skills.extract` | no | Theme skill extending `extract-paper`. |
| `skills.summarize` | no | Theme skill extending `summarize-category-<category>`. |

### Summary categories
| Category | Purpose | Summary |
|---|---|---|
| 1 | Specific research | Bullets: Context, Aims, Methods, Results, Conclusions. |
| 2 | Opening on the same field | At most 10 sentences, mostly context, methods and conclusions, with the field's vocabulary. |
| 3 | Opening on other fields | At most 10 sentences, understandable by a high-school science student. |

Each category can be used by any number of subsections.

## Default structure
1. **Main theme**
   1. specific research topic — category 1
   2. sub-domain of the field — category 2
2. **Next door**: several close fields — category 2 each
3. **Science at large**: main results of the period, any field — category 3
