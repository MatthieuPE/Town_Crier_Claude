"""Paper data: the ``data`` branch on GitHub, or a local copy."""

import json
import urllib.error
from pathlib import Path

from . import files


class DataSource:
    """Reader of the data folder written by the daily fetch.

    Parameters
    ----------
    repository : str, optional
        ``owner/name`` on GitHub.
    branch : str
        Data branch.
    local_dir : str or Path, optional
        Local data folder; used instead of GitHub when given.
    cache_dir : str or Path, optional
        Where downloaded files are kept during a run.
    """

    def __init__(self, repository=None, branch="data", local_dir=None, cache_dir=None):
        if not (repository or local_dir):
            raise ValueError("a repository or a local data folder is required")
        self.repository = repository
        self.branch = branch
        self.local_dir = Path(local_dir) if local_dir else None
        self.cache_dir = Path(cache_dir) if cache_dir else None

    def read(self, rel):
        """Text of a data file, or None when it does not exist.

        Parameters
        ----------
        rel : str
            Path inside the data folder.

        Returns
        -------
        str or None
            File content.
        """
        if self.local_dir:
            path = self.local_dir / rel
            return path.read_text(encoding="utf-8") if path.exists() else None
        cached = self.cache_dir / rel if self.cache_dir else None
        if cached and cached.exists():
            return cached.read_text(encoding="utf-8")
        try:
            text = files.fetch_text(files.raw_url(self.repository, self.branch, rel))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None  # no such file
            raise
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_text(text, encoding="utf-8")
        return text

    def index(self):
        """Index of the data folder.

        Raises
        ------
        FileNotFoundError
            No index: the daily fetch has never run.
        """
        text = self.read("index.json")
        if text is None:
            raise FileNotFoundError("index.json not found: run the 'Fetch papers' GitHub Action first")
        return json.loads(text)

    def day(self, db, day):
        """Records first seen on one day, or None when there is no file."""
        text = self.read(f"{db}/{day}.jsonl")
        if text is None:
            return None
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def from_config(resolved, run_dir=None, local_dir=None):
    """Data source described by a resolved configuration.

    Parameters
    ----------
    resolved : dict
        Resolved configuration (``data`` block).
    run_dir : str or Path, optional
        Run folder, for the download cache.
    local_dir : str or Path, optional
        Overrides ``data.local_dir``.

    Returns
    -------
    DataSource
        Reader.
    """
    data = resolved.get("data") or {}
    return DataSource(repository=data.get("repository"), branch=data.get("branch", "data"),
                      local_dir=local_dir or data.get("local_dir"),
                      cache_dir=Path(run_dir) / "data_cache" if run_dir else None)
