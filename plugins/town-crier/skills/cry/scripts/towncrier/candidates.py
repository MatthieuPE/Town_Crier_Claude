"""Candidate papers of the period, and stage-1 pools per subsection."""

import datetime as dt

from . import config as config_mod, prefilter, themes as themes_mod


def needed_databases(resolved):
    """Databases used by the subsections' themes."""
    dbs = set()
    for sub in config_mod.iter_subsections(resolved):
        theme = resolved["themes"].get(sub["theme"]) or {}
        dbs.update(themes_mod.scopes(theme))
    return sorted(dbs)


def collect(source, index, dbs, days):
    """Records first seen during the period.

    Parameters
    ----------
    source : data.DataSource
        Data reader.
    index : dict
        Data index.
    dbs : list of str
        Databases to read.
    days : list of datetime.date
        Covered days.

    Returns
    -------
    records : dict
        Paper id -> record.
    notes : list of str
        Coverage problems, for the digest notes.
    """
    records, notes = {}, []
    for db in dbs:
        entry = (index.get("databases") or {}).get(db)
        if not entry:
            notes.append(f"No data for {db}: the daily fetch does not cover it yet.")
            continue
        file_days = set(entry.get("files") or [])
        for day in days:
            if day.isoformat() not in file_days:
                continue
            for rec in source.day(db, day.isoformat()) or []:
                records.setdefault(rec["paper_id"], rec)
        runs = set(entry.get("run_days") or [])
        first_run = min(runs) if runs else None
        missing = [d.isoformat() for d in days
                   if first_run and d.isoformat() >= first_run and d.isoformat() not in runs]
        if missing:
            notes.append(f"{db}: the daily fetch did not run on {', '.join(missing)}; "
                         "papers of those days are normally caught up the next day.")
    last = index.get("last_run_day")
    if last and days and last < days[-1].isoformat():
        notes.append(f"Data last updated on {last}, before the end of the period: "
                     "the latest papers may be missing.")
    return records, notes


def coverage_notes(index, resolved, start):
    """Notes for theme scopes whose coverage starts after the period start.

    Parameters
    ----------
    index : dict
        Data index.
    resolved : dict
        Resolved configuration.
    start : datetime.date
        First covered day.

    Returns
    -------
    list of str
        Notes.
    """
    notes = []
    for sub in config_mod.iter_subsections(resolved):
        theme = resolved["themes"].get(sub["theme"]) or {}
        for db, scope_list in themes_mod.scopes(theme).items():
            coverage = ((index.get("databases") or {}).get(db) or {}).get("coverage") or {}
            for scope in scope_list:
                since = coverage.get(scope)
                if since is None:
                    notes.append(f"{sub['id']} {sub['title']}: {db} {scope} is not fetched yet "
                                 "(added recently?); it appears after the next daily fetch.")
                elif since > start.isoformat():
                    notes.append(f"{sub['id']} {sub['title']}: {db} {scope} is covered only since "
                                 f"{since}; the count may be incomplete.")
    return sorted(set(notes))


def build_pools(resolved, records):
    """Stage-1 pool of each subsection.

    Parameters
    ----------
    resolved : dict
        Resolved configuration.
    records : dict
        Paper id -> record of the period.

    Returns
    -------
    pools : dict
        Subsection id -> paper ids, newest first.
    candidates : dict
        Paper id -> record, with ``found_for`` (subsection ids).
    """
    pools, candidates = {}, {}
    ordered = sorted(records.values(), key=lambda r: (r.get("first_seen", ""), r["paper_id"]), reverse=True)
    for sub in config_mod.iter_subsections(resolved):
        filt = prefilter.ThemeFilter.from_theme(resolved["themes"].get(sub["theme"]) or {})
        ids = [r["paper_id"] for r in ordered if filt.passes(r)]
        pools[sub["id"]] = ids
        for pid in ids:
            cand = candidates.setdefault(pid, dict(records[pid], found_for=[]))
            cand["found_for"].append(sub["id"])
    return pools, candidates


def period_days(resolved):
    """Covered days of a resolved configuration."""
    start = dt.date.fromisoformat(resolved["period"]["start"])
    end = dt.date.fromisoformat(resolved["period"]["end"])
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
