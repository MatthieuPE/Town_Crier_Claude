"""Theme definitions: loading, checking, database scopes."""

import re
from pathlib import Path

from . import files

DATABASES = ("arxiv", "biorxiv", "medrxiv", "openalex")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ARXIV_CAT_RE = re.compile(r"^[a-z][a-z\-]*(?:\.[A-Za-z\-]+)?$")
ISSN_RE = re.compile(r"^\d{4}-\d{3}[\dX]$")


def load_local(skills_dir):
    """Themes found next to the ``cry`` skill.

    Parameters
    ----------
    skills_dir : str or Path
        Folder holding the plugin's skill folders.

    Returns
    -------
    dict
        Theme name -> definition.
    """
    themes = {}
    for path in sorted(Path(skills_dir).glob("theme-*/theme.yaml")):
        theme = files.read_yaml(path)
        themes[theme.get("name") or path.parent.name.removeprefix("theme-")] = theme
    return themes


def merge(local, remote):
    """Themes from both sources; the installed (local) copy wins."""
    out = dict(remote or {})
    out.update(local or {})
    return out


def issns(theme):
    """ISSNs of the OpenAlex journals of a theme."""
    spec = (theme.get("databases") or {}).get("openalex") or {}
    if isinstance(spec, list):
        return [str(i) for i in spec]
    out = []
    for journal in spec.get("journals") or []:
        value = journal.get("issn") or []
        out.extend([value] if isinstance(value, str) else value)
    return [str(i) for i in out]


def scopes(theme):
    """Database scopes of a theme.

    Parameters
    ----------
    theme : dict
        Theme definition.

    Returns
    -------
    dict
        Database -> list of scopes (arXiv categories, preprint categories
        or ``all``, ISSNs). Only declared databases appear.
    """
    dbs = theme.get("databases") or {}
    out = {}
    if dbs.get("arxiv"):
        out["arxiv"] = [str(c).strip() for c in dbs["arxiv"]]
    for db in ("biorxiv", "medrxiv"):
        if dbs.get(db):
            out[db] = [str(c).strip().lower() for c in dbs[db]]
    if issns(theme):
        out["openalex"] = issns(theme)
    return out


def validate(theme, name=None):
    """Problems in a theme definition.

    Parameters
    ----------
    theme : dict
        Theme definition.
    name : str, optional
        Expected name (from the folder ``theme-<name>``).

    Returns
    -------
    list of str
        Errors; empty when valid.
    """
    errors = []
    tname = theme.get("name")
    if not tname or not NAME_RE.match(str(tname)):
        errors.append("name: lowercase words joined by hyphens, e.g. stellar-streams")
    if name and tname != name:
        errors.append(f"name: must be '{name}' to match its folder theme-{name}")
    for key in ("title", "description"):
        if not str(theme.get(key) or "").strip():
            errors.append(f"{key}: required")
    found = scopes(theme)
    if not found:
        errors.append(f"databases: declare at least one of {', '.join(DATABASES)}")
    for cat in found.get("arxiv", []):
        if not ARXIV_CAT_RE.match(cat):
            errors.append(f"databases.arxiv: '{cat}' is not an arXiv category")
    for issn in found.get("openalex", []):
        if not ISSN_RE.match(issn):
            errors.append(f"databases.openalex: '{issn}' is not an ISSN (NNNN-NNNN)")
    keywords = theme.get("keywords") or {}
    for key in ("any", "all", "exclude"):
        value = keywords.get(key) or []
        if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
            errors.append(f"keywords.{key}: list of non-empty strings")
    for key in ("authors", "examples"):
        value = theme.get(key) or []
        if not isinstance(value, list):
            errors.append(f"{key}: list")
    skills = theme.get("skills") or {}
    extract = skills.get("extract")
    if extract and not str(extract).startswith("extract-paper"):
        errors.append("skills.extract: must be extract-paper or extract-paper-<theme>")
    for cat, skill in (skills.get("summarize") or {}).items():
        if skill and not str(skill).startswith(f"summarize-category-{cat}"):
            errors.append(f"skills.summarize.{cat}: must start with summarize-category-{cat}")
    return errors


def default_skill(theme, step, category):
    """Theme's own skill for a step, or None.

    Parameters
    ----------
    theme : dict
        Theme definition.
    step : {"extract", "summarize"}
        Pipeline step.
    category : int
        Summary category.

    Returns
    -------
    str or None
        Skill name.
    """
    skills = (theme or {}).get("skills") or {}
    if step == "extract":
        return skills.get("extract")
    by_cat = skills.get("summarize") or {}
    return by_cat.get(category) or by_cat.get(str(category))
