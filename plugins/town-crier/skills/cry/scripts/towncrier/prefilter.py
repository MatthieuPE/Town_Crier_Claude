"""Stage-1 filter: databases, keywords and authors of a theme.

Keywords match whole words, case-insensitively, in the title and abstract.
A trailing ``*`` matches any ending (``stream*`` matches ``streams``).
Hyphens, slashes and LaTeX markup are read as spaces (``GD-1`` matches
``GD 1``).
"""

import re
from dataclasses import dataclass, field

from . import themes as themes_mod

_MARKUP = re.compile(r"[$\\{}^_~]")
_SEPARATORS = re.compile(r"[\s\-‐-―/]+")


def normalize(text):
    """Lowercase text with markup and separators turned into single spaces."""
    text = _MARKUP.sub(" ", (text or "").lower())
    return _SEPARATORS.sub(" ", text).strip()


def compile_keyword(keyword):
    """Regex for one keyword.

    Parameters
    ----------
    keyword : str
        Word or phrase; trailing ``*`` for any ending.

    Returns
    -------
    re.Pattern
        Pattern applied to normalized text.
    """
    raw = keyword.strip()
    prefix = raw.endswith("*")
    core = normalize(raw.rstrip("*"))
    tail = "" if prefix else r"(?![a-z0-9])"  # whole word unless *
    return re.compile(r"(?<![a-z0-9])" + re.escape(core) + tail)


@dataclass
class ThemeFilter:
    """Stage-1 filter of one theme."""

    scopes: dict
    any_of: list = field(default_factory=list)
    all_of: list = field(default_factory=list)
    exclude: list = field(default_factory=list)
    authors: list = field(default_factory=list)

    @classmethod
    def from_theme(cls, theme):
        """Filter from a theme definition."""
        kw = theme.get("keywords") or {}
        return cls(
            scopes=themes_mod.scopes(theme),
            any_of=[compile_keyword(k) for k in kw.get("any") or []],
            all_of=[compile_keyword(k) for k in kw.get("all") or []],
            exclude=[compile_keyword(k) for k in kw.get("exclude") or []],
            authors=[normalize(a) for a in theme.get("authors") or [] if a],
        )

    def in_scope(self, rec):
        """True when the record comes from one of the theme's scopes."""
        source = rec.get("source")
        allowed = self.scopes.get(source)
        if not allowed:
            return False
        if source == "arxiv":
            return any(c in allowed for c in rec.get("categories") or [])  # cross-lists count
        if source in ("biorxiv", "medrxiv"):
            return "all" in allowed or any(c in allowed for c in rec.get("categories") or [])
        if source == "openalex":
            return any(i in allowed for i in rec.get("issn") or [])
        return False

    def author_hit(self, rec):
        """True when an author matches the theme's authors or collaborations."""
        names = [normalize(a) for a in rec.get("authors") or []]
        return any(want in name for want in self.authors for name in names)

    def keyword_hit(self, text):
        """True when ``any`` (if set) and every ``all`` keyword match."""
        ok_any = not self.any_of or any(p.search(text) for p in self.any_of)
        return ok_any and all(p.search(text) for p in self.all_of)

    def passes(self, rec):
        """Stage-1 decision for one record.

        Parameters
        ----------
        rec : dict
            Paper record.

        Returns
        -------
        bool
            In scope, not excluded, and matching keywords or authors.
        """
        if not self.in_scope(rec):
            return False
        text = normalize(f"{rec.get('title', '')} {rec.get('abstract', '')}")
        if any(p.search(text) for p in self.exclude):
            return False
        return self.author_hit(rec) or self.keyword_hit(text)
