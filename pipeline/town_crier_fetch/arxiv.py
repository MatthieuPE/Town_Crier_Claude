"""arXiv API client.

References
----------
arXiv API User's Manual, https://info.arxiv.org/help/api/user-manual.html
"""

import logging
import re
import time
import xml.etree.ElementTree as ET

from . import http

LOG = logging.getLogger(__name__)

API_URL = "https://export.arxiv.org/api/query"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}
_ID_RE = re.compile(r"arxiv\.org/abs/(?P<id>[^\s]+?)(?:v(?P<v>\d+))?$")


def build_query(category, start, end):
    """Search query for one category and a submission-date range.

    Parameters
    ----------
    category : str
        arXiv category, e.g. ``astro-ph.GA``. Cross-lists match too.
    start, end : datetime.date
        First and last day, inclusive (GMT).

    Returns
    -------
    str
        Value of the ``search_query`` parameter.
    """
    return f"cat:{category} AND submittedDate:[{start:%Y%m%d}0000 TO {end:%Y%m%d}2359]"


def _text(node, path):
    """Whitespace-collapsed text of a child element, or empty string."""
    found = node.find(path, NS)
    if found is None or not found.text:
        return ""
    return " ".join(found.text.split())  # collapse wraps


def _split_id(url):
    """Base identifier and version from an abstract URL."""
    match = _ID_RE.search(url or "")
    if not match:
        return None, None
    version = int(match.group("v")) if match.group("v") else None
    return match.group("id"), version


def parse_entry(entry):
    """Paper record from one Atom ``<entry>``.

    Parameters
    ----------
    entry : xml.etree.ElementTree.Element
        Atom entry.

    Returns
    -------
    dict or None
        Paper record, or None when the entry has no usable identifier.

    Raises
    ------
    ValueError
        Entry is an arXiv API error message.
    """
    raw_id = _text(entry, "atom:id")
    if "/api/errors" in raw_id:
        raise ValueError(f"arXiv API error: {_text(entry, 'atom:summary')}")
    base_id, version = _split_id(raw_id)
    for link in entry.findall("atom:link", NS):  # version from alternate link
        if link.get("rel") == "alternate":
            alt_id, alt_version = _split_id(link.get("href", ""))
            base_id = base_id or alt_id
            version = version or alt_version
    if not base_id:
        return None
    primary = entry.find("arxiv:primary_category", NS)
    categories = [c.get("term") for c in entry.findall("atom:category", NS) if c.get("term")]
    return {
        "paper_id": f"arXiv:{base_id}",
        "source": "arxiv",
        "title": _text(entry, "atom:title"),
        "authors": [_text(a, "atom:name") for a in entry.findall("atom:author", NS)],
        "abstract": _text(entry, "atom:summary"),
        "url": f"https://arxiv.org/abs/{base_id}",
        "html_url": f"https://arxiv.org/html/{base_id}",
        "doi": _text(entry, "arxiv:doi") or None,
        "categories": categories,
        "primary_category": primary.get("term") if primary is not None else None,
        "comment": _text(entry, "arxiv:comment") or None,
        "journal_ref": _text(entry, "arxiv:journal_ref") or None,
        "published": _text(entry, "atom:published")[:10],
        "updated": _text(entry, "atom:updated")[:10],
        "version": version or 1,
    }


def parse_feed(xml_bytes):
    """Records and total match count from one API response.

    Parameters
    ----------
    xml_bytes : bytes
        Atom feed.

    Returns
    -------
    records : list of dict
        Parsed entries.
    total : int
        ``opensearch:totalResults``.
    """
    root = ET.fromstring(xml_bytes)
    total_text = _text(root, "opensearch:totalResults")
    total = int(total_text) if total_text.isdigit() else 0
    records = [parse_entry(e) for e in root.findall("atom:entry", NS)]
    return [r for r in records if r], total


def fetch_category(category, start, end, *, page_size=500, delay=3.0, max_results=10000,
                   getter=http.get, sleep=time.sleep):
    """New papers of one category whose first version is in a date range.

    Parameters
    ----------
    category : str
        arXiv category.
    start, end : datetime.date
        First and last submission day, inclusive.
    page_size : int
        Results per request (API maximum 2000).
    delay : float
        Wait between requests, s. The API asks for 3 s.
    max_results : int
        Stop after this many results.
    getter : callable
        ``getter(url) -> bytes``.
    sleep : callable
        Wait function.

    Returns
    -------
    list of dict
        Records with first version (``published``) on or after ``start``.
        Replacements of older papers are dropped.
    """
    query = build_query(category, start, end)
    records, offset, empty_retries = [], 0, 0
    while True:
        url = http.with_params(API_URL, {
            "search_query": query, "start": offset, "max_results": page_size,
            "sortBy": "submittedDate", "sortOrder": "descending",
        })
        batch, total = parse_feed(getter(url))
        if not batch and offset < total and empty_retries < 3:
            empty_retries += 1  # transient empty page
            sleep(delay)
            continue
        records.extend(batch)
        offset += len(batch)
        if not batch or offset >= total or offset >= max_results:
            break
        sleep(delay)  # be polite
    keep = {}
    for rec in records:
        if rec["published"] and rec["published"] >= start.isoformat():  # v1 in window
            keep.setdefault(rec["paper_id"], rec)
    LOG.info("arxiv %s: %d new of %d returned", category, len(keep), len(records))
    return list(keep.values())
