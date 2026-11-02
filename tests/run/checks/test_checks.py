"""Tests of the accuracy and format checks."""

import pytest

from towncrier import checks, labels


@pytest.mark.run
@pytest.mark.checks
@pytest.mark.unit
@pytest.mark.parametrize("number, source, found", [
    ("71.2", "H0 = 71.2 +- 1.5", True),
    ("1.2", "H0 = 71.2", False),          # no partial match
    ("13", "135 binaries", False),
    ("10000", "10,000 stars", True),      # thousands separator
    ("0.3", "0,3 %", True),               # decimal comma
])
def test_number_in(number, source, found):
    """Numbers match whole, with separators normalized."""
    assert checks.number_in(number, checks.normalize_numbers(source)) is found


@pytest.mark.run
@pytest.mark.checks
@pytest.mark.unit
def test_numbers_in_skips_single_digits():
    """Single digits are not checked; decimals and longer integers are."""
    assert checks.numbers_in("3 papers, 12.5 kpc, 340 members, 7 days") == ["12.5", "340"]


@pytest.mark.run
@pytest.mark.checks
@pytest.mark.unit
def test_sentence_count_ignores_abbreviations():
    """et al., e.g. and decimals do not end sentences."""
    text = "Smith et al. find 1.5 times more. This is new, e.g. in halos. Third one!"
    assert checks.count_sentences(text) == 3


@pytest.mark.run
@pytest.mark.checks
@pytest.mark.unit
def test_category_1_bullets():
    """All five bullets, in order, none empty."""
    lab = labels.LABELS["en"]
    good = "\n".join(f"- **{b}:** text" for b in lab["bullets"])
    assert checks.check_category_1(good, lab) == []
    bad = good.replace("- **Aims:** text", "- **Aims:**")
    assert any("empty bullet 'Aims'" in e for e in checks.check_category_1(bad, lab))
    swapped = good.replace("Context", "TMP").replace("Results", "Context").replace("TMP", "Results")
    assert "bullets out of order" in checks.check_category_1(swapped, lab)


@pytest.mark.run
@pytest.mark.checks
@pytest.mark.unit
def test_citation_pattern():
    """Author-year and numeric citations are caught."""
    assert checks.CITATION.search("as shown by Smith et al. 2020")
    assert checks.CITATION.search("as shown by Smith and Jones (2019)")
    assert checks.CITATION.search("as shown before [12]")
    assert not checks.CITATION.search("Gaia DR3 data of 2025 stars")
