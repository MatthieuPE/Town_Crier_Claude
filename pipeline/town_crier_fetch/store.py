"""Data folder: one JSON-lines file per database and day first seen.

Layout::

    <data_dir>/index.json
    <data_dir>/last_run.json
    <data_dir>/<database>/<YYYY-MM-DD>.jsonl
"""

import datetime as dt
import json
from pathlib import Path

INDEX_FILE = "index.json"
LAST_RUN_FILE = "last_run.json"
SCHEMA = 1


def new_index():
    """Empty index."""
    return {"schema": SCHEMA, "updated": None, "databases": {}, "themes": {}}


def load_index(data_dir):
    """Index of the data folder, or a new one.

    Parameters
    ----------
    data_dir : str or Path
        Data folder.

    Returns
    -------
    dict
        Index.
    """
    path = Path(data_dir) / INDEX_FILE
    if not path.exists():
        return new_index()
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(data_dir, db):
    """All stored records of one database.

    Parameters
    ----------
    data_dir : str or Path
        Data folder.
    db : str
        Database name.

    Returns
    -------
    dict
        Paper id -> record.
    """
    records = {}
    for path in sorted((Path(data_dir) / db).glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                records[rec["paper_id"]] = rec
    return records


def merge(existing, fetched, *, today, backfill):
    """Add papers not seen before, with their first-seen day.

    Parameters
    ----------
    existing : dict
        Paper id -> record, updated in place.
    fetched : iterable of dict
        Records from one query.
    today : datetime.date
        Day of this run.
    backfill : bool
        True when the query covers a new scope or a requested backfill:
        papers are dated by their first version, not by today.

    Returns
    -------
    int
        Number of papers added.
    """
    added = 0
    for rec in fetched:
        if rec["paper_id"] in existing:
            continue  # already stored
        rec = dict(rec)
        published = rec.get("published") or today.isoformat()
        rec["first_seen"] = min(published, today.isoformat()) if backfill else today.isoformat()
        existing[rec["paper_id"]] = rec
        added += 1
    return added


def prune(records, today, retention_days):
    """Drop records first seen before the retention window.

    Parameters
    ----------
    records : dict
        Paper id -> record.
    today : datetime.date
        Day of this run.
    retention_days : int
        Days to keep.

    Returns
    -------
    dict
        Kept records.
    """
    cutoff = (today - dt.timedelta(days=retention_days)).isoformat()
    return {pid: r for pid, r in records.items() if r["first_seen"] >= cutoff}


def write_records(data_dir, db, records, today):
    """Rewrite the day files of one database.

    Parameters
    ----------
    data_dir : str or Path
        Data folder.
    db : str
        Database name.
    records : dict
        Paper id -> record.
    today : datetime.date
        Day of this run. Its file is written even when empty, to record
        that the run happened.

    Returns
    -------
    list of str
        Days with a file, sorted.
    """
    folder = Path(data_dir) / db
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.jsonl"):
        old.unlink()  # full rewrite
    by_day = {today.isoformat(): []}
    for rec in records.values():
        by_day.setdefault(rec["first_seen"], []).append(rec)
    for day, recs in by_day.items():
        lines = [json.dumps(r, ensure_ascii=False, sort_keys=True)
                 for r in sorted(recs, key=lambda r: r["paper_id"])]
        (folder / f"{day}.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""),
                                             encoding="utf-8")
    return sorted(by_day)


def update_database_entry(index, db, *, days, today, coverage, retention_days):
    """Record files, run days and scope coverage of one database.

    Parameters
    ----------
    index : dict
        Index, updated in place.
    db : str
        Database name.
    days : list of str
        Days with a file.
    today : datetime.date
        Day of this run.
    coverage : dict
        Scope -> first day covered (ISO date).
    retention_days : int
        Days of run history to keep.
    """
    entry = index["databases"].setdefault(db, {"files": [], "run_days": [], "coverage": {}})
    cutoff = (today - dt.timedelta(days=retention_days)).isoformat()
    runs = set(entry.get("run_days") or []) | {today.isoformat()}
    entry["files"] = days
    entry["run_days"] = sorted(d for d in runs if d >= cutoff)
    entry["coverage"] = dict(sorted(coverage.items()))


def write_json(data_dir, name, obj):
    """Write a JSON file in the data folder.

    Parameters
    ----------
    data_dir : str or Path
        Data folder.
    name : str
        File name.
    obj : object
        JSON-serializable content.
    """
    path = Path(data_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
