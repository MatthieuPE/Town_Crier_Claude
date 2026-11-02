"""File and URL helpers."""

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import yaml

USER_AGENT = "TownCrier-run/0.1"


def is_url(src):
    """True for http(s) sources."""
    return str(src).startswith(("http://", "https://"))


def fetch_text(url, timeout=60):
    """Text of a URL.

    Parameters
    ----------
    url : str
        URL.
    timeout : float
        Socket timeout, s.

    Returns
    -------
    str
        Decoded body.

    Raises
    ------
    urllib.error.URLError
        Network failure or HTTP error.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def read_text(src):
    """Text of a local file or a URL."""
    return fetch_text(src) if is_url(src) else Path(src).read_text(encoding="utf-8")


def read_yaml(src):
    """YAML mapping from a file or URL; empty mapping for empty files."""
    return yaml.safe_load(read_text(src)) or {}


def write_yaml(path, obj):
    """Write YAML, keys in insertion order."""
    Path(path).write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True), encoding="utf-8")


def read_json(path, default=None):
    """JSON content, or ``default`` when the file is missing."""
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, obj):
    """Write indented JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def read_jsonl(path):
    """Rows of a JSON-lines file; empty list when missing."""
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    """Write a JSON-lines file."""
    lines = [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows]
    Path(path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def safe_name(paper_id):
    """File-name-safe version of a paper id."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", paper_id)


def raw_url(repository, branch, path):
    """GitHub raw URL of a file.

    Parameters
    ----------
    repository : str
        ``owner/name``.
    branch : str
        Branch name.
    path : str
        Path inside the repository.

    Returns
    -------
    str
        URL on raw.githubusercontent.com.
    """
    return f"https://raw.githubusercontent.com/{repository}/{branch}/{path}"
