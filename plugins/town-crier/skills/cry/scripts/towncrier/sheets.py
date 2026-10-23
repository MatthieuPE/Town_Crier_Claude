"""Review sheets: compact candidate lists that Claude reads to judge papers."""

import re

from . import vocab

FLAG_PATTERNS = {
    "review?": re.compile(r"\breview\b", re.I),
    "proceedings?": re.compile(r"proceedings|conference|workshop|symposium", re.I),
    "erratum?": re.compile(r"\berrat|corrigend|correction to\b", re.I),
}


def flags(rec):
    """Hints about the kind of paper, from its title and comment."""
    text = f"{rec.get('title', '')} {rec.get('comment') or ''}"
    return [name for name, pat in FLAG_PATTERNS.items() if pat.search(text)]


def first_author(rec, et_al="et al."):
    """First author, with ``et al.`` when there are more."""
    authors = rec.get("authors") or []
    if not authors:
        return "unknown author"
    return authors[0] if len(authors) == 1 else f"{authors[0]} {et_al}"


def where(rec):
    """Categories or journal of a record."""
    if rec.get("source") == "openalex":
        return rec.get("journal") or "journal unknown"
    return ", ".join(rec.get("categories") or []) or rec.get("source", "")


def render(sub, recs, *, titles_only=False):
    """Markdown sheet of a subsection's candidates.

    Parameters
    ----------
    sub : dict
        Resolved subsection.
    recs : list of dict
        Candidate records.
    titles_only : bool
        One line per paper, no abstracts.

    Returns
    -------
    str
        Sheet text.
    """
    head = [f"# Subsection {sub['id']}: {sub['title']} (theme {sub['theme']}, category {sub['category']}, "
            f"rank by {sub['rank_by']})", f"{len(recs)} candidates."]
    if sub["category"] == 3:
        head.append("Field tags: " + " | ".join(vocab.FIELDS))
    lines = head + [""]
    for rec in recs:
        hint = ", ".join(flags(rec)) or "-"
        meta = f"{rec.get('first_seen', '')} · {where(rec)} · {first_author(rec)} · flags: {hint}"
        if titles_only:
            lines.append(f"- {rec['paper_id']} | {rec['title']} | {meta}")
            continue
        lines += [f"## {rec['paper_id']}", meta, f"**{rec['title']}**",
                  rec.get("abstract") or "(no abstract)", ""]
    return "\n".join(lines).rstrip() + "\n"
