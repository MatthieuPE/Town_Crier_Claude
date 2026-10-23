"""Command line: fetch new papers into the data folder."""

import argparse
import datetime as dt
import logging
import os
import time
from pathlib import Path

import yaml

from . import arxiv, biorxiv, http, openalex, store, themes

LOG = logging.getLogger("town_crier_fetch")

DEFAULT_SETTINGS = {
    "retention_days": 100,
    "lookback_days": {"arxiv": 14, "biorxiv": 3, "medrxiv": 3, "openalex": 21},
    "arxiv": {"page_size": 500, "delay_seconds": 3.0},
    "biorxiv": {"delay_seconds": 1.0},
    "openalex": {"per_page": 100, "delay_seconds": 1.0, "max_pages": 50},
    "themes_glob": "plugins/town-crier/skills/theme-*/theme.yaml",
}


def load_settings(path=None):
    """Fetch settings, file values over defaults.

    Parameters
    ----------
    path : str or Path, optional
        YAML settings file.

    Returns
    -------
    dict
        Settings.
    """
    settings = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT_SETTINGS.items()}
    if path and Path(path).exists():
        user = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        for key, value in user.items():
            if isinstance(value, dict) and isinstance(settings.get(key), dict):
                settings[key].update(value)  # merge one level
            else:
                settings[key] = value
    return settings


def fetch_scope(db, scope, start, end, settings, *, api_key, getter, sleep):
    """Records of one query: one arXiv category, one preprint category, or all journals.

    Parameters
    ----------
    db : str
        Database name.
    scope : str or list of str
        Category, ``all``, or list of ISSNs for OpenAlex.
    start, end : datetime.date
        Date range, inclusive.
    settings : dict
        Fetch settings.
    api_key : str or None
        OpenAlex key.
    getter, sleep : callable
        Network and wait functions.

    Returns
    -------
    list of dict
        Records.
    """
    if db == "arxiv":
        cfg = settings["arxiv"]
        return arxiv.fetch_category(scope, start, end, page_size=cfg["page_size"],
                                    delay=cfg["delay_seconds"], getter=getter, sleep=sleep)
    if db in ("biorxiv", "medrxiv"):
        return biorxiv.fetch_server(db, start, end, category=None if scope == "all" else scope,
                                    delay=settings["biorxiv"]["delay_seconds"], getter=getter,
                                    sleep=sleep)
    if db == "openalex":
        cfg = settings["openalex"]
        return openalex.fetch_journals(scope, start, end, api_key=api_key, per_page=cfg["per_page"],
                                       delay=cfg["delay_seconds"], max_pages=cfg["max_pages"],
                                       getter=getter, sleep=sleep)
    raise ValueError(f"unknown database {db}")


def update_database(db, scopes, data_dir, index, today, settings, *, backfill_days=0,
                    api_key=None, getter=http.get, sleep=time.sleep):
    """Fetch one database, store new papers, update its index entry.

    Parameters
    ----------
    db : str
        Database name.
    scopes : list of str
        Scopes to query (see ``themes.build_plan``).
    data_dir : Path
        Data folder.
    index : dict
        Index, updated in place.
    today : datetime.date
        Day of this run.
    settings : dict
        Fetch settings.
    backfill_days : int
        When > 0, look back this many days and date papers by their first
        version.
    api_key : str, optional
        OpenAlex key.
    getter, sleep : callable
        Network and wait functions.

    Returns
    -------
    added : int
        New papers stored.
    errors : list of str
        Failed queries.
    """
    entry = index["databases"].get(db) or {}
    coverage = dict(entry.get("coverage") or {})
    lookback = backfill_days or settings["lookback_days"][db]
    start = today - dt.timedelta(days=lookback)
    records = store.load_records(data_dir, db)
    added, errors, done = 0, [], set()
    queries = [(s, [s]) for s in sorted(scopes, key=lambda s: s not in coverage)]  # covered first
    if db == "openalex":
        queries = [("journals", list(scopes))]  # one query for all journals
    for i, (key, query_scopes) in enumerate(queries):
        if i:
            sleep(settings["arxiv"]["delay_seconds"] if db == "arxiv" else 1.0)
        try:
            recs = fetch_scope(db, query_scopes if db == "openalex" else key, start, today, settings,
                               api_key=api_key, getter=getter, sleep=sleep)
        except (http.FetchError, ValueError) as exc:
            errors.append(f"{db} {key}: {exc}")
            LOG.error("%s %s failed: %s", db, key, exc)
            continue
        for rec in recs:
            if db == "openalex":
                new_scope = not any(issn in coverage for issn in rec.get("issn") or [])
            else:
                new_scope = key not in coverage
            added += store.merge(records, [rec], today=today, backfill=bool(backfill_days) or new_scope)
        done.update(query_scopes)
    for scope in done:
        coverage.setdefault(scope, start.isoformat())  # start of coverage
    coverage = {s: d for s, d in coverage.items() if s in scopes}
    records = store.prune(records, today, settings["retention_days"])
    days = store.write_records(data_dir, db, records, today)
    store.update_database_entry(index, db, days=days, today=today, coverage=coverage,
                                retention_days=settings["retention_days"])
    LOG.info("%s: %d new papers, %d stored", db, added, len(records))
    return added, errors


def parse_args(argv=None):
    """Command-line arguments."""
    parser = argparse.ArgumentParser(prog="town_crier_fetch", description=__doc__)
    parser.add_argument("--repo-root", default=".", help="repository root (theme files)")
    parser.add_argument("--data-dir", required=True, help="data folder (data branch checkout)")
    parser.add_argument("--settings", default=None, help="settings YAML")
    parser.add_argument("--today", default=None, help="run day YYYY-MM-DD (default: today UTC)")
    parser.add_argument("--backfill-days", type=int, default=0,
                        help="look back N days and date papers by first version")
    parser.add_argument("--only", default=None, help="comma-separated databases to fetch")
    return parser.parse_args(argv)


def main(argv=None, *, getter=None, sleep=None):
    """Run one fetch.

    Parameters
    ----------
    argv : list of str, optional
        Arguments.
    getter, sleep : callable, optional
        Replace network access and waits (tests).

    Returns
    -------
    int
        Exit code: 0. Query failures are listed in ``last_run.json`` so the
        data is still published; the workflow fails afterwards.
    """
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = load_settings(args.settings)
    sleep = sleep or time.sleep
    getter = getter or (lambda url: http.get(url, sleep=sleep))
    if os.environ.get("CONTACT_EMAIL"):
        http.USER_AGENT += f"; mailto:{os.environ['CONTACT_EMAIL']}"  # polite contact
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    theme_defs, errors = themes.load_themes(themes.find_theme_files(args.repo_root, settings["themes_glob"]))
    if not theme_defs:
        errors.append("no valid theme definition found")
    plan = themes.build_plan(theme_defs)
    only = set(args.only.split(",")) if args.only else None
    index = store.load_index(data_dir)
    added = {}
    for db, scopes in plan.items():
        if only and db not in only:
            continue
        added[db], errs = update_database(db, scopes, data_dir, index, today, settings,
                                          backfill_days=args.backfill_days,
                                          api_key=os.environ.get("OPENALEX_API_KEY"),
                                          getter=getter, sleep=sleep)
        errors.extend(errs)
    index["themes"] = theme_defs
    index["plan"] = plan
    index["updated"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    index["last_run_day"] = today.isoformat()
    store.write_json(data_dir, store.INDEX_FILE, index)
    store.write_json(data_dir, store.LAST_RUN_FILE,
                     {"date": today.isoformat(), "added": added, "errors": errors})
    LOG.info("done: %s; %d error(s)", added, len(errors))
    return 0
