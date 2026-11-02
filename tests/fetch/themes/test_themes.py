"""Tests of theme loading and fetch planning."""

import pytest

from town_crier_fetch import themes

GLOB = "plugins/town-crier/skills/tcc-theme-*/theme.yaml"


@pytest.mark.fetch
@pytest.mark.themes
@pytest.mark.unit
def test_plan_merges_themes(plugin_repo):
    """Scopes are merged over themes, per database."""
    defs, errors = themes.load_themes(themes.find_theme_files(plugin_repo, GLOB))
    assert not errors
    assert sorted(defs) == ["cosmo", "science", "streams"]
    plan = themes.build_plan(defs)
    assert plan == {"arxiv": ["astro-ph.CO", "astro-ph.GA"], "openalex": ["0028-0836", "1476-4687"]}


@pytest.mark.fetch
@pytest.mark.themes
@pytest.mark.unit
def test_name_must_match_folder(tmp_path, theme_yaml):
    """A theme whose name differs from its folder is rejected."""
    folder = tmp_path / "tcc-theme-right"
    folder.mkdir()
    (folder / "theme.yaml").write_text(theme_yaml("wrong", arxiv=["astro-ph.GA"]))
    defs, errors = themes.load_themes([folder / "theme.yaml"])
    assert not defs
    assert "name must be 'right'" in errors[0]


@pytest.mark.fetch
@pytest.mark.themes
@pytest.mark.unit
def test_biorxiv_all_collapses():
    """``all`` replaces specific preprint categories."""
    defs = {"a": {"databases": {"biorxiv": ["Neuroscience"]}},
            "b": {"databases": {"biorxiv": ["all"]}}}
    assert themes.build_plan(defs) == {"biorxiv": ["all"]}


@pytest.mark.fetch
@pytest.mark.themes
@pytest.mark.unit
def test_configuration_themes_are_fetched(repo_root):
    """Themes written in configs/*.yaml add their databases to the fetch plan."""
    defs, errors = themes.load_config_themes(themes.find_theme_files(repo_root, "configs/*.yaml"))
    assert not errors
    assert "astro-ph.IM" in themes.build_plan(defs)["arxiv"]
