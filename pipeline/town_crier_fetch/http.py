"""HTTP GET with retries."""

import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request

LOG = logging.getLogger(__name__)

USER_AGENT = "TownCrier/0.1 (+https://github.com/MatthieuPE/Town_Crier_Claude)"
RETRY_CODES = {429, 500, 502, 503, 504}


class FetchError(RuntimeError):
    """Request failed after all retries."""


def with_params(url, params):
    """URL with an encoded query string.

    Parameters
    ----------
    url : str
        Base URL.
    params : dict
        Query parameters. ``None`` values are dropped.

    Returns
    -------
    str
        Full URL.
    """
    clean = {k: v for k, v in params.items() if v is not None}  # drop empty
    if not clean:
        return url
    query = urllib.parse.urlencode(clean, safe=":[]|,*")  # keep query syntax
    return f"{url}?{query}"


def redact(url):
    """URL with any API key hidden, for logs.

    Parameters
    ----------
    url : str
        URL that may hold ``api_key=...``.

    Returns
    -------
    str
        Same URL, key replaced by ``***``.
    """
    return re.sub(r"(api_key=)[^&]+", r"\1***", url)


def get(url, *, headers=None, retries=3, backoff=5.0, timeout=60.0, sleep=time.sleep):
    """GET a URL, retrying on network errors and on 429/5xx answers.

    Parameters
    ----------
    url : str
        URL to fetch.
    headers : dict, optional
        Extra request headers.
    retries : int
        Maximum number of attempts.
    backoff : float
        Base wait between attempts, s. Grows linearly.
    timeout : float
        Socket timeout, s.
    sleep : callable
        Wait function, replaceable in tests.

    Returns
    -------
    bytes
        Response body.

    Raises
    ------
    FetchError
        All attempts failed, or the server refused the request.
    """
    hdrs = {"User-Agent": USER_AGENT}
    hdrs.update(headers or {})
    last = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in RETRY_CODES:
                break  # client error: no retry
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
        if attempt < retries:
            LOG.warning("retry %d for %s (%s)", attempt, redact(url), last)
            sleep(backoff * attempt)  # wait longer each time
    raise FetchError(f"GET failed: {redact(url)}: {last}")
