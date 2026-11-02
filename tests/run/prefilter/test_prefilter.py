"""Tests of the stage-1 keyword filter."""

import pytest

from towncrier import config, themes
from towncrier.prefilter import ThemeFilter, compile_keyword, normalize


@pytest.mark.run
@pytest.mark.prefilter
@pytest.mark.unit
@pytest.mark.parametrize("keyword, text, hit", [
    ("stream*", "Stellar streams in the halo", True),
    ("stream", "Stellar streams in the halo", False),       # whole word only
    ("GD-1", "gaps in GD 1", True),
    ("GD-1", "the GD-10 cluster", False),
    ("Milky Way", "the milky-way disc", True),
    ("high-redshift galax*", "High redshift galaxies", True),
    ("CGM", "the $\\rm CGM$ of galaxies", True),
])
def test_keyword_matching(keyword, text, hit):
    """Whole words, case-insensitive, separators and markup ignored."""
    assert bool(compile_keyword(keyword).search(normalize(text))) is hit


@pytest.fixture
def theme():
    """Theme with any, exclude and authors."""
    return {"databases": {"arxiv": ["astro-ph.GA"]},
            "keywords": {"any": ["stellar stream*"], "exclude": ["cold stream*"]},
            "authors": ["Bonaca"]}


def rec(title, cats=("astro-ph.GA",), authors=("A. Person",)):
    """Minimal arXiv record."""
    return {"source": "arxiv", "title": title, "abstract": "", "categories": list(cats), "authors": list(authors)}


@pytest.mark.run
@pytest.mark.prefilter
@pytest.mark.unit
def test_theme_filter(theme):
    """Scope, keywords, exclusions and authors combine as documented."""
    f = ThemeFilter.from_theme(theme)
    assert f.passes(rec("Stellar streams as probes"))
    assert not f.passes(rec("Stellar streams as probes", cats=("astro-ph.CO",)))  # out of scope
    assert not f.passes(rec("Stellar streams and cold streams"))                    # excluded
    assert f.passes(rec("Dynamics of the halo", authors=("Ana Bonaca",)))           # author
    assert not f.passes(rec("Dynamics of the halo"))


def journal(title, abstract="We report a new result."):
    """Minimal OpenAlex record from Science."""
    return {"source": "openalex", "title": title, "abstract": abstract, "issn": ["0036-8075"], "authors": []}


@pytest.mark.run
@pytest.mark.prefilter
@pytest.mark.unit
def test_exclude_titles_whole_or_prefix():
    """Whole titles are dropped; a trailing * drops titles that start so; abstracts are not searched."""
    f = ThemeFilter.from_theme({"databases": {"openalex": ["0036-8075"]},
                                "keywords": {"exclude_titles": ["In Science Journals", "Profile of*"]}})
    assert not f.passes(journal("In Science Journals"))
    assert not f.passes(journal("in science journals"))
    assert not f.passes(journal("Profile of Jane Doe"))
    assert f.passes(journal("Publication bias in science journals"))              # not the whole title
    assert f.passes(journal("A new result", abstract="Gender gaps in science journals."))


@pytest.mark.run
@pytest.mark.prefilter
@pytest.mark.unit
def test_science_at_large_drops_digest_pages():
    """The shipped theme removes Science's weekly digest pages and keeps research."""
    theme = themes.load_local(config.SKILLS_DIR)["science-at-large"]
    f = ThemeFilter.from_theme(theme)
    assert not f.passes(journal("In Science Journals"))
    assert not f.passes(journal("In Other Journals"))
    assert f.passes(journal("A room-temperature superconductor"))
