"""Tests of the arXiv client."""

import datetime as dt
import xml.etree.ElementTree as ET

import pytest

from town_crier_fetch import arxiv

D = dt.date


@pytest.mark.fetch
@pytest.mark.arxiv
@pytest.mark.unit
def test_build_query_has_date_range():
    """Query holds category and GMT day bounds."""
    q = arxiv.build_query("astro-ph.GA", D(2026, 10, 9), D(2026, 10, 22))
    assert q == "cat:astro-ph.GA AND submittedDate:[202610090000 TO 202610222359]"


@pytest.mark.fetch
@pytest.mark.arxiv
@pytest.mark.unit
def test_parse_feed_fields(make_feed, make_entry):
    """Entry fields are parsed and cleaned."""
    feed = make_feed([make_entry("2610.30264", "2026-10-21", abstract="Line one\n  line two.")])
    records, total = arxiv.parse_feed(feed)
    rec = records[0]
    assert total == 1
    assert rec["paper_id"] == "arXiv:2610.30264"
    assert rec["version"] == 1
    assert rec["published"] == "2026-10-21"
    assert rec["abstract"] == "Line one line two."
    assert rec["authors"] == ["Ada Lovelace", "Alan Turing"]
    assert rec["categories"] == ["astro-ph.GA", "astro-ph.SR"]
    assert rec["primary_category"] == "astro-ph.GA"
    assert rec["url"] == "https://arxiv.org/abs/2610.30264"
    assert rec["comment"] == "12 pages, accepted to ApJ"


@pytest.mark.fetch
@pytest.mark.arxiv
@pytest.mark.unit
def test_error_feed_raises(error_feed):
    """API error entries raise ValueError."""
    with pytest.raises(ValueError, match="incorrect id format"):
        arxiv.parse_feed(error_feed)


@pytest.mark.fetch
@pytest.mark.arxiv
@pytest.mark.unit
def test_old_style_id():
    """Old identifiers with a slash keep it."""
    xml = ('<entry xmlns="http://www.w3.org/2005/Atom"><id>http://arxiv.org/abs/hep-ex/0307015v2</id>'
           '<published>2003-07-07T00:00:00Z</published><title>T</title><summary>S</summary></entry>')
    rec = arxiv.parse_entry(ET.fromstring(xml))
    assert rec["paper_id"] == "arXiv:hep-ex/0307015"
    assert rec["version"] == 2


@pytest.mark.fetch
@pytest.mark.arxiv
@pytest.mark.unit
def test_fetch_pages_and_drops_replacements(make_feed, make_entry):
    """Pages are followed; replacements of old papers are dropped; duplicates merged."""
    pages = [
        make_feed([make_entry("2610.00001", "2026-10-20"), make_entry("2610.00002", "2026-10-19")], total=4),
        make_feed([make_entry("2610.00002", "2026-10-19"),
                   make_entry("2501.00009", "2025-01-03", v=3)], total=4),  # duplicate + replacement
    ]
    calls = []

    def getter(url):
        calls.append(url)
        return pages[len(calls) - 1]

    recs = arxiv.fetch_category("astro-ph.GA", D(2026, 10, 9), D(2026, 10, 22), page_size=2,
                                getter=getter, sleep=lambda s: None)
    assert sorted(r["paper_id"] for r in recs) == ["arXiv:2610.00001", "arXiv:2610.00002"]
    assert len(calls) == 2
    assert "start=2" in calls[1]


@pytest.mark.fetch
@pytest.mark.arxiv
@pytest.mark.unit
def test_fetch_retries_transient_empty_page(make_feed, make_entry):
    """An empty page below the total is retried."""
    pages = [make_feed([], total=1), make_feed([make_entry("2610.00003", "2026-10-21")], total=1)]
    it = iter(pages)
    recs = arxiv.fetch_category("astro-ph.GA", D(2026, 10, 9), D(2026, 10, 22),
                                getter=lambda url: next(it), sleep=lambda s: None)
    assert [r["paper_id"] for r in recs] == ["arXiv:2610.00003"]
