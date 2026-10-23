"""Tests of candidate collection and stage-1 pools."""

import datetime as dt

import pytest

from towncrier import candidates, config, data, themes


@pytest.fixture
def resolved(user_config, data_dir, run_date):
    """Resolved test configuration."""
    cfg = config.load(user_config)
    cfg["data"]["local_dir"] = str(data_dir)
    return config.resolve(cfg, themes.load_local(config.SKILLS_DIR), run_date)


@pytest.mark.run
@pytest.mark.candidates
@pytest.mark.unit
def test_pools_follow_themes(resolved, data_dir):
    """Each subsection pools the period's papers that pass its theme filter."""
    source = data.DataSource(local_dir=data_dir)
    index = source.index()
    days = candidates.period_days(resolved)
    records, notes = candidates.collect(source, index, candidates.needed_databases(resolved), days)
    assert "arXiv:2610.09999" not in records  # before the period
    pools, cands = candidates.build_pools(resolved, records)
    assert pools["1.1"] == ["arXiv:2610.10003", "arXiv:2610.10002", "arXiv:2610.10001"]
    assert pools["1.2"] == ["arXiv:2610.10004"]
    assert sorted(pools["2.1"]) == ["arXiv:2610.10005", "arXiv:2610.10006"]
    assert pools["2.2"] == ["arXiv:2610.10007"]
    assert sorted(pools["3.1"]) == ["doi:10.1038/test.1", "doi:10.1038/test.2"]
    assert cands["arXiv:2610.10003"]["found_for"] == ["1.1"]
    assert notes == []


@pytest.mark.run
@pytest.mark.candidates
@pytest.mark.unit
def test_missing_run_days_are_noted(resolved, data_dir):
    """Days without a daily fetch are reported."""
    source = data.DataSource(local_dir=data_dir)
    index = source.index()
    index["databases"]["arxiv"]["run_days"].remove("2026-10-15")
    _, notes = candidates.collect(source, index, ["arxiv"], candidates.period_days(resolved))
    assert any("2026-10-15" in n for n in notes)
    late = candidates.coverage_notes(index | {"databases": {"arxiv": {"coverage": {"astro-ph.GA": "2026-10-14"}}}},
                                     resolved, dt.date(2026, 10, 12))
    assert any("covered only since 2026-10-14" in n for n in late)
