"""Theme definitions: which databases and scopes to fetch."""

import logging
from pathlib import Path

import yaml

LOG = logging.getLogger(__name__)

DATABASES = ("arxiv", "biorxiv", "medrxiv", "openalex")


def find_theme_files(repo_root, pattern):
    """Theme definition files in the repository.

    Parameters
    ----------
    repo_root : str or Path
        Repository root.
    pattern : str
        Glob relative to the root, e.g.
        ``plugins/town-crier/skills/theme-*/theme.yaml``.

    Returns
    -------
    list of Path
        Sorted file paths.
    """
    return sorted(Path(repo_root).glob(pattern))


def load_theme(path):
    """Read and check one theme definition.

    Parameters
    ----------
    path : str or Path
        ``theme.yaml`` inside a ``theme-<name>`` folder.

    Returns
    -------
    dict
        Theme definition.

    Raises
    ------
    ValueError
        Name does not match the folder, or no database is declared.
    """
    path = Path(path)
    theme = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    slug = path.parent.name.removeprefix("theme-")
    if theme.get("name") != slug:
        raise ValueError(f"{path}: name must be '{slug}' (folder theme-{slug})")
    dbs = theme.get("databases") or {}
    if not any(dbs.get(db) for db in DATABASES):
        raise ValueError(f"{path}: declare at least one database ({', '.join(DATABASES)})")
    return theme


def load_themes(paths):
    """Load all valid themes; log and skip invalid ones.

    Parameters
    ----------
    paths : iterable of Path
        Theme files.

    Returns
    -------
    themes : dict
        Theme name -> definition.
    errors : list of str
        Problems found.
    """
    themes, errors = {}, []
    for path in paths:
        try:
            theme = load_theme(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
            LOG.error("%s", exc)
            continue
        themes[theme["name"]] = theme
    return themes, errors


def journal_issns(openalex_spec):
    """Flat list of ISSNs from an OpenAlex database entry.

    Parameters
    ----------
    openalex_spec : dict or list
        ``{"journals": [{"name": ..., "issn": [...]}, ...]}`` or a list of ISSNs.

    Returns
    -------
    list of str
        ISSNs.
    """
    if isinstance(openalex_spec, list):
        return [str(i) for i in openalex_spec]
    issns = []
    for journal in (openalex_spec or {}).get("journals") or []:
        value = journal.get("issn") or []
        issns.extend([value] if isinstance(value, str) else value)
    return [str(i) for i in issns]


def build_plan(themes):
    """Scopes to fetch for each database, merged over all themes.

    Parameters
    ----------
    themes : dict
        Theme name -> definition.

    Returns
    -------
    dict
        Database -> sorted list of scopes. arXiv scopes are categories,
        bioRxiv/medRxiv scopes are subject categories (``all`` for every
        category), OpenAlex scopes are ISSNs. Databases with no scope are
        left out.
    """
    plan = {db: set() for db in DATABASES}
    for theme in themes.values():
        dbs = theme.get("databases") or {}
        for db in ("arxiv", "biorxiv", "medrxiv"):
            plan[db].update(str(s).strip().lower() if db != "arxiv" else str(s).strip()
                            for s in dbs.get(db) or [])
        plan["openalex"].update(journal_issns(dbs.get("openalex")))
    for db in ("biorxiv", "medrxiv"):
        if "all" in plan[db]:
            plan[db] = {"all"}  # one query covers everything
    return {db: sorted(scopes) for db, scopes in plan.items() if scopes}
