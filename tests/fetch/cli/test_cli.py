"""Integration tests of the daily fetch command."""

import json

import pytest

from town_crier_fetch import cli


def fake_getter(make_feed, make_entry, openalex_page, papers_by_cat):
    """Getter answering arXiv by category and OpenAlex with one page."""
    def getter(url):
        if "export.arxiv.org" in url:
            for cat, entries in papers_by_cat.items():
                if f"cat:{cat}" in url.replace("%3A", ":"):
                    return make_feed([make_entry(pid, pub, cat=cat) for pid, pub in entries])
            return make_feed([])
        if "api.openalex.org" in url:
            return openalex_page([(7, "2026-10-21", ["0028-0836"])])
        raise AssertionError(url)
    return getter


@pytest.mark.fetch
@pytest.mark.integration
def test_two_daily_runs(plugin_repo, tmp_path, monkeypatch, make_feed, make_entry, openalex_page):
    """First run backfills by first-version date; next run dates new papers by run day."""
    data = tmp_path / "data"
    monkeypatch.setenv("OPENALEX_API_KEY", "k")
    day1 = {"astro-ph.GA": [("2610.00001", "2026-10-20")], "astro-ph.CO": [("2610.00002", "2026-10-21")]}
    getter = fake_getter(make_feed, make_entry, openalex_page, day1)
    args = ["--repo-root", str(plugin_repo), "--data-dir", str(data)]
    assert cli.main(args + ["--today", "2026-10-22"], getter=getter, sleep=lambda s: None) == 0

    index = json.loads((data / "index.json").read_text())
    assert index["databases"]["arxiv"]["coverage"] == {"astro-ph.CO": "2026-10-08", "astro-ph.GA": "2026-10-08"}
    first = json.loads((data / "arxiv" / "2026-10-20.jsonl").read_text().splitlines()[0])
    assert first["paper_id"] == "arXiv:2610.00001" and first["first_seen"] == "2026-10-20"
    assert sorted(index["themes"]) == ["cosmo", "science", "streams"]

    day2 = dict(day1, **{"astro-ph.GA": [("2610.00001", "2026-10-20"), ("2610.00003", "2026-10-22")]})
    getter = fake_getter(make_feed, make_entry, openalex_page, day2)
    assert cli.main(args + ["--today", "2026-10-23"], getter=getter, sleep=lambda s: None) == 0
    new = [json.loads(line) for line in (data / "arxiv" / "2026-10-23.jsonl").read_text().splitlines()]
    assert [r["paper_id"] for r in new] == ["arXiv:2610.00003"]
    last = json.loads((data / "last_run.json").read_text())
    assert last == {"added": {"arxiv": 1, "openalex": 0}, "date": "2026-10-23", "errors": []}


@pytest.mark.fetch
@pytest.mark.integration
def test_missing_openalex_key_is_reported(plugin_repo, tmp_path, monkeypatch, make_feed, make_entry,
                                          openalex_page):
    """A failed database is listed in last_run.json; others still run."""
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    getter = fake_getter(make_feed, make_entry, openalex_page, {"astro-ph.GA": [("2610.00001", "2026-10-20")]})
    cli.main(["--repo-root", str(plugin_repo), "--data-dir", str(tmp_path), "--today", "2026-10-22"],
             getter=getter, sleep=lambda s: None)
    last = json.loads((tmp_path / "last_run.json").read_text())
    assert last["added"]["arxiv"] == 1
    assert any("OPENALEX_API_KEY" in e for e in last["errors"])
    index = json.loads((tmp_path / "index.json").read_text())
    assert index["databases"]["openalex"]["coverage"] == {}  # retried as new scope next time
