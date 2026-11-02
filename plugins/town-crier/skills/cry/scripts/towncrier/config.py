"""Configuration: merge with defaults, resolve, validate."""

import copy
import datetime as dt
import re
from pathlib import Path

from . import files, labels, period as periods, themes as themes_mod, vocab

CRY_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = CRY_DIR / "config" / "default.yaml"
SKILLS_DIR = CRY_DIR.parent
PLACEHOLDER = re.compile(r"<[^<>]+>")


def deep_merge(base, override):
    """Mapping ``override`` merged into ``base``; lists are replaced.

    Parameters
    ----------
    base, override : dict
        Mappings.

    Returns
    -------
    dict
        New merged mapping.
    """
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load(src=None, default_path=DEFAULT_CONFIG):
    """User configuration merged over the default one.

    Parameters
    ----------
    src : str, optional
        File path or URL of the user configuration.
    default_path : str or Path
        Default configuration.

    Returns
    -------
    dict
        Merged configuration. A user ``sections`` list replaces the default.
    """
    base = files.read_yaml(default_path)
    user = files.read_yaml(src) if src else {}
    return deep_merge(base, user)


def find_placeholders(obj, path="config"):
    """Locations of ``<...>`` placeholders.

    Parameters
    ----------
    obj : object
        Configuration or part of it.
    path : str
        Location prefix.

    Returns
    -------
    list of str
        ``location: value`` entries.
    """
    if isinstance(obj, dict):
        return [p for k, v in obj.items() for p in find_placeholders(v, f"{path}.{k}")]
    if isinstance(obj, list):
        return [p for i, v in enumerate(obj) for p in find_placeholders(v, f"{path}[{i}]")]
    if isinstance(obj, str) and PLACEHOLDER.search(obj):
        return [f"{path}: {obj}"]
    return []


def resolve_subsection(sid, sub, cfg, theme):
    """All settings of one subsection.

    Parameters
    ----------
    sid : str
        Subsection id, e.g. ``1.2``.
    sub : dict
        Subsection as written in the configuration.
    cfg : dict
        Merged configuration.
    theme : dict or None
        Theme definition.

    Returns
    -------
    dict
        Resolved subsection.
    """
    cat = sub.get("category")
    out = {"id": sid, "theme": sub.get("theme"), "category": cat,
           "title": sub.get("title") or (theme or {}).get("title") or sub.get("theme")}
    defaults = (cfg.get("defaults") or {}).get(f"category_{cat}") or {}
    for key, value in defaults.items():
        out[key] = sub.get(key, value)
    for key in ("n_papers", "rank_by", "count"):
        out.setdefault(key, sub.get(key))
    if cat == 1:
        out["full_text"] = deep_merge(cfg.get("full_text") or {}, sub.get("full_text") or {})
    skills = sub.get("skills") or {}
    out["skills"] = {
        "extract": skills.get("extract") or themes_mod.default_skill(theme, "extract", cat) or "extract-paper",
        "summarize": (skills.get("summarize") or themes_mod.default_skill(theme, "summarize", cat)
                      or f"summarize-category-{cat}"),
    }
    return out


def resolve(cfg, themes, run_date, anchor=None):
    """Resolved configuration of one run.

    Parameters
    ----------
    cfg : dict
        Merged configuration.
    themes : dict
        Theme name -> definition.
    run_date : datetime.date
        Day of the run.
    anchor : str, optional
        Overrides ``period.anchor`` (``calendar`` for scheduled runs).

    Returns
    -------
    dict
        Resolved configuration, ready to write as ``config.resolved.yaml``.
    """
    pcfg = cfg.get("period") or {}
    per = periods.compute_period(run_date, length=pcfg.get("length", 1), unit=pcfg.get("unit", "week"),
                                 end=pcfg.get("end", "yesterday"),
                                 anchor=anchor or pcfg.get("anchor", "rolling"))
    sections, used = [], {}
    for i, sec in enumerate(cfg.get("sections") or [], 1):
        subs = []
        for j, sub in enumerate(sec.get("subsections") or [], 1):
            theme = themes.get(sub.get("theme"))
            if theme:
                used[sub["theme"]] = theme
            subs.append(resolve_subsection(f"{i}.{j}", sub, cfg, theme))
        sections.append({"id": str(i), "title": sec.get("title"), "subsections": subs})
    return {
        "version": 1,
        "run": {"date": run_date.isoformat(), "anchor": per.anchor,
                "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")},
        "period": per.as_dict(),
        "data": cfg.get("data") or {},
        "output": cfg.get("output") or {},
        "selection": cfg.get("selection") or {},
        "schedule": cfg.get("schedule") or {},
        "sections": sections,
        "themes": used,
    }


def iter_subsections(resolved):
    """Subsections in reading order."""
    for sec in resolved["sections"]:
        yield from sec["subsections"]


def _check_subsection(sub, themes):
    """Errors and warnings of one resolved subsection."""
    errors, warnings = [], []
    where = f"subsection {sub['id']} ({sub.get('theme')})"
    cat = sub.get("category")
    if cat not in (1, 2, 3):
        errors.append(f"{where}: category must be 1, 2 or 3")
        return errors, warnings
    if sub.get("theme") not in themes:
        errors.append(f"{where}: unknown theme '{sub.get('theme')}'. Define it with the define-theme skill.")
    if not isinstance(sub.get("n_papers"), int) or sub["n_papers"] < 1:
        errors.append(f"{where}: n_papers must be an integer >= 1")
    if sub.get("rank_by") not in vocab.RANK_BY:
        errors.append(f"{where}: rank_by must be relevance or impact")
    if cat == 1:
        ft = sub.get("full_text") or {}
        if ft.get("source") not in vocab.FULL_TEXT_SOURCES:
            errors.append(f"{where}: full_text.source must be one of {vocab.FULL_TEXT_SOURCES}")
        if ft.get("source") == "html":
            warnings.append(f"{where}: full_text.source 'html' is not available yet; alphaxiv is used")
            ft["source"] = "alphaxiv"
        bad = [s for s in ft.get("sections") or [] if s not in vocab.SECTIONS]
        if bad or not ft.get("sections"):
            errors.append(f"{where}: full_text.sections must be among {vocab.SECTIONS}")
    if cat == 3:
        bad = [f for f in sub.get("exclude_fields") or [] if not vocab.match_field(f)]
        if bad:
            errors.append(f"{where}: unknown exclude_fields {bad}; use {list(vocab.FIELDS)}")
    if not sub["skills"]["extract"].startswith("extract-paper"):
        errors.append(f"{where}: skills.extract must be extract-paper or extract-paper-<theme>")
    base = f"summarize-category-{cat}"
    if not (sub["skills"]["summarize"] == base or sub["skills"]["summarize"].startswith(base + "-")):
        errors.append(f"{where}: skills.summarize must be {base} or {base}-<theme>")
    return errors, warnings


def validate(cfg, resolved, themes):
    """Errors (blocking) and warnings of a configuration.

    Parameters
    ----------
    cfg : dict
        Merged configuration.
    resolved : dict
        Resolved configuration.
    themes : dict
        Known themes.

    Returns
    -------
    errors, warnings : list of str
        Problems found.
    """
    errors, warnings = [], []
    holes = find_placeholders({"sections": cfg.get("sections"), "data": cfg.get("data")})
    errors.extend(f"placeholder to fill: {h}" for h in holes)
    if not resolved["sections"]:
        errors.append("sections: at least one section is required")
    seen_themes = set()
    for sub in iter_subsections(resolved):
        errs, warns = _check_subsection(sub, themes)
        errors.extend(errs)
        warnings.extend(warns)
        seen_themes.add(sub.get("theme"))
    for name in sorted(t for t in seen_themes if t in themes):
        errors.extend(f"theme {name}: {e}" for e in themes_mod.validate(themes[name], name))
    if not (resolved["data"].get("repository") or resolved["data"].get("local_dir")):
        errors.append("data.repository: required (owner/name of the GitHub repository)")
    _, lang_warning = labels.for_language(resolved["output"].get("language", "English"))
    if lang_warning:
        warnings.append(lang_warning)
    return errors, warnings
