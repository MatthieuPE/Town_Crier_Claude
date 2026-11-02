"""OpenAlex API client, for journal papers.

References
----------
OpenAlex works filters, https://developers.openalex.org/api-reference/works
OpenAlex quick reference, https://developers.openalex.org/guides/llm-quick-reference.md
"""

import json
import logging
import time

from . import http

LOG = logging.getLogger(__name__)

API_URL = "https://api.openalex.org/works"
SELECT = "id,doi,display_name,publication_date,authorships,abstract_inverted_index,primary_location,type"


def build_filter(issns, start, end):
    """``filter`` value for research articles of some journals in a date range.

    Parameters
    ----------
    issns : iterable of str
        Journal ISSNs (print or electronic). At most 100.
    start, end : datetime.date
        Publication-date range, inclusive.

    Returns
    -------
    str
        Filter string.
    """
    return ",".join([
        "primary_location.source.issn:" + "|".join(sorted(issns)),  # OR over journals
        f"from_publication_date:{start.isoformat()}",
        f"to_publication_date:{end.isoformat()}",
        "type:article",
        "has_abstract:true",
    ])


def reconstruct_abstract(inverted):
    """Plain abstract from an OpenAlex inverted index.

    Parameters
    ----------
    inverted : dict or None
        Word -> list of positions.

    Returns
    -------
    str
        Abstract text, empty when missing.
    """
    if not inverted:
        return ""
    slots = [(pos, word) for word, positions in inverted.items() for pos in positions]
    return " ".join(word for _, word in sorted(slots))  # words in order


def parse_work(work):
    """Paper record from one OpenAlex work.

    Parameters
    ----------
    work : dict
        Work object.

    Returns
    -------
    dict
        Paper record.
    """
    doi = (work.get("doi") or "").replace("https://doi.org/", "").strip()
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    issns = list(source.get("issn") or ([source["issn_l"]] if source.get("issn_l") else []))
    openalex_id = (work.get("id") or "").rsplit("/", 1)[-1]
    url = f"https://doi.org/{doi}" if doi else (location.get("landing_page_url") or work.get("id"))
    authors = [((a.get("author") or {}).get("display_name") or "").strip()
               for a in work.get("authorships") or []]
    return {
        "paper_id": f"doi:{doi.lower()}" if doi else f"openalex:{openalex_id}",
        "source": "openalex",
        "title": " ".join((work.get("display_name") or "").split()),
        "authors": [a for a in authors if a],
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "url": url,
        "html_url": None,
        "doi": doi or None,
        "categories": [],
        "primary_category": None,
        "comment": None,
        "journal_ref": source.get("display_name"),
        "journal": source.get("display_name"),
        "issn": issns,
        "type": work.get("type"),
        "published": (work.get("publication_date") or "")[:10],
        "updated": (work.get("publication_date") or "")[:10],
        "version": 1,
    }


def fetch_journals(issns, start, end, *, api_key, per_page=100, delay=1.0, max_pages=50,
                   getter=http.get, sleep=time.sleep):
    """Research articles of some journals published in a date range.

    Parameters
    ----------
    issns : iterable of str
        Journal ISSNs.
    start, end : datetime.date
        Publication-date range, inclusive.
    api_key : str
        OpenAlex API key (free, required since 2026).
    per_page : int
        Results per request (maximum 100).
    delay : float
        Wait between requests, s.
    max_pages : int
        Safety limit on requests.
    getter : callable
        ``getter(url) -> bytes``.
    sleep : callable
        Wait function.

    Returns
    -------
    list of dict
        Paper records.

    Raises
    ------
    http.FetchError
        No API key.
    """
    if not api_key:
        raise http.FetchError("OPENALEX_API_KEY is not set: journal papers skipped")
    filt = build_filter(issns, start, end)
    records = {}
    for page in range(1, max_pages + 1):
        url = http.with_params(API_URL, {
            "filter": filt, "select": SELECT, "per_page": per_page, "page": page, "api_key": api_key,
        })
        data = json.loads(getter(url))
        results = data.get("results") or []
        for work in results:
            rec = parse_work(work)
            records.setdefault(rec["paper_id"], rec)
        count = int((data.get("meta") or {}).get("count") or 0)
        if not results or page * per_page >= count:
            break
        sleep(delay)  # be polite
    LOG.info("openalex: %d articles", len(records))
    return list(records.values())
