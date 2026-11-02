"""Fixtures shared by the fetch tests: synthetic API responses."""

import json

import pytest

ATOM_ENTRY = """
  <entry>
    <id>http://arxiv.org/abs/{id}v{v}</id>
    <updated>{updated}T10:00:00Z</updated>
    <published>{published}T10:00:00Z</published>
    <title>{title}</title>
    <summary>  {abstract}
    </summary>
    <author><name>Ada Lovelace</name></author>
    <author><name>Alan Turing</name></author>
    <arxiv:comment>12 pages, accepted to ApJ</arxiv:comment>
    <link href="http://arxiv.org/abs/{id}v{v}" rel="alternate" type="text/html"/>
    <arxiv:primary_category term="{cat}" scheme="http://arxiv.org/schemas/atom"/>
    <category term="{cat}" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.SR" scheme="http://arxiv.org/schemas/atom"/>
  </entry>"""


def atom_feed(entries, total=None):
    """Atom feed bytes from entry dicts."""
    body = "".join(ATOM_ENTRY.format(**e) for e in entries)
    total = len(entries) if total is None else total
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>{total}</opensearch:totalResults>
  {body}
</feed>""".encode()


def arxiv_entry(pid, published, *, v=1, cat="astro-ph.GA", title="A stellar stream", abstract="We find a stream."):
    """One entry dict for ``atom_feed``."""
    return {"id": pid, "v": v, "published": published, "updated": published, "title": title,
            "abstract": abstract, "cat": cat}


@pytest.fixture
def make_feed():
    """Builder of Atom feeds."""
    return atom_feed


@pytest.fixture
def make_entry():
    """Builder of Atom entry dicts."""
    return arxiv_entry


@pytest.fixture
def error_feed():
    """arXiv API error response."""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry><id>http://arxiv.org/api/errors#incorrect_id_format</id>
  <title>Error</title><summary>incorrect id format</summary></entry>
</feed>"""


@pytest.fixture
def biorxiv_page():
    """Builder of bioRxiv API pages."""
    def make(items, total=None, cursor=0):
        coll = [{"doi": d, "title": f"Paper {d}", "authors": "Doe, J.; Roe, R.", "date": date,
                 "version": str(v), "category": "Neuroscience", "abstract": "Neurons fire.",
                 "published": "NA", "server": "biorxiv"} for d, date, v in items]
        msg = {"status": "ok", "cursor": cursor, "count": len(coll),
               "total": len(coll) if total is None else total}
        return json.dumps({"messages": [msg], "collection": coll}).encode()
    return make


@pytest.fixture
def openalex_page():
    """Builder of OpenAlex works pages."""
    def make(works, count=None):
        results = [{
            "id": f"https://openalex.org/W{n}", "doi": f"https://doi.org/10.1038/test.{n}",
            "display_name": f"Discovery {n}", "publication_date": date, "type": "article",
            "authorships": [{"author": {"display_name": "Marie Curie"}}],
            "abstract_inverted_index": {"We": [0], "found": [1], "it": [2]},
            "primary_location": {"source": {"display_name": "Nature", "issn_l": "0028-0836",
                                            "issn": issns}},
        } for n, date, issns in works]
        return json.dumps({"meta": {"count": len(results) if count is None else count},
                           "results": results}).encode()
    return make
