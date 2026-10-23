"""Tests of the bioRxiv/medRxiv client."""

import datetime as dt

import pytest

from town_crier_fetch import biorxiv

D = dt.date


@pytest.mark.fetch
@pytest.mark.biorxiv
@pytest.mark.unit
def test_page_url_with_category():
    """Interval, cursor and category are in the URL."""
    url = biorxiv.page_url("biorxiv", D(2026, 10, 20), D(2026, 10, 22), 30, "cell biology")
    assert url == "https://api.biorxiv.org/details/biorxiv/2026-10-20/2026-10-22/30/json?category=cell_biology"


@pytest.mark.fetch
@pytest.mark.biorxiv
@pytest.mark.unit
def test_fetch_pages_and_keeps_first_versions(biorxiv_page):
    """Cursor advances by page size; only version 1 is kept."""
    pages = [
        biorxiv_page([("10.1101/2026.10.20.1", "2026-10-20", 1), ("10.1101/2026.01.01.9", "2026-10-21", 2)], total=3),
        biorxiv_page([("10.1101/2026.10.21.2", "2026-10-21", 1)], total=3, cursor=2),
    ]
    urls = []

    def getter(url):
        urls.append(url)
        return pages[len(urls) - 1]

    recs = biorxiv.fetch_server("biorxiv", D(2026, 10, 20), D(2026, 10, 22), getter=getter,
                                sleep=lambda s: None)
    ids = sorted(r["paper_id"] for r in recs)
    assert ids == ["doi:10.1101/2026.10.20.1", "doi:10.1101/2026.10.21.2"]
    assert urls[1].endswith("/2/json")
    rec = next(r for r in recs if r["paper_id"].endswith(".1"))
    assert rec["authors"] == ["Doe, J.", "Roe, R."]
    assert rec["categories"] == ["neuroscience"]
    assert rec["url"] == "https://www.biorxiv.org/content/10.1101/2026.10.20.1v1"
