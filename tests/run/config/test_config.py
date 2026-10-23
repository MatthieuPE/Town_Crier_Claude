"""Tests of configuration merging, resolution and validation."""

import pytest

from towncrier import config, themes


@pytest.fixture
def plugin_themes():
    """Themes installed with the plugin."""
    return themes.load_local(config.SKILLS_DIR)


@pytest.mark.run
@pytest.mark.config
@pytest.mark.unit
def test_default_has_placeholders(plugin_themes, run_date):
    """The default configuration cannot run until its placeholders are filled."""
    cfg = config.load()
    resolved = config.resolve(cfg, plugin_themes, run_date)
    errors, _ = config.validate(cfg, resolved, plugin_themes)
    assert any("placeholder" in e for e in errors)


@pytest.mark.run
@pytest.mark.config
@pytest.mark.unit
def test_user_config_resolves(user_config, plugin_themes, run_date):
    """Sections are numbered; defaults and theme skills are filled in."""
    cfg = config.load(user_config)
    resolved = config.resolve(cfg, plugin_themes, run_date)
    errors, warnings = config.validate(cfg, resolved, plugin_themes)
    assert errors == []
    subs = {s["id"]: s for s in config.iter_subsections(resolved)}
    assert list(subs) == ["1.1", "1.2", "2.1", "2.2", "3.1"]
    assert subs["1.1"]["n_papers"] == 3 and subs["1.1"]["list_others"] is True
    assert subs["1.1"]["full_text"] == {"source": "alphaxiv", "sections": ["abstract", "methods", "results", "conclusions"]}
    assert subs["2.1"]["skills"] == {"extract": "extract-paper-cosmology", "summarize": "summarize-category-2-cosmology"}
    assert subs["1.2"]["skills"]["summarize"] == "summarize-category-2"
    assert resolved["period"]["start"] == "2026-10-12" and resolved["period"]["end"] == "2026-10-18"


@pytest.mark.run
@pytest.mark.config
@pytest.mark.unit
def test_wrong_category_skill_is_rejected(tmp_path, plugin_themes, run_date):
    """A category-2 theme skill cannot serve a category-1 subsection."""
    path = tmp_path / "bad.yaml"
    path.write_text("sections:\n  - title: X\n    subsections:\n"
                    "      - {theme: cosmology, category: 1, skills: {summarize: summarize-category-2-cosmology}}\n"
                    "      - {theme: nowhere, category: 2}\n")
    cfg = config.load(path)
    resolved = config.resolve(cfg, plugin_themes, run_date)
    errors, _ = config.validate(cfg, resolved, plugin_themes)
    assert any("summarize-category-1" in e for e in errors)
    assert any("unknown theme 'nowhere'" in e for e in errors)


@pytest.mark.run
@pytest.mark.config
@pytest.mark.unit
def test_plugin_themes_are_valid(plugin_themes):
    """Every theme shipped with the plugin passes validation."""
    for name, theme in plugin_themes.items():
        assert themes.validate(theme, name) == [], name
