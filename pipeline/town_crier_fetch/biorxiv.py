"""bioRxiv and medRxiv API client.

References
----------
bioRxiv API summary, https://api.biorxiv.org/
"""

import json
import logging
import time
import urllib.parse

from . import http

LOG = logging.getLogger(__name__)

API_URL = "https://api.biorxiv.org/details/{server}/{start}/{end}/{cursor}/json"
HOSTS = {"biorxiv": "https://www.biorxiv.org", "medrxiv": "https://www.medrxiv.org"}


def page_url(server, start, end, cursor, category=None):
    """URL of one result page.

    Parameters
    ----------
    server : {"biorxiv", "medrxiv"}
        Preprint server.
    start, end : datetime.date
        Posting-date interval, inclusive.
    cursor : int
        Index of the first result.
    category : str, optional
        Subject category, e.g. ``neuroscience``.

    Returns
    -------
    str
        Request URL.
    """
    url = API_URL.format(server=server, start=start.isoformat(), end=end.isoformat(), cursor=cursor)
    if category:
        url += "?category=" + urllib.parse.quote(category.replace(" ", "_"))
    return url


def parse_item(item, server):
    """Paper record from one item of the ``collection`` list.

    Parameters
    ----------
    item : dict
        API item.
    server : str
        Preprint server.

    Returns
    -------
    dict
        Paper record.
    """
    doi = (item.get("doi") or "").strip()
    version = str(item.get("version") or "1")
    authors = [a.strip() for a in (item.get("authors") or "").split(";") if a.strip()]
    journal_doi = item.get("published")
    return {
        "paper_id": f"doi:{doi.lower()}",
        "source": server,
        "title": " ".join((item.get("title") or "").split()),
        "authors": authors,
        "abstract": " ".join((item.get("abstract") or "").split()),
        "url": f"{HOSTS[server]}/content/{doi}v{version}",
        "html_url": None,
        "doi": doi or None,
        "categories": [(item.get("category") or "").strip().lower()],
        "primary_category": (item.get("category") or "").strip().lower() or None,
        "comment": None,
        "journal_ref": journal_doi if journal_doi and journal_doi != "NA" else None,
        "published": (item.get("date") or "")[:10],
        "updated": (item.get("date") or "")[:10],
        "version": int(version) if version.isdigit() else 1,
    }


def parse_page(data, server):
    """Records, page size and total from one response.

    Parameters
    ----------
    data : dict
        Decoded JSON response.
    server : str
        Preprint server.

    Returns
    -------
    records : list of dict
        Parsed items.
    count : int
        Items in this page.
    total : int
        Items in the whole interval.
    """
    collection = data.get("collection") or []
    message = (data.get("messages") or [{}])[0]
    count = int(message.get("count") or len(collection))
    total = int(message.get("total") or 0)
    return [parse_item(i, server) for i in collection if i.get("doi")], count, total


def fetch_server(server, start, end, *, category=None, delay=1.0, max_pages=500,
                 getter=http.get, sleep=time.sleep):
    """First versions posted in a date interval.

    Parameters
    ----------
    server : {"biorxiv", "medrxiv"}
        Preprint server.
    start, end : datetime.date
        Posting-date interval, inclusive.
    category : str, optional
        Subject category. All categories when None.
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
        Version-1 records only.
    """
    records, cursor = [], 0
    for _ in range(max_pages):
        data = json.loads(getter(page_url(server, start, end, cursor, category)))
        batch, count, total = parse_page(data, server)
        records.extend(batch)
        cursor += count
        if count == 0 or cursor >= total:
            break
        sleep(delay)  # be polite
    keep = {r["paper_id"]: r for r in records if r["version"] == 1}  # drop new versions
    LOG.info("%s %s: %d first versions of %d", server, category or "all", len(keep), len(records))
    return list(keep.values())
