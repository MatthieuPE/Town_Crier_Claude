# Daily fetch (GitHub Action)

`town_crier_fetch` collects new papers once a day and stores them in the `data` branch.
It runs from [`.github/workflows/fetch-papers.yml`](../.github/workflows/fetch-papers.yml).

## What it fetches
The union of the `databases` of every theme definition
(`plugins/town-crier/skills/theme-*/theme.yaml`):

| Database | Query | Needs |
|---|---|---|
| arXiv | each category, first versions submitted in the lookback window | nothing |
| bioRxiv, medRxiv | first versions posted in the lookback window, per category or all | nothing |
| OpenAlex | research articles with an abstract, by journal ISSN and publication date | `OPENALEX_API_KEY` secret |

Each run re-queries a lookback window (`settings.yaml`) and stores only papers it has not
seen, under today's date (`first_seen`). A new category or journal is backfilled with
papers dated by their first version. Papers older than `retention_days` are dropped.

## Output (`data` branch)
```
index.json                    files, run days and coverage per database; compiled themes
last_run.json                 papers added and errors of the last run
<database>/<YYYY-MM-DD>.jsonl papers first seen that day
```
The branch is rewritten as a single commit each day, so it never grows a history.

## Run locally
```
pip install -r requirements.txt
OPENALEX_API_KEY=... python -m town_crier_fetch --repo-root .. --data-dir ../_data --settings settings.yaml
```
Options: `--today YYYY-MM-DD`, `--backfill-days N`, `--only arxiv,openalex`.

## References
- arXiv API User's Manual: https://info.arxiv.org/help/api/user-manual.html
- arXiv API Terms of Use: https://info.arxiv.org/help/api/tou.html
- bioRxiv API: https://api.biorxiv.org/
- OpenAlex works API: https://developers.openalex.org/api-reference/works
