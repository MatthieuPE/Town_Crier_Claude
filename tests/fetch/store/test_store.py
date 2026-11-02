"""Tests of the data folder storage."""

import datetime as dt
import json

import pytest

from town_crier_fetch import store

D = dt.date


def rec(pid, published):
    """Minimal record."""
    return {"paper_id": pid, "published": published, "title": pid}


@pytest.mark.fetch
@pytest.mark.store
@pytest.mark.unit
def test_merge_dates_new_papers_today():
    """Normal runs date new papers by the run day; known papers are skipped."""
    existing = {"a": {"paper_id": "a", "first_seen": "2026-10-20"}}
    added = store.merge(existing, [rec("a", "2026-10-19"), rec("b", "2026-10-21")],
                        today=D(2026, 10, 23), backfill=False)
    assert added == 1
    assert existing["a"]["first_seen"] == "2026-10-20"
    assert existing["b"]["first_seen"] == "2026-10-23"


@pytest.mark.fetch
@pytest.mark.store
@pytest.mark.unit
def test_merge_backfill_uses_first_version_date():
    """Backfill dates papers by their first version."""
    existing = {}
    store.merge(existing, [rec("b", "2026-10-15")], today=D(2026, 10, 23), backfill=True)
    assert existing["b"]["first_seen"] == "2026-10-15"


@pytest.mark.fetch
@pytest.mark.store
@pytest.mark.unit
def test_prune_retention():
    """Records older than the retention window are dropped."""
    records = {"old": {"paper_id": "old", "first_seen": "2026-07-01"},
               "new": {"paper_id": "new", "first_seen": "2026-10-01"}}
    kept = store.prune(records, D(2026, 10, 23), retention_days=100)
    assert list(kept) == ["new"]


@pytest.mark.fetch
@pytest.mark.store
@pytest.mark.unit
def test_write_and_reload_day_files(tmp_path):
    """One file per day, today's file even when empty; reload round-trips."""
    records = {"a": {"paper_id": "a", "first_seen": "2026-10-20"},
               "b": {"paper_id": "b", "first_seen": "2026-10-20"}}
    days = store.write_records(tmp_path, "arxiv", records, D(2026, 10, 23))
    assert days == ["2026-10-20", "2026-10-23"]
    assert (tmp_path / "arxiv" / "2026-10-23.jsonl").read_text() == ""
    assert store.load_records(tmp_path, "arxiv") == records


@pytest.mark.fetch
@pytest.mark.store
@pytest.mark.unit
def test_index_entry_and_json(tmp_path):
    """Run days accumulate within retention; index is written as JSON."""
    index = store.new_index()
    for day in (D(2026, 6, 1), D(2026, 10, 22), D(2026, 10, 23)):
        store.update_database_entry(index, "arxiv", days=[day.isoformat()], today=day,
                                    coverage={"astro-ph.GA": "2026-06-01"}, retention_days=100)
    entry = index["databases"]["arxiv"]
    assert entry["run_days"] == ["2026-10-22", "2026-10-23"]
    store.write_json(tmp_path, store.INDEX_FILE, index)
    assert json.loads((tmp_path / "index.json").read_text())["databases"]["arxiv"]["files"] == ["2026-10-23"]
