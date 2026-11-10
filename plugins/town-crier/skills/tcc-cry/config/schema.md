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
| `anchor` | `rolling`, `calendar` | `rolling` | Rolling: `length` units ending on `end`. Calendar: one-week windows ending on `week_end`, half-months (1st–14th, 15th–end) for 2 weeks, calendar months; always ending before the run day. Scheduled tasks use `calendar`. |
| `week_end` | weekday name or `null` | `null` | Last day of a calendar week. `null`: the day before `schedule.weekday` (Sunday runs cover Sunday–Saturday; Monday runs, Monday–Sunday). |

## `output`
| Field | Default | Meaning |
|---|---|---|
| `title` | `The Town Crier` | Digest title. |
| `language` | `English` | Language of the digest. English, French and Italian have built-in headings. |
| `filename` | `town-crier_{start}_{end}.md` | File name; `{start}`, `{end}` are dates. |
| `delivery` | `file` | Markdown file sent in the conversation. |
| `contents` | `true` | Table of contents under the header. |

## `schedule` (used by `tcc-schedule-cry`)
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
| `title_screen_above` | `40` | Pools larger than this are screened on titles before reading abstracts. Lower = fewer tokens; abstracts are always read before a paper can be summarized. `off`: every abstract is read (most precise ranking, most tokens). A subsection can set its own value. |

## `full_text` (category 1)
| Field | Default | Meaning |
|---|---|---|
| `source` | `alphaxiv` | `alphaxiv`: full text from the alphaXiv connector (arXiv papers). `abstract`: abstract only. `html`: planned, not available yet. |
| `sections` | `[abstract, methods, results, conclusions]` | Sections kept, among `abstract`, `introduction`, `methods`, `results`, `discussion`, `conclusions`. |

## `defaults` (per category; any subsection can override)
| Field | Cat. 1 | Cat. 2 | Cat. 3 | Meaning |
|---|---|---|---|---|
| `n_papers` | 3 | 1 | 1 | Most papers summarized. |
| `min_score` | 3 | 1 | 1 | Lowest score a summarized paper can have (scores 1-3 from stage 2). With 3, only close fits are summarized, so a week can have none. |
| `rank_by` | `relevance` | `impact` | `impact` | Fit to the theme, or strength of the result. |
| `count` | `true` | `true` | `false` | Show the number of papers of the period on the theme. |
| `list_others` | `true` | `false` | `true` | List the best other papers on the theme, without summary. |
| `list_max` | 5 | — | 5 | Most papers listed, best first; `null` = all. |
| `one_per_field` | — | — | `true` | At most one paper per field. |
| `exclude_fields` | — | — | `[]` | Fields to skip (tags below). |

## `themes`
Themes written in the configuration, by name. They override plugin themes of the same name.
| Field | Meaning |
|---|---|
| `title`, `description` | Name and one-paragraph scope. |
| `databases` | `arxiv` (categories), `biorxiv` / `medrxiv` (categories or `all`), `openalex` (`journals` with ISSNs). The daily fetch reads them from `configs/*.yaml`. |
| `keywords` | `any`, `all`, `exclude`, `exclude_titles` (stage 1, see `docs/extending.md`). |
| `authors`, `examples` | Always-kept authors; typical papers (`arXiv:...`). |
| `guidance` | Free text for stage 2: on and off theme, scoring. Printed on each review sheet. |
| `summary_guidance` | Free text for the summaries: what to explain simply for this reader (e.g. chemistry for a dynamicist). Printed by `finalize`. |
| `skills` | Optional theme skills (`extract`, `summarize: {N: ...}`). |

## `sections`
A list of sections, each with a `title`, an optional `category` and `subsections`.
Numbered in order (1, 1.1, ...). A subsection without a `category` takes the section's, else
the first subsection's.

| Subsection field | Required | Meaning |
|---|---|---|
| `theme` | yes | Theme name: a `tcc-theme-<name>` skill of the plugin. |
| `category` | no | Summary level: 1, 2 or 3. Default: the section's `category`, else the first subsection's. |
| `title` | no | Heading; default: the theme's title. |
| `n_papers`, `min_score`, `rank_by`, `count`, `list_others`, `list_max`, `one_per_field`, `exclude_fields` | no | Override the category defaults. |
| `title_screen_above` | no | Overrides `selection.title_screen_above`, e.g. `off` for one subsection. |
| `guidance` | no | Extra judging rules for this subsection only, printed on its review sheet. |
| `summary_guidance` | no | Writing rules for this subsection's summaries; replaces the theme's. |
| `full_text` | no | Overrides `full_text` (category 1). |
| `skills.extract` | no | Theme skill extending `tcc-extract-paper`. |
| `skills.summarize` | no | Theme skill extending `tcc-summarize-category-<category>`. |

## Summary categories
| Category | For | Summary |
|---|---|---|
| 1 | Specific research | 0 to 3 close fits, in bullets: Context, Aims, Methods, Results, Conclusions. Full text read. The 5 closest other papers listed. |
| 2 | Opening on the same field | At most 10 sentences for a graduate-level reader with a rough view of the sub-domain: about half explaining the specific physics and the open question, then what was found. |
| 3 | Opening on other fields | One paper, 5 to 8 short sentences in plain words, for a high-school or first-year university student. Field tag and news link. Up to 5 other results listed. Research papers only. |

## Field tags (category 3)
Astronomy & astrophysics · Physics · Chemistry & materials · Biology · Medicine & health ·
Earth & environment · Mathematics & computing · Engineering & technology ·
Social & behavioural sciences
