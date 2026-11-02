"""Tests of the OpenAlex client."""

import datetime as dt

import pytest

from town_crier_fetch import http, openalex

D = dt.date


@pytest.mark.fetch
@pytest.mark.openalex
@pytest.mark.unit
def test_reconstruct_abstract_orders_words():
    """Words are placed by position."""
    inv = {"stream": [2], "A": [0], "stellar": [1], "again": [4], "and": [3]}
    assert openalex.reconstruct_abstract(inv) == "A stellar stream and again"
    assert openalex.reconstruct_abstract(None) == ""


@pytest.mark.fetch
@pytest.mark.openalex
@pytest.mark.unit
def test_build_filter():
    """Filter ORs journals and bounds dates."""
    f = openalex.build_filter(["1476-4687", "0028-0836"], D(2026, 10, 1), D(2026, 10, 22))
    assert f == ("primary_location.source.issn:0028-0836|1476-4687,from_publication_date:2026-10-01,"
                 "to_publication_date:2026-10-22,type:article,has_abstract:true")


@pytest.mark.fetch
@pytest.mark.openalex
@pytest.mark.unit
def test_requires_api_key():
    """Missing key is an explicit failure."""
    with pytest.raises(http.FetchError, match="OPENALEX_API_KEY"):
        openalex.fetch_journals(["0028-0836"], D(2026, 10, 1), D(2026, 10, 22), api_key=None)


@pytest.mark.fetch
@pytest.mark.openalex
@pytest.mark.unit
def test_fetch_journals_paging(openalex_page):
    """Pages stop at the reported count; records are parsed."""
    pages = [openalex_page([(1, "2026-10-20", ["0028-0836"])], count=2),
             openalex_page([(2, "2026-10-21", ["0028-0836"])], count=2)]
    urls = []

    def getter(url):
        urls.append(url)
        return pages[len(urls) - 1]

    recs = openalex.fetch_journals(["0028-0836"], D(2026, 10, 1), D(2026, 10, 22), api_key="k",
                                   per_page=1, getter=getter, sleep=lambda s: None)
    assert len(urls) == 2
    assert "api_key=k" in urls[0] and "page=2" in urls[1]
    rec = recs[0]
    assert rec["paper_id"] == "doi:10.1038/test.1"
    assert rec["abstract"] == "We found it"
    assert rec["journal"] == "Nature"
    assert rec["url"] == "https://doi.org/10.1038/test.1"
    assert rec["issn"] == ["0028-0836"]


@pytest.mark.fetch
@pytest.mark.openalex
@pytest.mark.unit
def test_redact_hides_key():
    """API keys never reach logs."""
    assert http.redact("https://x?a=1&api_key=SECRET&b=2") == "https://x?a=1&api_key=***&b=2"
