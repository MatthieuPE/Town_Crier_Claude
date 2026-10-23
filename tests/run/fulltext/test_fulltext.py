"""Tests of the full-text section cut."""

import pytest

from towncrier import fulltext


@pytest.mark.run
@pytest.mark.fulltext
@pytest.mark.unit
def test_headings_skip_running_heads(paper_text):
    """Running page heads are not headings; subsections inherit their parent."""
    names = [(n, h) for _, n, h in fulltext.find_headings(paper_text.splitlines())]
    assert ("methods", "2. DATA AND METHODS") in names
    assert ("methods", "2.1. Membership") in names
    assert not any("SMITH" in h for _, h in names)
    assert [n for n, _ in names][-2:] == ["back", "back"]


@pytest.mark.run
@pytest.mark.fulltext
@pytest.mark.unit
def test_cut_keeps_sections_and_numbers(paper_text):
    """Selected sections are kept, others dropped, numbers preserved."""
    out, stats = fulltext.cut(paper_text, ["abstract", "methods", "results", "conclusions"])
    assert "introduction is long" not in out and "referee" not in out and "caveats" not in out
    assert "∼10^4 candidates" in out          # superscript rebuilt, not lost
    assert "More results on the stream" in out  # running head did not end Results
    assert "constrains the progenitor" in out   # hyphenation joined
    assert "\nf\n" not in out and " pre " not in out
    assert stats["missing"] == [] and stats["chars_out"] < stats["chars_in"]


@pytest.mark.run
@pytest.mark.fulltext
@pytest.mark.unit
def test_cut_file_reads_tool_results(tool_result_file, tmp_path):
    """Saved MCP results are unwrapped; abstract falls back to the database one."""
    dst = tmp_path / "out.txt"
    stats = fulltext.cut_file(tool_result_file, dst, ["abstract", "results"])
    assert "12.5 kpc" in dst.read_text()
    out, _ = fulltext.cut("1. INTRODUCTION\nText here.\n3. RESULTS\nFound it.\n", ["abstract", "results"],
                          abstract="Database abstract.")
    assert out.startswith("[[abstract: from the database]]")
    assert stats["kept"] == ["abstract", "results"]
